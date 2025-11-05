"""Extração de PDFs usando Unstructured.io"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger

logger = get_logger("extract.unstructured")


def extract_pdf_unstructured(
    pdf_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    """Extrai conteúdo de PDF usando Unstructured.io
    
    Args:
        pdf_path: Caminho do PDF
        output_dir: Diretório de saída
        
    Returns:
        Dicionário com dados extraídos estruturados
    """
    logger.info(f"Extraindo com Unstructured: {pdf_path.name}")
    
    try:
        # Particiona o PDF com Unstructured
        elements = partition_pdf(
            filename=str(pdf_path),
            strategy=settings.unstructured_strategy,  # "hi_res" para melhor qualidade
            infer_table_structure=settings.extract_tables,
            extract_images_in_pdf=settings.extract_images,
            languages=["por"],  # Português
            model_name=settings.unstructured_model_name if settings.extract_tables else None,
        )
        
        logger.info(f"Extraídos {len(elements)} elementos")
        
        # Organiza elementos por tipo
        result = {
            "filename": pdf_path.name,
            "total_elements": len(elements),
            "text": [],
            "tables": [],
            "metadata": {},
        }
        
        # Processa cada elemento
        for element in elements:
            element_type = type(element).__name__
            
            if element_type == "Title":
                result["text"].append({
                    "type": "title",
                    "text": str(element),
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                })
                
            elif element_type == "Table":
                # Extrai tabela estruturada
                table_data = {
                    "type": "table",
                    "text": str(element),
                    "html": element.metadata.text_as_html if hasattr(element.metadata, 'text_as_html') else None,
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                result["tables"].append(table_data)
                
            elif element_type in ["NarrativeText", "Text", "ListItem"]:
                result["text"].append({
                    "type": element_type.lower(),
                    "text": str(element),
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                })
        
        # Salva JSON com todos os elementos
        output_json = output_dir / f"{pdf_path.stem}_unstructured.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Extraído: {len(result['text'])} textos, {len(result['tables'])} tabelas")
        logger.info(f"Salvo em: {output_json}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao extrair {pdf_path.name}: {e}")
        return {
            "filename": pdf_path.name,
            "error": str(e),
            "total_elements": 0,
            "text": [],
            "tables": [],
            "metadata": {},
        }


def extract_all_pdfs(
    pdf_dir: Path,
    output_dir: Path,
) -> List[Dict[str, Any]]:
    """Extrai conteúdo de todos os PDFs de um diretório.
    
    Args:
        pdf_dir: Diretório com PDFs
        output_dir: Diretório de saída
        
    Returns:
        Lista de resultados de extração
    """
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Encontrados {len(pdf_files)} PDFs em {pdf_dir}")
    
    results = []
    
    for pdf_path in pdf_files:
        result = extract_pdf_unstructured(pdf_path, output_dir)
        results.append(result)
    
    # Salva JSON consolidado
    consolidated_json = output_dir / "all_extractions.json"
    with open(consolidated_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Extração consolidada salva em: {consolidated_json}")
    
    return results


def extract_text_from_elements(result: Dict[str, Any]) -> str:
    """Extrai texto limpo dos elementos para uso com LLM.
    
    Args:
        result: Resultado da extração do Unstructured
        
    Returns:
        Texto limpo e concatenado
    """
    text_parts = []
    
    # Adiciona textos
    for item in result.get("text", []):
        text = item.get("text", "").strip()
        if text:
            text_parts.append(text)
    
    # Adiciona conteúdo de tabelas
    for table in result.get("tables", []):
        text = table.get("text", "").strip()
        if text:
            text_parts.append(f"\n[TABELA]\n{text}\n[/TABELA]\n")
    
    return "\n\n".join(text_parts)


def extract_tables_structured(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai tabelas estruturadas para análise.
    
    Args:
        result: Resultado da extração do Unstructured
        
    Returns:
        Lista de tabelas estruturadas
    """
    tables = []
    
    for i, table in enumerate(result.get("tables", []), 1):
        tables.append({
            "table_id": i,
            "text": table.get("text", ""),
            "html": table.get("html"),
            "metadata": table.get("metadata", {}),
        })
    
    return tables



