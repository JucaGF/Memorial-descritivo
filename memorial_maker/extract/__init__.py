"""Módulos de extração de dados de PDFs usando Unstructured.io"""

from memorial_maker.extract.unstructured_extract import (
    extract_pdf_unstructured,
    extract_all_pdfs,
    extract_text_from_elements,
    extract_tables_structured,
)
from memorial_maker.extract.optimized_extract import (
    extract_pdf_hybrid,
    extract_all_pdfs_optimized,
)

__all__ = [
    "extract_pdf_unstructured",
    "extract_all_pdfs",
    "extract_text_from_elements",
    "extract_tables_structured",
    "extract_pdf_hybrid",
    "extract_all_pdfs_optimized",
]











