"""Optimized PDF extraction with hybrid text-first extraction, parallel OCR, and caching."""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
import json
import os
import multiprocessing

try:
    from unstructured.partition.pdf import partition_pdf
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    partition_pdf = None

from memorial_maker.config import settings
from memorial_maker.utils.logging import get_logger
from memorial_maker.utils.ocr_cache import (
    get_cache_key,
    load_from_cache,
    save_to_cache,
)

logger = get_logger("extract.optimized")


def extract_pdf_hybrid_wrapper(pdf_path: Path, output_dir: Path, log_queue: Optional[multiprocessing.Queue] = None) -> Dict[str, Any]:
    """Wrapper para extract_pdf_hybrid que captura logs em uma fila.
    
    Esta função é necessária porque spawn cria processos novos que não compartilham stdout.
    Usamos uma Queue para enviar mensagens de log de volta ao processo pai.
    """
    def log_message(msg: str):
        """Envia mensagem para a fila de log E imprime localmente."""
        print(msg)  # Tenta print local (pode não aparecer com spawn)
        if log_queue:
            try:
                log_queue.put(msg)
            except:
                pass  # Ignora erros de queue
    
    try:
        log_message(f"🔄 Worker iniciado para: {pdf_path.name}")
        result = extract_pdf_hybrid(pdf_path, output_dir)
        log_message(f"✅ Worker completou: {pdf_path.name}")
        return result
    except Exception as e:
        log_message(f"❌ Worker falhou: {pdf_path.name} - {e}")
        raise


def is_text_valid(text: str, min_length: int = 50) -> bool:
    """Check if extracted text is valid (not empty or too short).
    
    Args:
        text: Extracted text
        min_length: Minimum valid text length
        
    Returns:
        True if text is valid, False otherwise
    """
    if not text or len(text.strip()) < min_length:
        return False
    
    # Check if text is mostly whitespace or special characters
    non_whitespace = len([c for c in text if c.isalnum()])
    if non_whitespace < min_length * 0.3:  # At least 30% alphanumeric
        return False
    
    return True


def extract_page_native_text(pdf_path: Path, page_number: int) -> Tuple[str, bool]:
    """Attempt native text extraction from a PDF page.
    
    Args:
        pdf_path: Path to PDF file
        page_number: Page number (0-indexed)
        
    Returns:
        Tuple of (extracted_text, success)
    """
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError("Unstructured não está instalado. Esta dependência é obrigatória.")
    
    try:
        # Extract only the specific page
        elements = partition_pdf(
            filename=str(pdf_path),
            strategy="fast",  # Fast strategy for native text
            page_numbers=[page_number],
            languages=["por"],
        )
        
        # Combine all text elements
        text_parts = []
        for element in elements:
            text = str(element).strip()
            if text:
                text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        return full_text, True
        
    except Exception as e:
        logger.warning(f"Error extracting native text from page {page_number} of {pdf_path.name}: {e}")
        return "", False


def extract_page_with_ocr(
    pdf_path: Path,
    page_number: int,
    pdf_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """Extract text from a PDF page using OCR (with caching).
    
    Args:
        pdf_path: Path to PDF file
        page_number: Page number (0-indexed)
        pdf_bytes: Raw PDF bytes (for cache key generation)
        
    Returns:
        Dict with extracted text and metadata
    """
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError("Unstructured não está instalado. Esta dependência é obrigatória para OCR.")
    
    # Load PDF bytes if not provided
    if pdf_bytes is None:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    
    # Check cache
    cache_key = get_cache_key(pdf_bytes, page_number, settings.ocr_config_version)
    cached_result = load_from_cache(cache_key)
    
    if cached_result:
        logger.debug(f"Cache hit for page {page_number} of {pdf_path.name}")
        return {
            **cached_result,
            "from_cache": True,
        }
    
    # Run OCR
    start_time = time.time()
    try:
        elements = partition_pdf(
            filename=str(pdf_path),
            strategy="hi_res",  # High-res strategy for OCR
            page_numbers=[page_number],
            languages=["por"],
        )
        
        # Combine all text elements
        text_parts = []
        for element in elements:
            text = str(element).strip()
            if text:
                text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        ocr_time = time.time() - start_time
        
        result = {
            "text": full_text,
            "page_number": page_number,
            "ocr_time": ocr_time,
            "from_cache": False,
        }
        
        # Save to cache
        save_to_cache(cache_key, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error during OCR for page {page_number} of {pdf_path.name}: {e}")
        return {
            "text": "",
            "page_number": page_number,
            "ocr_time": 0.0,
            "from_cache": False,
            "error": str(e),
        }


def extract_pdf_hybrid(
    pdf_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    """Extract content from PDF using hybrid approach (text-first, OCR fallback).
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory for output files
        
    Returns:
        Dict with extracted data and metrics
    """
    logger.info(f"Extracting with hybrid approach: {pdf_path.name}")
    
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError("Unstructured não está instalado. Esta dependência é obrigatória.")

    # Load PDF bytes for cache key generation
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    # Get total page count (quick check)
    try:
        # Extract first page to get metadata
        sample_elements = partition_pdf(
            filename=str(pdf_path),
            strategy="fast",
            page_numbers=[0],
            languages=["por"],
        )
        # Estimate page count from filename or use a default
        # Note: unstructured doesn't directly give page count, so we'll process pages incrementally
        total_pages = 1  # Will be determined during processing
    except Exception as e:
        logger.error(f"Error getting page count for {pdf_path.name}: {e}")
        raise e
    
    # Try to determine page count by attempting to extract pages until failure
    max_pages = 1000  # Safety limit
    page_results = []
    pages_processed = 0
    text_extracted_pages = 0
    ocr_pages = 0
    total_ocr_time = 0.0
    cache_hits = 0
    
    # Process pages sequentially to determine count and extraction method
    for page_num in range(max_pages):
        try:
            # Try native text extraction first
            native_text, success = extract_page_native_text(pdf_path, page_num)
            
            if success and is_text_valid(native_text):
                # Native text is valid
                page_results.append({
                    "page_number": page_num,
                    "text": native_text,
                    "extraction_method": "native",
                })
                text_extracted_pages += 1
                pages_processed += 1
            else:
                # Need OCR
                ocr_result = extract_page_with_ocr(pdf_path, page_num, pdf_bytes)
                page_results.append({
                    "page_number": page_num,
                    "text": ocr_result.get("text", ""),
                    "extraction_method": "ocr",
                    "ocr_time": ocr_result.get("ocr_time", 0.0),
                    "from_cache": ocr_result.get("from_cache", False),
                })
                ocr_pages += 1
                total_ocr_time += ocr_result.get("ocr_time", 0.0)
                if ocr_result.get("from_cache"):
                    cache_hits += 1
                pages_processed += 1
                
        except Exception as e:
            # Likely reached end of document
            logger.debug(f"Stopped at page {page_num}: {e}")
            break
    
    # Combine all page texts
    all_text_elements = []
    all_tables = []
    
    for page_result in page_results:
        page_text = page_result.get("text", "")
        if page_text:
            all_text_elements.append({
                "type": "text",
                "text": page_text,
                "metadata": {
                    "page_number": page_result.get("page_number"),
                    "extraction_method": page_result.get("extraction_method"),
                },
            })
    
    # Extract carimbo from full text
    from memorial_maker.extract.unstructured_extract import extract_carimbo_from_text
    full_text = "\n".join([item["text"] for item in all_text_elements])
    carimbo_info = extract_carimbo_from_text(full_text)
    
    # Build result
    result = {
        "filename": pdf_path.name,
        "total_elements": len(all_text_elements),
        "text": all_text_elements,
        "tables": all_tables,
        "metadata": {
            "total_pages": pages_processed,
            "text_extracted_pages": text_extracted_pages,
            "ocr_pages": ocr_pages,
            "cache_hits": cache_hits,
            "total_ocr_time": total_ocr_time,
        },
        "carimbo": carimbo_info,
        "metrics": {
            "total_pages": pages_processed,
            "text_extracted_pages": text_extracted_pages,
            "ocr_pages": ocr_pages,
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / ocr_pages if ocr_pages > 0 else 0.0,
            "total_ocr_time": total_ocr_time,
        },
    }
    
    # Save JSON
    output_json = output_dir / f"{pdf_path.stem}_optimized.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(
        f"Extracted {pages_processed} pages: {text_extracted_pages} native, "
        f"{ocr_pages} OCR ({(cache_hits/ocr_pages*100) if ocr_pages > 0 else 0:.1f}% cache hits)"
    )
    
    return result


def extract_all_pdfs_optimized(
    pdf_dir: Path,
    output_dir: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[Dict[str, Any]]:
    """Extract content from all PDFs using optimized parallel extraction.
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory for output files
        progress_callback: Optional callback for tracking progress (current, total)
        
    Returns:
        List of extraction results
    """
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDFs in {pdf_dir}")
    print(f"🔍 Encontrados {len(pdf_files)} PDFs em {pdf_dir}")  # Direct print for Streamlit
    
    if not pdf_files:
        print("⚠️ Nenhum PDF encontrado!")
        return []
    
    results = []
    
    # SOLUÇÃO DEFINITIVA: Usar 'spawn' em vez de 'fork' para ProcessPoolExecutor
    # Fork() causa deadlock com bibliotecas que usam threads (PyTorch, OpenCV, etc)
    # Spawn cria processos completamente novos, evitando herança de estado perigoso
    
    # Determine number of workers
    # Use CPU count but cap at 4 to balance speed and memory usage
    max_workers = min(os.cpu_count() or 2, 4)
    logger.info(f"Starting parallel extraction with {max_workers} workers using spawn context")
    print(f"⚙️ Iniciando extração paralela com {max_workers} workers (modo spawn - seguro)")
    
    start_time = time.time()
    
    # Criar contexto de multiprocessing com spawn (não fork)
    mp_context = multiprocessing.get_context('spawn')
    
    # Criar Manager para Queue compartilhada (para logs dos workers)
    manager = multiprocessing.Manager()
    log_queue = manager.Queue()
    
    # Thread para ler logs da queue em background
    import threading
    stop_log_thread = threading.Event()
    
    def log_reader():
        """Lê mensagens da fila de log e imprime."""
        while not stop_log_thread.is_set():
            try:
                msg = log_queue.get(timeout=0.5)
                print(msg)
            except:
                continue  # Timeout ou fila vazia
    
    log_thread = threading.Thread(target=log_reader, daemon=True)
    log_thread.start()
    
    # Use ProcessPoolExecutor com contexto spawn para paralelismo seguro
    with ProcessPoolExecutor(max_workers=max_workers, mp_context=mp_context) as executor:
        # Submit all tasks com a queue de log
        future_to_file = {
            executor.submit(extract_pdf_hybrid_wrapper, pdf_path, output_dir, log_queue): pdf_path
            for pdf_path in pdf_files
        }
        
        # Process results as they complete
        completed_count = 0
        total_files = len(pdf_files)
        
        # TIMEOUT: Se um worker travar, detectamos aqui
        TIMEOUT_PER_PDF = 300  # 5 minutos por PDF (bem generoso)
        
        for future in as_completed(future_to_file, timeout=TIMEOUT_PER_PDF * len(pdf_files)):
            pdf_path = future_to_file[future]
            try:
                # Timeout individual por future
                result = future.result(timeout=TIMEOUT_PER_PDF)
                results.append(result)
                logger.info(f"Completed extraction for: {pdf_path.name}")
                print(f"✅ Concluído: {pdf_path.name} ({completed_count + 1}/{total_files})")
            except TimeoutError:
                logger.error(f"TIMEOUT extracting {pdf_path.name} after {TIMEOUT_PER_PDF}s")
                print(f"⏱️ TIMEOUT: {pdf_path.name} travou após {TIMEOUT_PER_PDF}s")
                results.append({
                    "filename": pdf_path.name,
                    "error": f"Timeout after {TIMEOUT_PER_PDF}s",
                    "text": [],
                    "tables": [],
                    "metadata": {},
                    "carimbo": {}
                })
            except Exception as e:
                logger.error(f"Failed to extract {pdf_path.name}: {e}")
                print(f"❌ Erro ao extrair {pdf_path.name}: {e}")
                # Add a dummy error result so we don't lose track of the file
                results.append({
                    "filename": pdf_path.name,
                    "error": str(e),
                    "text": [],
                    "tables": [],
                    "metadata": {},
                    "carimbo": {}
                })
            
            completed_count += 1
            if progress_callback:
                try:
                    progress_callback(completed_count, total_files)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
                    print(f"⚠️ Erro no callback de progresso: {e}")
    
    # Para thread de logs
    stop_log_thread.set()
    log_thread.join(timeout=2)
    
    total_time = time.time() - start_time
    
    # Aggregate metrics
    total_pages = sum(r.get("metrics", {}).get("total_pages", 0) for r in results)
    total_text_pages = sum(r.get("metrics", {}).get("text_extracted_pages", 0) for r in results)
    total_ocr_pages = sum(r.get("metrics", {}).get("ocr_pages", 0) for r in results)
    total_cache_hits = sum(r.get("metrics", {}).get("cache_hits", 0) for r in results)
    total_ocr_time = sum(r.get("metrics", {}).get("total_ocr_time", 0.0) for r in results)
    
    logger.info(
        f"Total extraction ({total_time:.2f}s): {total_pages} pages ({total_text_pages} native, {total_ocr_pages} OCR), "
        f"{(total_cache_hits/total_ocr_pages*100) if total_ocr_pages > 0 else 0:.1f}% cache hits, "
        f"{total_ocr_time:.2f}s accumulated OCR time"
    )
    
    # Print summary for Streamlit
    print(f"\n📊 Extração concluída em {total_time:.2f}s:")
    print(f"   • {total_pages} páginas processadas")
    print(f"   • {total_text_pages} páginas com texto nativo")
    print(f"   • {total_ocr_pages} páginas com OCR")
    if total_ocr_pages > 0:
        print(f"   • {(total_cache_hits/total_ocr_pages*100):.1f}% cache hits")
        print(f"   • {total_ocr_time:.2f}s tempo total de OCR")
    
    # Save consolidated JSON
    consolidated_json = output_dir / "all_extractions_optimized.json"
    with open(consolidated_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Consolidated extraction saved: {consolidated_json}")
    print(f"💾 Extração salva em: {consolidated_json}")
    
    return results
