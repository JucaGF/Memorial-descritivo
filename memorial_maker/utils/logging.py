"""Configuração de logging."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    verbose: bool = False
) -> logging.Logger:
    """Configura logging com Rich."""
    
    # Ajusta nível se verbose
    if verbose:
        level = logging.DEBUG
    
    # Handler console com Rich
    console = Console()
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=verbose,
    )
    console_handler.setLevel(level)
    
    # Handler arquivo (se fornecido)
    handlers = [console_handler]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        handlers.append(file_handler)
    
    # Configura root logger
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )
    
    # Silencia logs verbosos de bibliotecas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = logging.getLogger("memorial_maker")
    logger.setLevel(level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Retorna logger para um módulo específico."""
    return logging.getLogger(f"memorial_maker.{name}")






