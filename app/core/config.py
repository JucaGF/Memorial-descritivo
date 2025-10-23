"""
Configuration management for the application.
Handles environment variables, API keys, and application settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application Settings
    app_name: str = "Memorial Automator"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API Settings
    api_prefix: str = "/api/v1"
    allowed_origins: list = ["*"]
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"  # Modelo multimodal para análise
    openai_writer_model: str = "gpt-4-turbo"  # Modelo para redação
    openai_reviewer_model: str = "gpt-4-turbo"  # Modelo para revisão
    
    # Temperature settings for different agents
    writer_temperature: float = 0.7
    parser_temperature: float = 0.3
    reviewer_temperature: float = 0.2
    
    # File Upload Settings
    upload_dir: str = "temp_uploads"
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: list = [".pdf"]
    
    # Context Files
    context_files_dir: str = "context_files"
    abnt_rules_file: str = "abnt_rules.txt"
    client_template_file: str = "client_template.txt"
    
    # Processing Settings
    max_pages_per_pdf: int = 200
    extraction_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


def ensure_directories():
    """
    Ensure required directories exist.
    """
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.context_files_dir, exist_ok=True)

