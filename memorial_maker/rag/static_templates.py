"""Helper module to load static templates for electrical memorial sections."""

from pathlib import Path
from typing import Optional


class StaticTemplateLoader:
    """Loads static text templates for electrical memorial sections."""
    
    def __init__(self, templates_dir: Path):
        """Initialize with templates directory.
        
        Args:
            templates_dir: Path to directory containing static templates
        """
        self.templates_dir = templates_dir
        self._cache = {}
    
    def load_template(self, template_name: str) -> Optional[str]:
        """Load a static template by name.
        
        Args:
            template_name: Name of template file (without .txt extension)
            
        Returns:
            Template content or None if not found
        """
        # Check cache first
        if template_name in self._cache:
            return self._cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.txt"
        
        if not template_path.exists():
            return None
        
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # Cache for future use
        self._cache[template_name] = content
        return content
    
    def has_template(self, template_name: str) -> bool:
        """Check if a static template exists.
        
        Args:
            template_name: Name of template file (without .txt extension)
            
        Returns:
            True if template exists, False otherwise
        """
        if template_name in self._cache:
            return True
        
        template_path = self.templates_dir / f"{template_name}.txt"
        return template_path.exists()


# Mapping of section IDs to static template names
STATIC_TEMPLATES = {
    # Sumário (static TOC)
    "s0_sumario": "s0_sumario",
    
    # Section 1 - Introdução (static)
    "s1_introducao": "s1_introducao",
    
    # Section 3 - Requisitos Gerais (static)
    "s3_requisitos_gerais": "s3_requisitos_gerais",
    "s3_1_disposicoes_gerais": "s3_1_disposicoes_gerais",
    
    # Section 4 - Visão Geral (intro is static)
    "s4_visao_geral": "s4_visao_geral_intro",
    "s4_6_medicao_energia": "s4_6_medicao_energia",
    
    # Add more mappings as templates are created
}

