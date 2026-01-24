"""Schema and generator for DADOS DA OBRA section following reference memorial standard."""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class DadosObraField:
    """Field definition for DADOS DA OBRA section."""
    label: str  # Display label (exactly as in reference model)
    key: str  # Key in master_data['obra']
    required: bool  # If True, show "Não informado" when missing
    formatter: Optional[Callable[[Any], str]] = None  # Optional value formatter


# SCHEMA: Exact field list from reference memorial
# Order matches reference document structure
DADOS_OBRA_SCHEMA = [
    DadosObraField(
        label="CONSTRUTORA",
        key="construtora",
        required=True
    ),
    DadosObraField(
        label="EMPREENDIMENTO",
        key="empreendimento",
        required=True
    ),
    DadosObraField(
        label="ENDEREÇO",
        key="endereco",
        required=True
    ),
    DadosObraField(
        label="TIPO DE EDIFICAÇÃO",
        key="tipo_edificacao",
        required=False  # If not present in reference as mandatory, set False
    ),
    DadosObraField(
        label="TIPOLOGIA",
        key="tipologia",
        required=False
    ),
    DadosObraField(
        label="PAVIMENTOS",
        key="pavimentos",
        required=False,
        formatter=lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    ),
    DadosObraField(
        label="NÚMERO DE UNIDADES",
        key="numero_unidades",
        required=False,
        formatter=lambda x: str(x) if x else None
    ),
    DadosObraField(
        label="ÁREA TOTAL",
        key="area_total",
        required=False,
        formatter=lambda x: f"{x} m²" if x else None
    ),
    DadosObraField(
        label="RESPONSÁVEL TÉCNICO",
        key="responsavel_tecnico",
        required=False
    ),
    DadosObraField(
        label="CREA",
        key="crea",
        required=False
    ),
    DadosObraField(
        label="DATA",
        key="data",
        required=False
    ),
]


def format_dados_obra_section(master_data: Dict[str, Any]) -> str:
    """Generate formatted DADOS DA OBRA section text following schema.
    
    Args:
        master_data: JSON mestre with 'obra' and 'carimbo' fields
        
    Returns:
        Formatted text for DADOS DA OBRA section (without title)
    """
    obra = master_data.get("obra", {})
    carimbo = obra.get("carimbo", {})
    
    lines = []
    
    for field in DADOS_OBRA_SCHEMA:
        # Try to get value from obra, then from carimbo as fallback
        value = obra.get(field.key)
        if value is None:
            value = carimbo.get(field.key)
        
        # Apply formatter if provided
        if value is not None and field.formatter:
            try:
                value = field.formatter(value)
            except Exception:
                pass  # Keep original value if formatter fails
        
        # Handle missing values
        if value is None or (isinstance(value, str) and not value.strip()):
            if field.required:
                value = "Não informado"
            else:
                # Optional field without value - skip
                continue
        
        # Format line: "LABEL: value"
        line = f"{field.label}: {value}"
        lines.append(line)
    
    return "\n\n".join(lines)


def validate_dados_obra_schema():
    """Validate that schema is properly defined."""
    assert len(DADOS_OBRA_SCHEMA) > 0, "Schema must have at least one field"
    
    labels = [f.label for f in DADOS_OBRA_SCHEMA]
    assert len(labels) == len(set(labels)), "Duplicate labels in schema"
    
    keys = [f.key for f in DADOS_OBRA_SCHEMA]
    assert len(keys) == len(set(keys)), "Duplicate keys in schema"
    
    return True
