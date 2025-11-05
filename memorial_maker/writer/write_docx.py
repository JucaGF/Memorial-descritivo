"""Montagem do documento DOCX final."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from docx import Document

from memorial_maker.writer.docx_styles import (
    setup_styles,
    add_cover_page,
    add_section_heading,
    add_body_text,
)
from memorial_maker.utils.logging import get_logger

logger = get_logger("writer.docx")


class MemorialWriter:
    """Escritor de Memorial em DOCX."""

    def __init__(self, logo_path: Optional[Path] = None):
        """Inicializa writer.
        
        Args:
            logo_path: Caminho para logo TecPred
        """
        self.logo_path = str(logo_path) if logo_path else None
        self.doc = Document()
        setup_styles(self.doc)

    def write_memorial(
        self,
        sections: Dict[str, str],
        master_data: Dict,
        output_path: Path,
    ):
        """Escreve memorial completo.
        
        Args:
            sections: Dicionário {section_id: content}
            master_data: Dados consolidados (JSON mestre)
            output_path: Caminho de saída do DOCX
        """
        logger.info(f"Escrevendo memorial: {output_path}")
        
        # Capa
        project_data = {
            "empreendimento": master_data.get("obra", {}).get("empreendimento", ""),
            "construtora": master_data.get("obra", {}).get("construtora", ""),
            "endereco": master_data.get("obra", {}).get("endereco", ""),
            "carimbo": master_data.get("obra", {}).get("carimbo", {}),
        }
        add_cover_page(self.doc, self.logo_path, project_data)
        
        # Seções na ordem
        self._write_section_1(sections.get("s1_introducao", ""))
        self._write_section_2(sections.get("s2_dados_obra", ""))
        self._write_section_3(sections.get("s3_normas", ""))
        self._write_section_4(sections)
        self._write_section_5(sections.get("s5_sala_monitoramento", ""))
        self._write_section_6(sections.get("s6_passivos_ativos", ""))
        self._write_section_7(sections.get("s7_testes_aceitacao", ""))
        
        # Salva
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output_path))
        logger.info(f"Memorial salvo: {output_path}")

    def _write_section_1(self, content: str):
        """Seção 1: Introdução."""
        add_section_heading(self.doc, "1", "INTRODUÇÃO", level=1)
        add_body_text(self.doc, content)

    def _write_section_2(self, content: str):
        """Seção 2: Dados da Obra."""
        add_section_heading(self.doc, "2", "DADOS DA OBRA", level=1)
        add_body_text(self.doc, content)

    def _write_section_3(self, content: str):
        """Seção 3: Normas Técnicas."""
        add_section_heading(self.doc, "3", "NORMAS TÉCNICAS", level=1)
        add_body_text(self.doc, content)

    def _write_section_4(self, sections: Dict[str, str]):
        """Seção 4: Serviços Contemplados (com subseções)."""
        add_section_heading(self.doc, "4", "SERVIÇOS CONTEMPLADOS", level=1)
        
        # Introdução da seção 4
        intro = sections.get("s4_servicos", "")
        add_body_text(self.doc, intro)
        
        # Subseções
        subsections = [
            ("4.1", "SERVIÇO DE VOZ", "s4_1_voz"),
            ("4.2", "SERVIÇO DE DADOS", "s4_2_dados"),
            ("4.3", "SERVIÇO DE VÍDEO", "s4_3_video"),
            ("4.4", "SERVIÇO DE INTERCOMUNICAÇÃO", "s4_4_intercom"),
            ("4.5", "SERVIÇO DE MONITORAMENTO", "s4_5_monitoramento"),
        ]
        
        for number, title, section_id in subsections:
            content = sections.get(section_id, "")
            if content:
                add_section_heading(self.doc, number, title, level=2)
                add_body_text(self.doc, content)

    def _write_section_5(self, content: str):
        """Seção 5: Sala de Monitoramento."""
        add_section_heading(self.doc, "5", "SALA DE MONITORAMENTO (ER/EF)", level=1)
        add_body_text(self.doc, content)

    def _write_section_6(self, content: str):
        """Seção 6: Elementos Passivos e Ativos."""
        add_section_heading(self.doc, "6", "ELEMENTOS PASSIVOS E ATIVOS DA REDE", level=1)
        add_body_text(self.doc, content)

    def _write_section_7(self, content: str):
        """Seção 7: Testes e Aceitação."""
        add_section_heading(self.doc, "7", "TESTES E ACEITAÇÃO", level=1)
        add_body_text(self.doc, content)


def write_memorial_docx(
    sections: Dict[str, str],
    master_data: Dict,
    output_dir: Path,
    logo_path: Optional[Path] = None,
    project_name: str = "PROJETO",
) -> Path:
    """Função conveniente para escrever memorial.
    
    Args:
        sections: Seções geradas
        master_data: Dados consolidados
        output_dir: Diretório de saída
        logo_path: Caminho para logo
        project_name: Nome do projeto
        
    Returns:
        Caminho do arquivo gerado
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"MEMORIAL_{project_name}_{timestamp}.docx"
    output_path = output_dir / filename
    
    writer = MemorialWriter(logo_path)
    writer.write_memorial(sections, master_data, output_path)
    
    return output_path






