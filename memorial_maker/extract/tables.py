"""Extração de tabelas com múltiplas estratégias."""

import cv2
import numpy as np
import pytesseract
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger
from memorial_maker.utils.cv_utils import detect_tables, enhance_for_ocr

logger = get_logger("extract.tables")


class TableExtractor:
    """Extrator de tabelas com fallback OCR."""

    def __init__(self):
        """Inicializa extrator."""
        self.tesseract_config = f"--psm 6 -l {settings.tesseract_lang}"

    def extract_tables_from_image(
        self,
        image: np.ndarray,
        page_num: int = 0,
    ) -> List[Dict[str, Any]]:
        """Extrai tabelas de uma imagem usando OpenCV."""
        logger.debug(f"Detectando tabelas na página {page_num}")
        
        # Detecta bounding boxes de tabelas
        table_boxes = detect_tables(image)
        
        tables = []
        for idx, (x, y, w, h) in enumerate(table_boxes):
            # Extrai ROI da tabela
            table_roi = image[y:y+h, x:x+w]
            
            # Tenta extrair células
            table_data = self._extract_table_cells(table_roi)
            
            tables.append({
                "table_id": f"p{page_num}_t{idx}",
                "bbox": (x, y, w, h),
                "num_rows": table_data["num_rows"],
                "num_cols": table_data["num_cols"],
                "cells": table_data["cells"],
                "type": self._classify_table(table_data["cells"]),
            })
        
        logger.debug(f"Encontradas {len(tables)} tabelas na página {page_num}")
        return tables

    def _extract_table_cells(self, table_image: np.ndarray) -> Dict[str, Any]:
        """Extrai células de uma tabela."""
        
        # Preprocessa
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY) if len(table_image.shape) == 3 else table_image
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Detecta linhas horizontais e verticais
        h_lines = self._detect_lines(thresh, horizontal=True)
        v_lines = self._detect_lines(thresh, horizontal=False)
        
        # Encontra interseções (células)
        cells = self._find_cells(h_lines, v_lines, table_image)
        
        # Organiza em grid
        if cells:
            rows, cols = self._organize_cells_in_grid(cells)
        else:
            rows, cols = 0, 0
        
        return {
            "num_rows": rows,
            "num_cols": cols,
            "cells": cells,
        }

    def _detect_lines(
        self,
        thresh: np.ndarray,
        horizontal: bool = True,
    ) -> List[Tuple[int, int, int, int]]:
        """Detecta linhas horizontais ou verticais."""
        
        kernel_size = (40, 1) if horizontal else (1, 40)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        
        lines_img = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Detecta contornos
        contours, _ = cv2.findContours(lines_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        lines = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            lines.append((x, y, w, h))
        
        return sorted(lines, key=lambda l: l[1] if horizontal else l[0])

    def _find_cells(
        self,
        h_lines: List[Tuple[int, int, int, int]],
        v_lines: List[Tuple[int, int, int, int]],
        image: np.ndarray,
    ) -> List[Dict[str, Any]]:
        """Encontra células pela interseção de linhas."""
        
        cells = []
        
        # Se não temos linhas suficientes, tenta OCR direto
        if len(h_lines) < 2 or len(v_lines) < 2:
            # Fallback: OCR da imagem inteira
            text = self._ocr_region(image, (0, 0, image.shape[1], image.shape[0]))
            return [{"row": 0, "col": 0, "text": text, "bbox": (0, 0, image.shape[1], image.shape[0])}]
        
        # Cria grid de células
        for row_idx in range(len(h_lines) - 1):
            y1 = h_lines[row_idx][1]
            y2 = h_lines[row_idx + 1][1]
            
            for col_idx in range(len(v_lines) - 1):
                x1 = v_lines[col_idx][0]
                x2 = v_lines[col_idx + 1][0]
                
                # Extrai ROI da célula
                cell_roi = image[y1:y2, x1:x2]
                
                # OCR
                text = self._ocr_region(image, (x1, y1, x2 - x1, y2 - y1))
                
                cells.append({
                    "row": row_idx,
                    "col": col_idx,
                    "text": text,
                    "bbox": (x1, y1, x2 - x1, y2 - y1),
                })
        
        return cells

    def _ocr_region(
        self,
        image: np.ndarray,
        bbox: Tuple[int, int, int, int],
    ) -> str:
        """Executa OCR em uma região específica."""
        x, y, w, h = bbox
        
        # Extrai e processa ROI
        roi = image[y:y+h, x:x+w]
        
        if roi.size == 0:
            return ""
        
        try:
            processed = enhance_for_ocr(roi)
            text = pytesseract.image_to_string(processed, config=self.tesseract_config)
            return text.strip()
        except Exception as e:
            logger.debug(f"Erro ao fazer OCR de célula: {e}")
            return ""

    def _organize_cells_in_grid(self, cells: List[Dict]) -> Tuple[int, int]:
        """Determina dimensões do grid."""
        if not cells:
            return 0, 0
        
        rows = max(c["row"] for c in cells) + 1
        cols = max(c["col"] for c in cells) + 1
        
        return rows, cols

    def _classify_table(self, cells: List[Dict]) -> str:
        """Classifica tipo de tabela por conteúdo."""
        if not cells:
            return "unknown"
        
        # Junta todo o texto
        all_text = " ".join(c["text"].lower() for c in cells)
        
        # Keywords
        if "legenda" in all_text or "simbologia" in all_text or "símbolo" in all_text:
            return "legenda"
        elif "quantidade" in all_text or "total" in all_text or "pavimento" in all_text:
            return "sumario"
        elif "norma" in all_text or "nbr" in all_text:
            return "normas"
        
        return "generic"

    def extract_with_tabula(self, pdf_path: Path, page_num: int) -> List[Dict]:
        """Tenta extrair tabelas usando Tabula (fallback opcional).
        
        Requer Java instalado.
        """
        try:
            import tabula
            
            logger.debug(f"Tentando Tabula para página {page_num} de {pdf_path.name}")
            
            dfs = tabula.read_pdf(
                str(pdf_path),
                pages=page_num + 1,
                multiple_tables=True,
                lattice=True,
            )
            
            tables = []
            for idx, df in enumerate(dfs):
                cells = []
                for row_idx, row in df.iterrows():
                    for col_idx, value in enumerate(row):
                        cells.append({
                            "row": row_idx,
                            "col": col_idx,
                            "text": str(value),
                        })
                
                tables.append({
                    "table_id": f"p{page_num}_tabula_{idx}",
                    "num_rows": len(df),
                    "num_cols": len(df.columns),
                    "cells": cells,
                    "type": self._classify_table(cells),
                })
            
            return tables
            
        except ImportError:
            logger.debug("Tabula não disponível (Java não instalado)")
            return []
        except Exception as e:
            logger.debug(f"Erro com Tabula: {e}")
            return []


def extract_legenda_table(page_data: Dict) -> Optional[List[Dict]]:
    """Extrai especificamente tabela de legenda/simbologia."""
    
    # Verifica se página é do tipo legenda
    if page_data.get("type") != "legenda":
        return None
    
    # Busca tabelas classificadas como legenda
    tables = []
    
    # Nas extrações Docling
    for table in page_data.get("tables", []):
        if table.get("type") == "legenda":
            tables.append(table)
    
    return tables if tables else None


def extract_sumario_table(page_data: Dict) -> Optional[List[Dict]]:
    """Extrai especificamente tabela de sumário/quantidades."""
    
    # Busca tabelas classificadas como sumário
    tables = []
    
    for table in page_data.get("tables", []):
        if table.get("type") == "sumario":
            tables.append(table)
    
    return tables if tables else None






