"""
Pydantic schemas for request and response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class StructuredProjectData(BaseModel):
    """
    Structured data extracted from the project PDF.
    """
    project_name: Optional[str] = Field(None, description="Nome do projeto")
    client_name: Optional[str] = Field(None, description="Nome do cliente")
    area_total_m2: Optional[float] = Field(None, description="Área total em m²")
    localizacao_obra: Optional[str] = Field(None, description="Localização da obra")
    lista_materiais: Optional[List[str]] = Field(default_factory=list, description="Lista de materiais")
    especificacoes_tecnicas: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Especificações técnicas")
    tipo_construcao: Optional[str] = Field(None, description="Tipo de construção")
    responsavel_tecnico: Optional[str] = Field(None, description="Responsável técnico")
    data_projeto: Optional[str] = Field(None, description="Data do projeto")
    numero_pavimentos: Optional[int] = Field(None, description="Número de pavimentos")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados brutos adicionais")


class GenerateMemorialRequest(BaseModel):
    """
    Request model for memorial generation.
    """
    client_id: Optional[str] = Field("default", description="ID do cliente para template específico")
    include_images: bool = Field(False, description="Incluir análise de imagens")
    custom_instructions: Optional[str] = Field(None, description="Instruções customizadas adicionais")


class GenerateMemorialResponse(BaseModel):
    """
    Response model for memorial generation.
    """
    memorial_text: str = Field(..., description="Texto do memorial descritivo gerado")
    structured_data: Optional[StructuredProjectData] = Field(None, description="Dados estruturados extraídos")
    processing_time_seconds: float = Field(..., description="Tempo de processamento em segundos")
    pages_processed: int = Field(..., description="Número de páginas processadas")
    warnings: List[str] = Field(default_factory=list, description="Avisos durante o processamento")


class ErrorResponse(BaseModel):
    """
    Error response model.
    """
    detail: str = Field(..., description="Detalhes do erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")


class HealthCheckResponse(BaseModel):
    """
    Health check response.
    """
    status: str = Field(..., description="Status da aplicação")
    version: str = Field(..., description="Versão da aplicação")
    timestamp: datetime = Field(default_factory=datetime.now)


class PDFExtractionResult(BaseModel):
    """
    Result from PDF extraction.
    """
    text: str = Field(..., description="Texto extraído do PDF")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Imagens extraídas")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados do PDF")
    pages: int = Field(..., description="Número de páginas")

