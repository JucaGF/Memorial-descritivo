"""Mapeamento para chaves canônicas e normalização."""

import re
from typing import Dict, List, Optional, Any
from memorial_maker.config import CANONICAL_KEYS, REGEX_PATTERNS
from memorial_maker.utils.logging import get_logger

logger = get_logger("normalize.canonical")


class CanonicalMapper:
    """Mapeia termos variados para chaves canônicas."""

    def __init__(self):
        """Inicializa mapeador."""
        self.canonical_map = CANONICAL_KEYS
        self.regex_patterns = REGEX_PATTERNS
        
        # Cria índice reverso para busca rápida
        self.reverse_map = {}
        for canonical, variants in self.canonical_map.items():
            for variant in variants:
                self.reverse_map[variant.lower()] = canonical

    def normalize_text(self, text: str) -> str:
        """Normaliza texto para busca."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def find_canonical(self, text: str) -> Optional[str]:
        """Encontra chave canônica para um termo.
        
        Args:
            text: Termo a normalizar
            
        Returns:
            Chave canônica ou None
        """
        text_norm = self.normalize_text(text)
        
        # Busca exata
        if text_norm in self.reverse_map:
            return self.reverse_map[text_norm]
        
        # Busca parcial
        for variant, canonical in self.reverse_map.items():
            if variant in text_norm or text_norm in variant:
                return canonical
        
        return None

    def extract_diametro(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrai diâmetro em mm e polegadas."""
        result = {}
        
        # Milímetros
        match = re.search(self.regex_patterns["diametro_mm"], text)
        if match:
            result["mm"] = int(match.group(1))
        
        # Polegadas
        match = re.search(self.regex_patterns["diametro_pol"], text)
        if match:
            result["polegadas"] = match.group(1)
        
        return result if result else None

    def extract_altura(self, text: str) -> Optional[float]:
        """Extrai altura em metros."""
        match = re.search(self.regex_patterns["altura"], text)
        if match:
            altura_str = match.group(1).replace(",", ".")
            return float(altura_str)
        return None

    def extract_divisor(self, text: str) -> Optional[str]:
        """Extrai tipo de divisor (1/2, 1/3, etc.)."""
        match = re.search(self.regex_patterns["divisor"], text)
        if match:
            return f"div_1_{match.group(1)}"
        return None

    def extract_data(self, text: str) -> Optional[str]:
        """Extrai data no formato DD/MM/AAAA."""
        match = re.search(self.regex_patterns["data"], text)
        if match:
            return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        return None

    def extract_escala(self, text: str) -> Optional[str]:
        """Extrai escala (ex: 1:100)."""
        match = re.search(self.regex_patterns["escala"], text)
        if match:
            return f"1:{match.group(1)}"
        return None

    def normalize_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza um item completo.
        
        Args:
            raw_item: Item com dados brutos
            
        Returns:
            Item normalizado com chaves canônicas
        """
        normalized = {}
        
        for key, value in raw_item.items():
            if not value:
                continue
            
            # Tenta mapear chave
            canonical_key = self.find_canonical(key)
            if canonical_key:
                key = canonical_key
            
            # Tenta mapear valor (para tipos de pontos, cabos, etc.)
            if isinstance(value, str):
                canonical_value = self.find_canonical(value)
                if canonical_value:
                    value = canonical_value
            
            normalized[key] = value
        
        return normalized


class ItemExtractor:
    """Extrai itens estruturados de texto/tabelas."""

    def __init__(self):
        """Inicializa extrator."""
        self.mapper = CanonicalMapper()

    def extract_from_text(self, text: str, page_context: Dict = None) -> List[Dict[str, Any]]:
        """Extrai itens de texto livre.
        
        Args:
            text: Texto a processar
            page_context: Contexto da página (pavimento, tipo, etc.)
            
        Returns:
            Lista de itens extraídos
        """
        items = []
        lines = text.split("\n")
        
        current_item = {}
        if page_context:
            current_item["pavimento"] = page_context.get("pavimento")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detecta tipo de ponto
            tipo = self.mapper.find_canonical(line)
            if tipo and tipo.startswith("point_"):
                if current_item.get("tipo"):
                    items.append(current_item.copy())
                current_item = {"tipo": tipo}
                if page_context:
                    current_item["pavimento"] = page_context.get("pavimento")
            
            # Extrai quantidade
            match = re.search(r"(\d+)\s*(?:un|unid|unidades?|pontos?|pçs?)", line.lower())
            if match:
                current_item["quantidade"] = int(match.group(1))
            
            # Extrai altura
            altura = self.mapper.extract_altura(line)
            if altura:
                current_item["altura_m"] = altura
            
            # Extrai diâmetro
            diam = self.mapper.extract_diametro(line)
            if diam:
                current_item.update(diam)
            
            # Extrai cabo
            cabo = self.mapper.find_canonical(line)
            if cabo and cabo in ["cat6", "rg6_u90", "cci2"]:
                if "cabos" not in current_item:
                    current_item["cabos"] = []
                current_item["cabos"].append(cabo)
            
            # Extrai divisor
            divisor = self.mapper.extract_divisor(line)
            if divisor:
                current_item["divisor"] = divisor
        
        # Adiciona último item
        if current_item.get("tipo"):
            items.append(current_item)
        
        return items

    def extract_from_table(self, table: Dict[str, Any], page_context: Dict = None) -> List[Dict[str, Any]]:
        """Extrai itens de uma tabela.
        
        Args:
            table: Dados da tabela
            page_context: Contexto da página
            
        Returns:
            Lista de itens extraídos
        """
        items = []
        cells = table.get("cells", [])
        
        if not cells:
            return items
        
        # Organiza células por linha
        rows = {}
        for cell in cells:
            row_idx = cell.get("row", 0)
            if row_idx not in rows:
                rows[row_idx] = []
            rows[row_idx].append(cell)
        
        # Processa cada linha como um possível item
        for row_idx in sorted(rows.keys()):
            row_cells = sorted(rows[row_idx], key=lambda c: c.get("col", 0))
            row_text = " ".join(c.get("text", "") for c in row_cells)
            
            # Extrai itens do texto da linha
            row_items = self.extract_from_text(row_text, page_context)
            items.extend(row_items)
        
        return items


def normalize_all_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normaliza lista de itens.
    
    Args:
        raw_items: Itens brutos
        
    Returns:
        Itens normalizados
    """
    mapper = CanonicalMapper()
    normalized = []
    
    for item in raw_items:
        norm_item = mapper.normalize_item(item)
        if norm_item.get("tipo"):  # Só inclui se tiver tipo identificado
            normalized.append(norm_item)
    
    logger.info(f"Normalizados {len(normalized)} itens de {len(raw_items)} brutos")
    return normalized











