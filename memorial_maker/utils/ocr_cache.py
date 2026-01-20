"""OCR cache management utilities."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger

logger = get_logger("utils.ocr_cache")


def get_cache_key(pdf_bytes: bytes, page_number: int, config_version: str) -> str:
    """Generate cache key for a PDF page.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        page_number: Page number (0-indexed)
        config_version: OCR configuration version
        
    Returns:
        SHA256 hash string as cache key
    """
    content = pdf_bytes + str(page_number).encode() + config_version.encode()
    return hashlib.sha256(content).hexdigest()


def get_cache_path(cache_key: str) -> Path:
    """Get file path for a cache key.
    
    Args:
        cache_key: Cache key (hash string)
        
    Returns:
        Path to cache file
    """
    cache_dir = settings.ocr_cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{cache_key}.json"


def load_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Load OCR result from cache.
    
    Args:
        cache_key: Cache key
        
    Returns:
        Cached result dict or None if not found
    """
    cache_path = get_cache_path(cache_key)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading cache {cache_key}: {e}")
        return None


def save_to_cache(cache_key: str, result: Dict[str, Any]) -> None:
    """Save OCR result to cache.
    
    Args:
        cache_key: Cache key
        result: Result dict to cache
    """
    cache_path = get_cache_path(cache_key)
    
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.debug(f"Cached OCR result: {cache_key[:16]}...")
    except Exception as e:
        logger.warning(f"Error saving cache {cache_key}: {e}")


def clear_cache() -> None:
    """Clear all cached OCR results."""
    cache_dir = settings.ocr_cache_dir
    
    if cache_dir.exists():
        for cache_file in cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info(f"Cleared OCR cache: {len(list(cache_dir.glob('*.json')))} files")
    else:
        logger.info("OCR cache directory does not exist")
