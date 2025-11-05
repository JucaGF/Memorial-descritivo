"""Configurações globais do sistema."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-5")
    embed_model: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    llm_temperature: float = 0.0
    llm_top_p: float = 0.1
    llm_max_tokens: int = 4096

    # Extração - Unstructured
    unstructured_strategy: str = os.getenv("UNSTRUCTURED_STRATEGY", "fast")  # "fast", "hi_res", "ocr_only", "auto"
    unstructured_model_name: str = "yolox"  # para detecção de tabelas
    extract_images: bool = os.getenv("EXTRACT_IMAGES", "true").lower() == "true"
    extract_tables: bool = True
    chunk_by_title: bool = True
    
    # Configurações de imagem/PDF (para compatibilidade)
    dpi: int = 300

    # Processamento
    parallel_execution: bool = True
    max_retries: int = 3

    # Caminhos
    runtime_dir: Path = Path("./runtime")
    out_dir: Path = Path("./out")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância global
settings = Settings()


# Constantes de normalização
CANONICAL_KEYS = {
    # Cabos
    "cat6": ["cat-6", "cat 6", "cat6", "categoria 6", "u/utp cat6"],
    "rg6_u90": ["rg-06/u#90%", "rg06/u#90%", "rg-6", "rg6", "rg-06 u#90", "coaxial rg6"],
    "cci2": ["cci-2", "cci 2", "cci2", "cabo cci2"],
    "mb10": ["mb-10", "mb 10", "mb10", "caixa mb10"],
    
    # Pontos
    "point_rj45": ["rj-45", "rj45", "ponto rj45", "ponto de dados", "tomada rj45"],
    "point_tv_coletiva": ["tv coletiva", "tv col", "ponto tv col"],
    "point_tv_assinatura": ["tv assinatura", "tv ass", "ponto tv ass"],
    "point_telefone": ["telefone", "tel", "ponto tel"],
    "point_interfone": ["interfone", "interf", "ponto interfone"],
    
    # Wi-Fi
    "wifi_indoor": ["wifi indoor", "wi-fi indoor", "roteador indoor", "ap indoor"],
    "wifi_outdoor": ["wifi outdoor", "wi-fi outdoor", "roteador outdoor", "ap outdoor"],
    
    # Câmeras
    "cam_bullet": ["camera bullet", "câmera bullet", "cam bullet", "bullet"],
    "cam_dome": ["camera dome", "câmera dome", "cam dome", "dome"],
    
    # Divisores
    "div_1_2": ["divisor 1/2", "div 1/2", "1/2", "divisor 1x2"],
    "div_1_3": ["divisor 1/3", "div 1/3", "1/3", "divisor 1x3"],
    "div_1_4": ["divisor 1/4", "div 1/4", "1/4", "divisor 1x4"],
    "div_1_5": ["divisor 1/5", "div 1/5", "1/5", "divisor 1x5"],
    
    # Infraestrutura
    "quadro_vdi": ["quadro vdi", "qvdi", "quadro de distribuição"],
    "dg": ["d.g.", "dg", "distribuição geral"],
    "rack": ["rack", "bastidor"],
    
    # Pavimentos
    "subsolo": ["subsolo", "sub-solo", "sub"],
    "terreo": ["térreo", "terreo", "térreo", "tér"],
    "pavimento_tipo": ["pavimento tipo", "pav tipo", "tipo"],
    "cobertura": ["cobertura", "coberta", "cob"],
}

# Regex patterns para extração
REGEX_PATTERNS = {
    "diametro_mm": r"[∅Ø]?\s*(\d+)\s*mm",
    "diametro_pol": r'(\d+(?:/\d+)?)\s*["\']',
    "altura": r"[Hh]\s*=\s*(\d+(?:[,.]\d+)?)\s*m",
    "divisor": r"divisor\s+1[/x](\d)",
    "revisao": r"rev(?:\.|:)?\s*(\w+)",
    "data": r"(\d{2})[/-](\d{2})[/-](\d{4})",
    "escala": r"(?:escala|esc\.?)\s*[:\-]?\s*1[:/](\d+)",
}

# Normas técnicas padrão
NORMAS_PADRAO = [
    "NBR 14565 - Cabeamento de telecomunicações para edifícios comerciais",
    "NBR 16264 - Cabeamento estruturado residencial",
    "EIA/TIA-569 - Commercial Building Standard for Telecommunications Pathways and Spaces",
    "IEEE 802.3ah - Ethernet in the First Mile",
    "ISO/TIA 568-C - Commercial Building Telecommunications Cabling Standard",
    "ISO/TIA 569-B - Commercial Building Standard for Telecommunications Pathways and Spaces",
    "ISO/TIA 606-A - Administration Standard for Commercial Telecommunications Infrastructure",
    "ISO/TIA 607-B - Generic Telecommunications Bonding and Grounding for Customer Premises",
    "ISO/TIA 942 - Data Center Standards Overview",
    "NBR 5410 - Instalações elétricas de baixa tensão",
]




