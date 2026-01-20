"""Extração de PDFs usando Unstructured.io"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.staging.base import elements_to_json
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    partition_pdf = None
    elements_to_json = None

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger

logger = get_logger("extract.unstructured")


def extract_carimbo_from_text(text: str) -> Dict[str, str]:
    """Extrai informações do carimbo (canto inferior direito) do texto.
    
    O carimbo pode estar em diferentes formatos:
    1. Labels e valores na mesma linha: PROJETO: Valor
    2. Labels em uma linha, valores nas linhas seguintes
    
    Args:
        text: Texto extraído do PDF
        
    Returns:
        Dicionário com dados do carimbo
    """
    import re
    
    carimbo_data = {}
    
    # Primeiro, procura pelo padrão onde todos os labels estão juntos
    # PROJETO: CONSTRUTOR: EDIFÍCIO: LOCAL: Escala:
    # E os valores vêm nas linhas seguintes
    pattern_labels = r'PROJETO:\s*CONSTRUTOR:\s*EDIF[ÍI]CIO:\s*LOCAL:'
    match_labels = re.search(pattern_labels, text, re.IGNORECASE)
    
    if match_labels:
        # Encontrou o padrão com labels juntos
        # Pega o texto após os labels
        start_pos = match_labels.end()
        # Pega as próximas 1500 caracteres para ter mais contexto
        text_after = text[start_pos:start_pos + 1500]
        
        # Divide em linhas e pega os valores
        lines = [l.strip() for l in text_after.split('\n') if l.strip()]
        
        # Mapeia valores baseado na ordem esperada
        # Linha 0: Escala: (descartamos ou pegamos depois)
        # Linha 1: Nome do projeto (ex: PROJETO DE INSTALAÇÕES DE TELECOMUNICAÇÃO)
        # Linha 2: Construtora (ex: MGA CONSTRUÇÕES E INCORPORAÇÕES LTDA)
        # Linha 3: Empreendimento (ex: MAKAI)
        # Linha 4: Endereço (ex: AVENIDA MAX ZAGEL, S/N...)
        # Linha 5+: Outras informações
        
        if len(lines) >= 1:
            # Primeira linha pode ser "Escala:" ou já ser o projeto
            first_line = lines[0]
            if 'Escala:' in first_line or 'ESCALA:' in first_line.upper():
                # Pula essa linha e pega as próximas
                value_lines = lines[1:]
            else:
                value_lines = lines
            
            # Agora pega os valores na ordem: projeto, construtora, empreendimento
            # Mas o endereço pode estar em qualquer posição, então procuramos em todas as linhas
            
            if len(value_lines) >= 1:
                projeto = value_lines[0]
                if 'PROJETO' not in projeto.upper() or 'DE ' in projeto or 'INSTALAÇÃO' in projeto.upper():
                    carimbo_data["projeto"] = projeto
                    
            if len(value_lines) >= 2:
                construtora = value_lines[1]
                if len(construtora) > 3 and 'EDIFÍCIO' not in construtora.upper():
                    carimbo_data["construtora"] = construtora
                    
            if len(value_lines) >= 3:
                empreendimento = value_lines[2]
                if len(empreendimento) > 2 and empreendimento != 'LOCAL':
                    carimbo_data["empreendimento"] = empreendimento
            
            # Procura por endereço em TODAS as linhas (não só na posição 3)
            # porque o texto pode estar em ordem diferente da visual
            for i, line in enumerate(value_lines):
                # Ignora linhas já identificadas como projeto, construtora, empreendimento
                if i < 3:
                    continue
                
                # Verifica se parece com um endereço
                is_address = (
                    ',' in line and len(line) > 15 and
                    any(word in line.upper() for word in ['AVENIDA', 'RUA', 'AV.', 'R.', 'LOTE', 'QUADRA', 'TRAVESSA', 'AL.', 'ALAMEDA'])
                )
                
                if is_address and "endereco" not in carimbo_data:
                    carimbo_data["endereco"] = line
                    logger.info(f"Endereço encontrado na linha {i}: {line}")
                    break
                
                # Procura por escala
                if '/' in line and len(line) < 10 and "escala" not in carimbo_data:
                    carimbo_data["escala"] = line
        
        logger.info(f"Carimbo extraído (formato labels juntos): {list(carimbo_data.keys())}")
        
    else:
        # Tenta padrões tradicionais com labels e valores na mesma linha
        patterns = {
            "projeto": r"PROJETO\s*:\s*([^\n]+?)(?=\s*(?:CONSTRUTOR|EDIF[ÍI]CIO|LOCAL|DATA|$))",
            "construtora": r"CONSTRUTOR\s*:\s*([^\n]+?)(?=\s*(?:EDIF[ÍI]CIO|LOCAL|DATA|$))",
            "empreendimento": r"EDIF[ÍI]CIO\s*:\s*([^\n]+?)(?=\s*(?:LOCAL|DATA|$))",
            "endereco": r"LOCAL\s*:\s*([^\n]+?)(?=\s*(?:DATA|Escala|$))",
            "data": r"DATA\s*:\s*([0-9]{2}[\/\-][0-9]{2}[\/\-][0-9]{4})",
            "escala": r"Escala\s*:\s*([^\n]+)",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Remove labels extras que possam ter sido capturados
                value = re.sub(r'\s*(CONSTRUTOR|EDIF[ÍI]CIO|LOCAL|DATA|Escala)\s*:.*$', '', value, flags=re.IGNORECASE)
                if value and len(value) > 1:
                    carimbo_data[key] = value
                    logger.debug(f"Carimbo - {key}: {value}")
    
    # Procura por data no formato dd/mm/yyyy em qualquer lugar próximo
    if not carimbo_data.get("data"):
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            carimbo_data["data"] = date_match.group(1)
    
    # Se ainda não encontrou endereço, procura perto do carimbo no texto
    # Busca por padrões comuns de endereço brasileiro que contenham palavras-chave de localização
    if not carimbo_data.get("endereco"):
        # Busca texto ao redor do empreendimento se tivermos essa informação
        search_text = text
        if carimbo_data.get("empreendimento"):
            emp_pos = text.find(carimbo_data["empreendimento"])
            if emp_pos > 0:
                # Pega 2000 chars antes e depois do empreendimento
                search_text = text[max(0, emp_pos - 2000):emp_pos + 2000]
        
        # Padrão: deve começar com AVENIDA/RUA/etc e conter LOTE ou QUADRA ou número da casa
        # e ter cidade ou estado no final
        endereco_pattern = r'((?:AVENIDA|AV\.|RUA|R\.|TRAVESSA|TRAV\.|ALAMEDA|AL\.)[^,]{5,100}(?:LOTE|QUADRA|N[ºo°]|S/N)[^,]{0,50},[^,]{3,60}(?:-\s*[A-Z]{2})?)'
        
        match = re.search(endereco_pattern, search_text, re.IGNORECASE)
        if match:
            endereco_candidate = match.group(1).strip()
            # Remove quebras de linha e espaços extras
            endereco_candidate = ' '.join(endereco_candidate.split())
            carimbo_data["endereco"] = endereco_candidate
            logger.info(f"Endereço encontrado via regex: {endereco_candidate[:60]}...")
    
    return carimbo_data


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
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError(
            "Unstructured.io não está instalado ou não pôde ser carregado. "
            "Esta é uma dependência CRÍTICA para o funcionamento do Memorial Maker. "
            "Execute: pip install unstructured[pdf]"
        )
    
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
            "carimbo": {},
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
        
        # Extrai informações do carimbo do texto completo
        full_text = "\n".join([item["text"] for item in result["text"]])
        carimbo_info = extract_carimbo_from_text(full_text)
        result["carimbo"] = carimbo_info
        
        if carimbo_info:
            logger.info(f"Carimbo extraído: {list(carimbo_info.keys())}")
        
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
        raise e


def extract_all_pdfs(
    pdf_dir: Path,
    output_dir: Path,
    memorial_type: str = "telecom",
    progress_callback: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    """Extrai conteúdo de todos os PDFs de um diretório.
    
    Args:
        pdf_dir: Diretório com PDFs
        output_dir: Diretório de saída
        memorial_type: Tipo de memorial ("telecom" ou "eletrico")
        progress_callback: Função opcional para reportar progresso (current, total)
        
    Returns:
        Lista de resultados de extração
    """
    # Ambos os tipos (telecom e elétrico) usam a mesma extração sequencial confiável
    # A extração paralela estava causando travamentos, então desabilitamos por enquanto
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Encontrados {len(pdf_files)} PDFs em {pdf_dir}")
    
    results = []
    total_files = len(pdf_files)
    
    for i, pdf_path in enumerate(pdf_files, 1):
        result = extract_pdf_unstructured(pdf_path, output_dir)
        results.append(result)
        
        if progress_callback:
            try:
                progress_callback(i, total_files)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
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



