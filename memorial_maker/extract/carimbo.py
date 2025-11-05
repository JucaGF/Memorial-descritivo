"""Extração e parsing de carimbo de projetos."""

import re
from typing import Dict, Optional, List
from memorial_maker.utils.logging import get_logger

logger = get_logger("extract.carimbo")


class CarimboParser:
    """Parser de carimbo de projetos técnicos."""

    def __init__(self):
        """Inicializa parser."""
        self.patterns = {
            "construtora": r"(?:construtora|empresa)[:\s]+([^\n]+)",
            "empreendimento": r"(?:empreendimento|obra)[:\s]+([^\n]+)",
            "endereco": r"(?:endere[çc]o|local)[:\s]+([^\n]+)",
            "projeto": r"(?:projeto|desenho)[:\s]+([^\n]+)",
            "revisao": r"rev(?:\.|:)?\s*(\w+)",
            "data": r"(\d{2})[/-](\d{2})[/-](\d{4})",
            "escala": r"(?:escala|esc\.?)\s*[:\-]?\s*1[:/](\d+)",
            "autor": r"(?:autor|desenhista|projetista)[:\s]+([^\n]+)",
            "arquivo": r"(?:arquivo|dwg|n[°º])[:\s]+([^\n]+)",
        }

    def parse(self, text: str) -> Dict[str, str]:
        """Parse de texto do carimbo.
        
        Args:
            text: Texto extraído do carimbo
            
        Returns:
            Dicionário com campos identificados
        """
        parsed = {
            "construtora": "",
            "empreendimento": "",
            "endereco": "",
            "projeto": "",
            "revisao": "",
            "data": "",
            "escala": "",
            "autor": "",
            "arquivo": "",
        }
        
        text_lower = text.lower()
        lines = text.split("\n")
        
        for field, pattern in self.patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                if field == "data":
                    parsed[field] = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                elif field == "escala":
                    parsed[field] = f"1:{match.group(1)}"
                elif field == "revisao":
                    parsed[field] = match.group(1).upper()
                else:
                    # Busca linha original (não lowercase) para preservar maiúsculas
                    for line in lines:
                        if re.search(pattern, line.lower()):
                            value = line.split(":", 1)[-1].strip() if ":" in line else match.group(1)
                            parsed[field] = value.strip()
                            break
        
        # Heurísticas adicionais
        parsed = self._apply_heuristics(parsed, lines)
        
        return parsed

    def _apply_heuristics(self, parsed: Dict[str, str], lines: List[str]) -> Dict[str, str]:
        """Aplica heurísticas para melhorar parsing."""
        
        # Se não encontrou empreendimento, tenta linha com palavras-chave
        if not parsed["empreendimento"]:
            for line in lines:
                line_upper = line.upper()
                if any(kw in line_upper for kw in ["EDIFÍCIO", "EDIFICIO", "RESIDENCIAL", "COMERCIAL", "TOWER", "PLAZA"]):
                    parsed["empreendimento"] = line.strip()
                    break
        
        # Se não encontrou construtora, tenta linhas iniciais com nome próprio
        if not parsed["construtora"]:
            for line in lines[:5]:
                if len(line) > 10 and line[0].isupper() and not line.lower().startswith(("projeto", "desenho", "escala")):
                    parsed["construtora"] = line.strip()
                    break
        
        # Limpa valores
        for key in parsed:
            parsed[key] = parsed[key].replace("\t", " ").strip()
        
        return parsed

    def extract_tipologia(self, text: str) -> Optional[str]:
        """Extrai tipologia do projeto (pavimento/tipo de folha)."""
        text_lower = text.lower()
        
        tipologias = {
            "subsolo": ["subsolo", "sub-solo", "sub solo"],
            "térreo": ["térreo", "terreo", "tér", "tér."],
            "tipo": ["pavimento tipo", "pav tipo", "pav. tipo", "tipo"],
            "cobertura": ["cobertura", "coberta", "cobert", "cob"],
            "corte": ["corte esquemático", "corte esquematico"],
        }
        
        for tipo, keywords in tipologias.items():
            if any(kw in text_lower for kw in keywords):
                return tipo
        
        # Detecta pavimentos numerados
        match = re.search(r"(\d+)[ºº°]\s*(?:pavimento|pav)", text_lower)
        if match:
            return f"{match.group(1)}º pavimento"
        
        return None


def merge_carimbo_data(extractions: list) -> Dict[str, any]:
    """Merge dados de carimbo de múltiplas páginas.
    
    Args:
        extractions: Lista de extrações de páginas
        
    Returns:
        Dicionário consolidado com dados da obra
    """
    parser = CarimboParser()
    
    # Coleta todos os carimbos
    carimbos = []
    for extraction in extractions:
        for page in extraction.get("pages", []):
            rois = page.get("rois", {})
            if "carimbo" in rois:
                carimbo_parsed = rois["carimbo"].get("parsed", {})
                if carimbo_parsed:
                    carimbos.append(carimbo_parsed)
    
    if not carimbos:
        logger.warning("Nenhum carimbo encontrado")
        return {}
    
    # Merge: prioriza valores mais completos
    merged = {}
    for field in ["construtora", "empreendimento", "endereco", "projeto", "autor"]:
        values = [c.get(field, "") for c in carimbos if c.get(field)]
        # Pega o mais longo (geralmente mais completo)
        merged[field] = max(values, key=len) if values else ""
    
    # Para revisão, data, escala: pega o mais recente/último
    for field in ["revisao", "data", "escala", "arquivo"]:
        values = [c.get(field, "") for c in carimbos if c.get(field)]
        merged[field] = values[-1] if values else ""
    
    return merged



