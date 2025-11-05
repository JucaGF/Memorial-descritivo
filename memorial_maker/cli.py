"""Interface CLI com Typer."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from memorial_maker.config import settings
from memorial_maker.utils.logging import setup_logging, get_logger
from memorial_maker.utils.io_paths import (
    setup_output_dirs,
    list_pdfs,
    list_models,
    get_project_name,
)
from memorial_maker.extract.unstructured_extract import extract_all_pdfs, extract_text_from_elements
from memorial_maker.normalize.canonical_map import ItemExtractor, normalize_all_items
from memorial_maker.normalize.consolidate import consolidate_and_export
from memorial_maker.rag.index_style import index_models
from memorial_maker.rag.generate_sections import SectionGenerator
from memorial_maker.writer.write_docx import write_memorial_docx

app = typer.Typer(
    name="memorial-make",
    help="Geração automática de Memorial Descritivo de Telecomunicações",
)
console = Console()


@app.command()
def generate(
    pdf_dir: Path = typer.Option(
        ...,
        "--pdf-dir",
        help="Diretório com PDFs de projeto",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    modelos_dir: Path = typer.Option(
        ...,
        "--modelos-dir",
        help="Diretório com memoriais-modelo (DOC/DOCX)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    logo: Optional[Path] = typer.Option(
        None,
        "--logo",
        help="Caminho para logo customizada (opcional, usa logo TecPred padrão)",
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
    out_dir: Path = typer.Option(
        Path("./out"),
        "--out-dir",
        help="Diretório de saída",
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        help="DPI para renderização de PDFs",
    ),
    llm_model: Optional[str] = typer.Option(
        None,
        "--llm-model",
        help="Modelo LLM (ex: gpt-4o)",
    ),
    parallel: bool = typer.Option(
        True,
        "--parallel/--sequential",
        help="Processar seções em paralelo",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Modo verbose",
    ),
):
    """Gera memorial descritivo a partir de PDFs de projeto."""
    
    # Setup logging
    log_dir = out_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(log_file=log_dir / "execution.log", verbose=verbose)
    logger = get_logger("cli")
    
    console.print("\n[bold cyan]Memorial Maker[/bold cyan] - Geração de Memorial Descritivo\n")
    
    # Atualiza settings
    if llm_model:
        settings.llm_model = llm_model
    settings.dpi = dpi
    settings.parallel_execution = parallel
    
    # Valida API key
    if not settings.openai_api_key:
        console.print("[bold red]Erro:[/bold red] OPENAI_API_KEY não configurada")
        raise typer.Exit(1)
    
    # Setup diretórios
    dirs = setup_output_dirs(out_dir)
    
    # Lista arquivos
    pdf_paths = list_pdfs(pdf_dir)
    model_paths = list_models(modelos_dir)
    
    if not pdf_paths:
        console.print(f"[bold red]Erro:[/bold red] Nenhum PDF encontrado em {pdf_dir}")
        raise typer.Exit(1)
    
    if not model_paths:
        console.print(f"[bold yellow]Aviso:[/bold yellow] Nenhum modelo encontrado em {modelos_dir}")
    
    console.print(f"📄 PDFs encontrados: {len(pdf_paths)}")
    console.print(f"📋 Modelos encontrados: {len(model_paths)}")
    
    project_name = get_project_name(pdf_paths)
    console.print(f"🏗️  Projeto: [bold]{project_name}[/bold]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # 1. Extração com Unstructured
        task = progress.add_task("Extraindo dados dos PDFs com Unstructured...", total=None)
        extractions = extract_all_pdfs(pdf_dir, dirs["extraido"])
        progress.update(task, completed=True)
        console.print("✅ Extração concluída\n")
        
        # 2. Normalização
        task = progress.add_task("Normalizando dados...", total=None)
        extractor = ItemExtractor()
        raw_items = []
        
        for extraction in extractions:
            # Extrai texto de todos os elementos
            full_text = extract_text_from_elements(extraction)
            
            # Extrai itens do texto
            items = extractor.extract_from_text(full_text, {
                "filename": extraction.get("filename", ""),
            })
            raw_items.extend(items)
            
            # Processa tabelas estruturadas
            for table in extraction.get("tables", []):
                table_text = table.get("text", "")
                items = extractor.extract_from_text(table_text, {
                    "filename": extraction.get("filename", ""),
                    "source": "table",
                })
                raw_items.extend(items)
        
        normalized_items = normalize_all_items(raw_items)
        progress.update(task, completed=True)
        console.print(f"✅ Normalizados {len(normalized_items)} itens\n")
        
        # 3. Consolidação
        task = progress.add_task("Consolidando e exportando CSVs...", total=None)
        master_data = consolidate_and_export(
            extractions,
            normalized_items,
            dirs["extraido"],
        )
        progress.update(task, completed=True)
        console.print("✅ Consolidação concluída\n")
        
        # 4. Indexação de estilo
        if model_paths:
            task = progress.add_task("Indexando memoriais-modelo...", total=None)
            style_indexer = index_models(modelos_dir)
            progress.update(task, completed=True)
            # Se indexação falhou, cria indexador vazio
            if style_indexer is None:
                console.print("[yellow]⚠️  Falha ao indexar modelos, usando indexador vazio[/yellow]\n")
                from memorial_maker.rag.index_style import StyleIndexer
                style_indexer = StyleIndexer()
            else:
                console.print("✅ Indexação de estilo concluída\n")
        else:
            console.print("[yellow]⚠️  Pulando indexação (sem modelos)[/yellow]\n")
            from memorial_maker.rag.index_style import StyleIndexer
            style_indexer = StyleIndexer()
        
        # 5. Geração de seções
        task = progress.add_task("Gerando seções com LLM...", total=None)
        prompts_dir = Path(__file__).parent / "rag" / "prompts"
        generator = SectionGenerator(style_indexer, prompts_dir)
        
        sections = generator.generate_all_sections(master_data, parallel=parallel)
        progress.update(task, completed=True)
        console.print(f"✅ Geradas {len(sections)} seções\n")
        
        # 6. Escrita DOCX
        task = progress.add_task("Escrevendo memorial DOCX...", total=None)
        
        # Usa logo padrão se não fornecida
        if logo is None:
            default_logo = Path(__file__).parent.parent / "assets" / "logo_tecpred.png"
            logo_to_use = default_logo if default_logo.exists() else None
        else:
            logo_to_use = logo
        
        output_path = write_memorial_docx(
            sections,
            master_data,
            dirs["memorial"],
            logo_path=logo_to_use,
            project_name=project_name,
        )
        progress.update(task, completed=True)
        console.print(f"✅ Memorial gerado: [bold green]{output_path}[/bold green]\n")
    
    console.print("[bold green]🎉 Processo concluído com sucesso![/bold green]")


@app.command()
def version():
    """Mostra versão do Memorial Maker."""
    from memorial_maker import __version__
    console.print(f"Memorial Maker v{__version__}")


if __name__ == "__main__":
    app()




