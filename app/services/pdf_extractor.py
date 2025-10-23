"""
PDF Extractor Service - Extraction of text, images, and metadata from PDF files.
Uses PyMuPDF (fitz) for robust PDF processing.
"""

import fitz  # PyMuPDF
from typing import Dict, List, Any
import io
from PIL import Image
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Handles extraction of data from PDF files.
    """
    
    def __init__(self):
        self.supported_image_formats = ["png", "jpeg", "jpg"]
    
    def extract(self, file_path: str, extract_images: bool = True) -> Dict[str, Any]:
        """
        Extract all data from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            extract_images: Whether to extract images from the PDF
            
        Returns:
            Dictionary containing:
                - text: Extracted text from all pages
                - images: List of extracted images (if extract_images=True)
                - metadata: PDF metadata
                - pages: Number of pages
        """
        try:
            logger.info(f"Starting PDF extraction from: {file_path}")
            
            # Open PDF
            pdf_document = fitz.open(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(pdf_document)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                text_content.append(f"--- Página {page_num + 1} ---\n{page_text}")
            
            full_text = "\n\n".join(text_content)
            
            # Extract images if requested
            images = []
            if extract_images:
                images = self._extract_images(pdf_document)
            
            result = {
                "text": full_text,
                "images": images,
                "metadata": metadata,
                "pages": pdf_document.page_count
            }
            
            pdf_document.close()
            
            logger.info(f"Successfully extracted {pdf_document.page_count} pages, "
                       f"{len(images)} images, {len(full_text)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise Exception(f"Failed to extract PDF: {str(e)}")
    
    def _extract_metadata(self, pdf_document: fitz.Document) -> Dict[str, Any]:
        """
        Extract metadata from PDF document.
        """
        metadata = pdf_document.metadata
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": pdf_document.page_count
        }
    
    def _extract_images(self, pdf_document: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract images from PDF document.
        """
        images = []
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            for img_index, img_info in enumerate(image_list):
                try:
                    xref = img_info[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Convert to base64 for easy storage/transmission
                    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    images.append({
                        "page": page_num + 1,
                        "index": img_index,
                        "format": image_ext,
                        "data": image_b64,
                        "size": len(image_bytes)
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {str(e)}")
                    continue
        
        logger.info(f"Extracted {len(images)} images from PDF")
        return images
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Quick extraction of only text content.
        """
        try:
            pdf_document = fitz.open(file_path)
            text_content = []
            
            for page in pdf_document:
                text_content.append(page.get_text())
            
            pdf_document.close()
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")

