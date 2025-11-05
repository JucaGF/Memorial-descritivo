"""Estilos e formatação para DOCX."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


def setup_styles(doc: Document):
    """Configura estilos do documento.
    
    Args:
        doc: Documento python-docx
    """
    
    # Estilo: Título 1 (seções principais: 1, 2, 3, ...)
    try:
        style_h1 = doc.styles['Heading 1']
    except KeyError:
        style_h1 = doc.styles.add_style('Heading 1', WD_STYLE_TYPE.PARAGRAPH)
    
    style_h1.font.name = 'Arial'
    style_h1.font.size = Pt(14)
    style_h1.font.bold = True
    style_h1.font.color.rgb = RGBColor(0, 0, 0)
    style_h1.paragraph_format.space_before = Pt(18)
    style_h1.paragraph_format.space_after = Pt(12)
    
    # Estilo: Título 2 (subseções: 4.1, 4.2, ...)
    try:
        style_h2 = doc.styles['Heading 2']
    except KeyError:
        style_h2 = doc.styles.add_style('Heading 2', WD_STYLE_TYPE.PARAGRAPH)
    
    style_h2.font.name = 'Arial'
    style_h2.font.size = Pt(12)
    style_h2.font.bold = True
    style_h2.font.color.rgb = RGBColor(0, 0, 0)
    style_h2.paragraph_format.space_before = Pt(14)
    style_h2.paragraph_format.space_after = Pt(10)
    
    # Estilo: Corpo
    try:
        style_body = doc.styles['Normal']
    except KeyError:
        style_body = doc.styles.add_style('Normal', WD_STYLE_TYPE.PARAGRAPH)
    
    style_body.font.name = 'Arial'
    style_body.font.size = Pt(11)
    style_body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style_body.paragraph_format.space_after = Pt(6)
    style_body.paragraph_format.line_spacing = 1.15
    
    # Estilo: Lista
    try:
        style_list = doc.styles['List Bullet']
    except KeyError:
        style_list = doc.styles.add_style('List Bullet', WD_STYLE_TYPE.PARAGRAPH)
    
    style_list.font.name = 'Arial'
    style_list.font.size = Pt(11)
    style_list.paragraph_format.left_indent = Inches(0.25)
    style_list.paragraph_format.space_after = Pt(4)


def add_cover_page(doc: Document, logo_path: str, project_data: dict):
    """Adiciona capa ao documento.
    
    Args:
        doc: Documento python-docx
        logo_path: Caminho para logo TecPred
        project_data: Dados do projeto (empreendimento, data, etc.)
    """
    from pathlib import Path
    
    # Logo TecPred (centralizado, topo)
    if logo_path and Path(logo_path).exists():
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(logo_path, width=Inches(3.0))
    
    # Espaço
    doc.add_paragraph()
    
    # Título principal
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("MEMORIAL DESCRITIVO\n")
    run.font.name = 'Arial'
    run.font.size = Pt(18)
    run.font.bold = True
    
    run = title.add_run("SISTEMA DE TELECOMUNICAÇÕES")
    run.font.name = 'Arial'
    run.font.size = Pt(18)
    run.font.bold = True
    
    doc.add_paragraph()
    
    # Nome do empreendimento
    empreendimento = project_data.get("empreendimento", "")
    if empreendimento:
        emp_para = doc.add_paragraph()
        emp_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = emp_para.add_run(empreendimento.upper())
        run.font.name = 'Arial'
        run.font.size = Pt(16)
        run.font.bold = True
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Dados da obra (centralizado)
    construtora = project_data.get("construtora", "")
    if construtora:
        const_para = doc.add_paragraph()
        const_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = const_para.add_run(f"Construtora: {construtora}")
        run.font.name = 'Arial'
        run.font.size = Pt(12)
    
    endereco = project_data.get("endereco", "")
    if endereco:
        end_para = doc.add_paragraph()
        end_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = end_para.add_run(endereco)
        run.font.name = 'Arial'
        run.font.size = Pt(11)
    
    # Espaço para rodapé
    for _ in range(5):
        doc.add_paragraph()
    
    # Data e revisão (rodapé da capa)
    carimbo = project_data.get("carimbo", {})
    data = carimbo.get("data", "")
    revisao = carimbo.get("revisao", "")
    
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if data:
        run = footer_para.add_run(f"Data: {data}")
        run.font.name = 'Arial'
        run.font.size = Pt(10)
    
    if revisao:
        footer_para.add_run("  |  ")
        run = footer_para.add_run(f"Revisão: {revisao}")
        run.font.name = 'Arial'
        run.font.size = Pt(10)
    
    # Quebra de página
    doc.add_page_break()


def add_section_heading(doc: Document, number: str, title: str, level: int = 1):
    """Adiciona título de seção.
    
    Args:
        doc: Documento
        number: Número da seção (ex: "1", "4.1")
        title: Título da seção
        level: Nível (1=Heading 1, 2=Heading 2)
    """
    style = 'Heading 1' if level == 1 else 'Heading 2'
    heading = doc.add_paragraph(style=style)
    run = heading.add_run(f"{number}. {title}")
    return heading


def add_body_text(doc: Document, text: str):
    """Adiciona texto de corpo.
    
    Args:
        doc: Documento
        text: Texto a adicionar
    """
    if not text or not text.strip():
        return
    
    # Split por parágrafos
    paragraphs = text.split("\n\n")
    
    for para_text in paragraphs:
        para_text = para_text.strip()
        if not para_text:
            continue
        
        # Verifica se é item de lista (começa com -, *, •, ou número)
        if para_text.startswith(("- ", "* ", "• ")) or (len(para_text) > 2 and para_text[0].isdigit() and para_text[1] in ".)-"):
            # Lista
            para = doc.add_paragraph(para_text, style='List Bullet')
        else:
            # Corpo normal
            para = doc.add_paragraph(para_text, style='Normal')


def format_decimal(value: float) -> str:
    """Formata número com vírgula decimal (PT-BR).
    
    Args:
        value: Valor numérico
        
    Returns:
        String formatada
    """
    return f"{value:.2f}".replace(".", ",")






