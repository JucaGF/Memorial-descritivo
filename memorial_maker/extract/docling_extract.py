"""Extração primária usando Docling (ou PyMuPDF se não disponível)."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger

logger = get_logger("extract.docling")

# Tenta importar Docling, mas é opcional
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
    logger.info("Docling disponível")
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling não disponível - usando apenas PyMuPDF")


class DoclingExtractor:
    """Extrator usando Docling (ou fallback direto)."""

    def __init__(self):
        """Inicializa o conversor Docling se disponível."""
        if DOCLING_AVAILABLE:
            # Configura pipeline com OCR se necessário
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = settings.docling_ocr
            
            self.converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        else:
            self.converter = None
            logger.info("Usando PyMuPDF como extrator primário")

    def extract_pdf(self, pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Extrai dados de um PDF usando Docling ou PyMuPDF.
        
        Args:
            pdf_path: Caminho do PDF
            output_dir: Diretório para salvar JSONs por página
            
        Returns:
            Dict com dados estruturados do documento
        """
        # Se Docling não está disponível, usa fallback direto
        if not DOCLING_AVAILABLE or self.converter is None:
            logger.info(f"Extraindo com PyMuPDF (fallback): {pdf_path.name}")
            from memorial_maker.extract.pdf_fallback import PDFFallbackExtractor
            fallback = PDFFallbackExtractor()
            return fallback.extract_pdf(pdf_path, output_dir)
        
        logger.info(f"Extraindo com Docling: {pdf_path.name}")
        
        try:
            # Converte documento
            result = self.converter.convert(str(pdf_path))
            doc = result.document
            
            # Estrutura de dados
            extraction = {
                "source": pdf_path.name,
                "num_pages": len(doc.pages) if hasattr(doc, 'pages') else 0,
                "pages": [],
                "tables": [],
                "metadata": {},
            }
            
            # Processa cada página
            for page_idx, page in enumerate(doc.pages if hasattr(doc, 'pages') else [], start=1):
                page_data = self._process_page(page, page_idx)
                extraction["pages"].append(page_data)
                
                # Salva JSON por página
                page_json_path = output_dir / f"pagina_{page_idx:03d}_{pdf_path.stem}.json"
                with open(page_json_path, "w", encoding="utf-8") as f:
                    json.dump(page_data, f, ensure_ascii=False, indent=2)
            
            # Extrai tabelas
            if hasattr(doc, 'tables'):
                for table in doc.tables:
                    extraction["tables"].append(self._process_table(table))
            
            # Metadata
            if hasattr(doc, 'metadata'):
                extraction["metadata"] = self._process_metadata(doc.metadata)
            
            logger.info(f"Extraído: {extraction['num_pages']} páginas, {len(extraction['tables'])} tabelas")
            return extraction
            
        except Exception as e:
            logger.error(f"Erro ao extrair {pdf_path.name} com Docling: {e}")
            return {
                "source": pdf_path.name,
                "error": str(e),
                "num_pages": 0,
                "pages": [],
                "tables": [],
            }

    def _process_page(self, page: Any, page_num: int) -> Dict[str, Any]:
        """Processa uma página individual."""
        page_data = {
            "page_num": page_num,
            "blocks": [],
            "type": "unknown",  # planta, corte, legenda, etc.
            "pavimento": None,
            "keywords": [],
        }
        
        # Extrai texto dos blocos
        text_content = []
        if hasattr(page, 'texts') or hasattr(page, 'elements'):
            elements = page.texts if hasattr(page, 'texts') else page.elements
            for element in elements:
                block = {
                    "type": getattr(element, 'label', 'text'),
                    "text": str(element),
                    "bbox": self._get_bbox(element),
                }
                page_data["blocks"].append(block)
                text_content.append(str(element))
        
        # Classifica tipo de página por keywords
        full_text = " ".join(text_content).lower()
        page_data["type"] = self._classify_page(full_text)
        page_data["pavimento"] = self._extract_pavimento(full_text)
        page_data["keywords"] = self._extract_keywords(full_text)
        
        return page_data

    def _process_table(self, table: Any) -> Dict[str, Any]:
        """Processa uma tabela."""
        table_data = {
            "num_rows": 0,
            "num_cols": 0,
            "cells": [],
            "type": "unknown",
        }
        
        try:
            # Extrai células
            if hasattr(table, 'data'):
                rows = table.data
                table_data["num_rows"] = len(rows)
                table_data["num_cols"] = len(rows[0]) if rows else 0
                
                for row_idx, row in enumerate(rows):
                    for col_idx, cell in enumerate(row):
                        table_data["cells"].append({
                            "row": row_idx,
                            "col": col_idx,
                            "text": str(cell),
                        })
            
            # Classifica tabela
            texts = [cell["text"].lower() for cell in table_data["cells"]]
            if any("legenda" in t or "simbologia" in t for t in texts):
                table_data["type"] = "legenda"
            elif any("quantidade" in t or "total" in t for t in texts):
                table_data["type"] = "sumario"
                
        except Exception as e:
            logger.debug(f"Erro ao processar tabela: {e}")
        
        return table_data

    def _process_metadata(self, metadata: Any) -> Dict[str, Any]:
        """Processa metadata do documento."""
        meta_dict = {}
        if hasattr(metadata, '__dict__'):
            meta_dict = {k: v for k, v in metadata.__dict__.items() if not k.startswith('_')}
        return meta_dict

    def _get_bbox(self, element: Any) -> Optional[List[float]]:
        """Extrai bounding box de um elemento."""
        if hasattr(element, 'bbox'):
            bbox = element.bbox
            if hasattr(bbox, 'as_tuple'):
                return list(bbox.as_tuple())
            return [bbox.x0, bbox.y0, bbox.x1, bbox.y1] if hasattr(bbox, 'x0') else None
        return None

    def _classify_page(self, text: str) -> str:
        """Classifica tipo de página por keywords."""
        if "legenda" in text or "simbologia" in text:
            return "legenda"
        elif "corte" in text and ("esquemático" in text or "esquematico" in text):
            return "corte"
        elif "planta" in text or "pavimento" in text:
            return "planta"
        elif "detalhe" in text:
            return "detalhe"
        elif "observa" in text and len(text) > 200:
            return "observacoes"
        return "unknown"

    def _extract_pavimento(self, text: str) -> Optional[str]:
        """Extrai pavimento mencionado na página."""
        pavimentos = {
            "subsolo": ["subsolo", "sub-solo"],
            "térreo": ["térreo", "terreo", "tér", "terreo"],
            "cobertura": ["cobertura", "coberta", "cobert"],
        }
        
        for pav, keywords in pavimentos.items():
            if any(kw in text for kw in keywords):
                return pav
        
        # Detecta pavimentos numerados (1º, 2º, etc.)
        import re
        match = re.search(r"(\d+)[ºº°]?\s*(?:pavimento|pav)", text)
        if match:
            return f"{match.group(1)}º"
        
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai keywords relevantes."""
        keywords_map = {
            "rj45": ["rj-45", "rj45"],
            "tv": ["tv coletiva", "tv assinatura"],
            "wifi": ["wifi", "wi-fi"],
            "camera": ["camera", "câmera", "cftv"],
            "interfone": ["interfone", "porteiro"],
            "cat6": ["cat-6", "cat6"],
            "rg6": ["rg-06", "rg6", "coaxial"],
            "divisor": ["divisor"],
        }
        
        found = []
        for key, patterns in keywords_map.items():
            if any(p in text for p in patterns):
                found.append(key)
        
        return found


def extract_all_pdfs(pdf_dir: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """Extrai todos os PDFs de um diretório.
    
    Args:
        pdf_dir: Diretório com PDFs
        output_dir: Diretório para salvar JSONs
        
    Returns:
        Lista de extrações
    """
    from memorial_maker.utils.io_paths import list_pdfs
    
    pdf_paths = list_pdfs(pdf_dir)
    logger.info(f"Encontrados {len(pdf_paths)} PDFs em {pdf_dir}")
    
    extractor = DoclingExtractor()
    extractions = []
    
    for pdf_path in pdf_paths:
        extraction = extractor.extract_pdf(pdf_path, output_dir)
        extractions.append(extraction)
    
    return extractions



