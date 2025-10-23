"""
FastAPI Main Application - Memorial Automator API
Entry point for the memorial generation system.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
import os
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import get_settings, ensure_directories
from app.models.schemas import (
    GenerateMemorialResponse,
    ErrorResponse,
    HealthCheckResponse,
    StructuredProjectData
)
from app.services.pdf_extractor import PDFExtractor
from app.services.document_parser import DocumentParser
from app.services.agent_service import AgentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings and create directories
settings = get_settings()
ensure_directories()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de automação para criação de memoriais descritivos a partir de projetos em PDF"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - Serve the web interface.
    """
    static_path = Path(__file__).parent.parent / "static" / "index.html"
    if static_path.exists():
        return FileResponse(static_path)
    else:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Memorial Automator</title></head>
                <body>
                    <h1>Memorial Automator API</h1>
                    <p>Interface web não encontrada. Acesse <a href="/docs">/docs</a> para a documentação da API.</p>
                </body>
            </html>
            """,
            status_code=200
        )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version
    )


@app.post(
    f"{settings.api_prefix}/generate_memorial",
    response_model=GenerateMemorialResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_memorial(
    file: UploadFile = File(..., description="PDF do projeto de engenharia/arquitetura"),
    client_id: str = Form("default", description="ID do cliente para template específico"),
    include_images: bool = Form(False, description="Incluir análise de imagens"),
    custom_instructions: Optional[str] = Form(None, description="Instruções customizadas adicionais")
):
    """
    Generate a memorial descritivo from a project PDF.
    
    This endpoint orchestrates the complete pipeline:
    1. Upload and save PDF
    2. Extract data from PDF
    3. Structure data using AI
    4. Generate draft using Writer Agent
    5. Review and finalize using Reviewer Agent
    6. Return final memorial
    """
    start_time = time.time()
    temp_file_path = None
    warnings = []
    
    try:
        logger.info(f"Starting memorial generation request for client: {client_id}")
        
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size} bytes"
            )
        
        # Save file temporarily
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_file_path = Path(settings.upload_dir) / temp_filename
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved temporary file: {temp_file_path}")
        
        # Step 1: Extract data from PDF
        logger.info("Step 1/5: Extracting data from PDF...")
        pdf_extractor = PDFExtractor()
        raw_data = pdf_extractor.extract(str(temp_file_path), extract_images=include_images)
        pages_processed = raw_data.get("pages", 0)
        
        if pages_processed > settings.max_pages_per_pdf:
            warnings.append(f"PDF has {pages_processed} pages, which exceeds recommended limit")
        
        # Step 2: Structure data using AI
        logger.info("Step 2/5: Structuring data with AI...")
        document_parser = DocumentParser()
        structured_data = document_parser.structure_data(raw_data)
        
        # Step 3: Load context files
        logger.info("Step 3/5: Loading context files (ABNT rules and client template)...")
        agent_service = AgentService()
        abnt_rules, client_template = agent_service.load_context_files(client_id)
        
        # Step 4: Run Writer Agent
        logger.info("Step 4/5: Running Writer Agent to generate draft...")
        draft_memorial = agent_service.run_writer_agent(
            structured_data=structured_data,
            abnt_rules=abnt_rules,
            client_template=client_template,
            custom_instructions=custom_instructions
        )
        
        # Step 5: Run Reviewer Agent
        logger.info("Step 5/5: Running Reviewer Agent to review and finalize...")
        final_memorial = agent_service.run_reviewer_agent(
            draft_memorial=draft_memorial,
            structured_data=structured_data,
            abnt_rules=abnt_rules,
            client_template=client_template
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        logger.info(f"Memorial generation completed successfully in {processing_time:.2f} seconds")
        
        # Return response
        return GenerateMemorialResponse(
            memorial_text=final_memorial,
            structured_data=structured_data,
            processing_time_seconds=round(processing_time, 2),
            pages_processed=pages_processed,
            warnings=warnings
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error generating memorial: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate memorial: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Global HTTP exception handler.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=str(exc.status_code)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler for unexpected errors.
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected error occurred",
            error_code="500"
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

