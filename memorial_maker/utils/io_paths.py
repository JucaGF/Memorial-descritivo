"""Gerenciamento de caminhos e I/O."""

from pathlib import Path
from typing import List, Optional
import shutil


def ensure_dir(path: Path) -> Path:
    """Garante que um diretório existe."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_session_dir(base_dir: Path, session_id: str) -> Path:
    """Cria e retorna diretório de sessão."""
    session_dir = base_dir / session_id
    ensure_dir(session_dir)
    return session_dir


def setup_output_dirs(out_dir: Path) -> dict:
    """Cria estrutura de diretórios de saída."""
    dirs = {
        "extraido": ensure_dir(out_dir / "extraido"),
        "memorial": ensure_dir(out_dir / "memorial"),
        "logs": ensure_dir(out_dir / "logs"),
    }
    return dirs


def list_pdfs(pdf_dir: Path) -> List[Path]:
    """Lista todos os PDFs em um diretório."""
    return sorted(pdf_dir.glob("*.pdf")) + sorted(pdf_dir.glob("*.PDF"))


def list_models(models_dir: Path) -> List[Path]:
    """Lista memoriais-modelo (DOCX preferível, DOC como fallback)."""
    # Prioriza .docx, ignora .doc se existir .docx correspondente
    docx_files = list(models_dir.glob("*.docx")) + list(models_dir.glob("*.DOCX"))
    doc_files = list(models_dir.glob("*.doc")) + list(models_dir.glob("*.DOC"))
    
    # Remove .doc se existir .docx correspondente
    docx_stems = {f.stem for f in docx_files}
    doc_files = [f for f in doc_files if f.stem not in docx_stems]
    
    return sorted(docx_files + doc_files)


def clean_session(session_dir: Path):
    """Remove diretório de sessão temporário."""
    if session_dir.exists():
        shutil.rmtree(session_dir)


def get_project_name(pdf_paths: List[Path]) -> str:
    """Extrai nome do projeto dos arquivos PDF."""
    if not pdf_paths:
        return "PROJETO"
    
    # Tenta extrair prefixo comum
    first = pdf_paths[0].stem
    parts = first.split("_")
    if len(parts) >= 2:
        return parts[0]  # Ex: MGAMAK
    return first.split()[0] if " " in first else "PROJETO"





