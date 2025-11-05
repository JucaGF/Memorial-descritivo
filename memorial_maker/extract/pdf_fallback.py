"""Fallback de extração usando PyMuPDF + OpenCV + OCR."""

import cv2
import numpy as np
import fitz  # PyMuPDF
import pytesseract
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger
from memorial_maker.utils.cv_utils import (
    preprocess_image,
    deskew_image,
    extract_roi,
    enhance_for_ocr,
)

logger = get_logger("extract.fallback")


class PDFFallbackExtractor:
    """Extrator fallback usando PyMuPDF + OpenCV + Tesseract."""

    def __init__(self):
        """Inicializa extrator."""
        self.dpi = settings.dpi
        self.tesseract_config = (
            f"--psm {settings.tesseract_psm} "
            f"-l {settings.tesseract_lang} "
            f"-c tessedit_char_whitelist='{settings.ocr_whitelist}'"
        )

    def extract_pdf(self, pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Extrai PDF usando fallback."""
        logger.info(f"Extração fallback: {pdf_path.name}")
        
        try:
            doc = fitz.open(pdf_path)
            extraction = {
                "source": pdf_path.name,
                "num_pages": len(doc),
                "pages": [],
            }
            
            for page_num in range(len(doc)):
                page_data = self._process_page(doc, page_num, output_dir, pdf_path.stem)
                extraction["pages"].append(page_data)
            
            doc.close()
            return extraction
            
        except Exception as e:
            logger.error(f"Erro no fallback para {pdf_path.name}: {e}")
            return {"source": pdf_path.name, "error": str(e), "pages": []}

    def _process_page(
        self,
        doc: fitz.Document,
        page_num: int,
        output_dir: Path,
        pdf_stem: str,
    ) -> Dict[str, Any]:
        """Processa uma página."""
        page = doc[page_num]
        page_data = {
            "page_num": page_num + 1,
            "text_blocks": [],
            "drawings": [],
            "images": [],
            "rois": {},
        }
        
        # Extrai texto estruturado
        try:
            text_dict = page.get_text("rawdict")
            for block in text_dict.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    page_data["text_blocks"].append({
                        "bbox": block.get("bbox"),
                        "text": self._extract_block_text(block),
                    })
        except Exception as e:
            logger.debug(f"Erro ao extrair texto estruturado da página {page_num + 1}: {e}")
        
        # Extrai drawings (linhas, formas)
        try:
            drawings = page.get_drawings()
            page_data["drawings"] = [
                {"type": d.get("type"), "rect": d.get("rect")}
                for d in drawings[:100]  # Limita para não sobrecarregar
            ]
        except Exception as e:
            logger.debug(f"Erro ao extrair drawings da página {page_num + 1}: {e}")
        
        # Renderiza página para OCR de ROIs
        try:
            pix = page.get_pixmap(dpi=self.dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )
            if pix.n == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 1:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            # Extrai ROIs específicas
            page_data["rois"] = self._extract_rois(img, output_dir, page_num + 1, pdf_stem)
            
        except Exception as e:
            logger.debug(f"Erro ao processar imagem da página {page_num + 1}: {e}")
        
        return page_data

    def _extract_block_text(self, block: Dict) -> str:
        """Extrai texto de um bloco."""
        lines = []
        for line in block.get("lines", []):
            spans = []
            for span in line.get("spans", []):
                spans.append(span.get("text", ""))
            lines.append(" ".join(spans))
        return "\n".join(lines)

    def _extract_rois(
        self,
        image: np.ndarray,
        output_dir: Path,
        page_num: int,
        pdf_stem: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Extrai ROIs padrão da imagem."""
        rois = {}
        
        # ROI: Carimbo (canto inferior direito)
        try:
            carimbo_roi = extract_roi(
                image,
                settings.carimbo_x_start,
                settings.carimbo_y_start,
                1.0,
                1.0,
            )
            carimbo_text = self._ocr_roi(carimbo_roi, "carimbo")
            rois["carimbo"] = {
                "text": carimbo_text,
                "parsed": self._parse_carimbo(carimbo_text),
            }
            
            # Salva debug
            debug_path = output_dir / f"roi_carimbo_p{page_num:03d}_{pdf_stem}.png"
            cv2.imwrite(str(debug_path), carimbo_roi)
            
        except Exception as e:
            logger.debug(f"Erro ao extrair carimbo: {e}")
            rois["carimbo"] = {"text": "", "parsed": {}}
        
        # ROI: Legenda (parte inferior)
        try:
            legenda_roi = extract_roi(
                image,
                settings.legenda_x_start,
                settings.legenda_y_start,
                1.0,
                1.0,
            )
            legenda_text = self._ocr_roi(legenda_roi, "legenda")
            rois["legenda"] = {"text": legenda_text}
            
            debug_path = output_dir / f"roi_legenda_p{page_num:03d}_{pdf_stem}.png"
            cv2.imwrite(str(debug_path), legenda_roi)
            
        except Exception as e:
            logger.debug(f"Erro ao extrair legenda: {e}")
            rois["legenda"] = {"text": ""}
        
        return rois

    def _ocr_roi(self, roi_image: np.ndarray, roi_type: str) -> str:
        """Executa OCR em uma ROI."""
        try:
            # Preprocessa
            processed = enhance_for_ocr(roi_image)
            
            # Deskew
            deskewed, angle = deskew_image(processed)
            if abs(angle) > 0.5:
                logger.debug(f"Corrigido ângulo de {angle:.2f}° em {roi_type}")
            
            # OCR
            text = pytesseract.image_to_string(
                deskewed,
                config=self.tesseract_config,
            )
            
            return text.strip()
            
        except Exception as e:
            logger.debug(f"Erro ao fazer OCR de {roi_type}: {e}")
            return ""

    def _parse_carimbo(self, text: str) -> Dict[str, str]:
        """Parse do carimbo para extrair campos."""
        import re
        
        parsed = {
            "projeto": "",
            "desenho": "",
            "revisao": "",
            "data": "",
            "escala": "",
            "autor": "",
            "arquivo": "",
        }
        
        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower()
            
            # Projeto/Desenho
            if "projeto" in line_lower or "desenho" in line_lower:
                parsed["projeto"] = line.split(":", 1)[-1].strip() if ":" in line else line
            
            # Revisão
            match = re.search(r"rev(?:\.|:)?\s*(\w+)", line_lower)
            if match:
                parsed["revisao"] = match.group(1).upper()
            
            # Data
            match = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", line)
            if match:
                parsed["data"] = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
            
            # Escala
            match = re.search(r"(?:escala|esc\.?)\s*[:\-]?\s*1[:/](\d+)", line_lower)
            if match:
                parsed["escala"] = f"1:{match.group(1)}"
            
            # Autor
            if "autor" in line_lower or "desenhista" in line_lower:
                parsed["autor"] = line.split(":", 1)[-1].strip() if ":" in line else ""
            
            # Arquivo
            if "arquivo" in line_lower or ".dwg" in line_lower:
                parsed["arquivo"] = line.split(":", 1)[-1].strip() if ":" in line else line
        
        return parsed


def enhance_extraction_with_fallback(
    docling_data: Dict[str, Any],
    pdf_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    """Complementa extração Docling com fallback onde necessário."""
    logger.info(f"Complementando extração com fallback para {pdf_path.name}")
    
    fallback = PDFFallbackExtractor()
    fallback_data = fallback.extract_pdf(pdf_path, output_dir)
    
    # Merge: prioriza Docling, complementa com fallback
    merged = docling_data.copy()
    
    for i, docling_page in enumerate(merged.get("pages", [])):
        if i < len(fallback_data.get("pages", [])):
            fallback_page = fallback_data["pages"][i]
            
            # Adiciona ROIs do fallback
            docling_page["rois"] = fallback_page.get("rois", {})
            
            # Se Docling não encontrou texto, usa fallback
            if not docling_page.get("blocks"):
                docling_page["blocks_fallback"] = fallback_page.get("text_blocks", [])
    
    return merged






