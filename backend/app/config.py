"""
Configuration management for HackTheAgent
"""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "HackTheAgent Email Brain"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = base_dir / "data"
    vector_store_dir: Path = base_dir / "vector_store"
    
    # Email data
    emails_file: str = "emails.json"
    
    # Embedding settings
    embedding_provider: str = "sentence-transformers"  # or "watsonx", "openai"
    embedding_model: str = "all-MiniLM-L6-v2"  # Fast and efficient
    
    # Vector DB settings
    vector_db: str = "chroma"  # or "faiss"
    collection_name: str = "email_embeddings"
    
    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Search settings
    default_top_k: int = 5
    
    # LLM settings
    llm_provider: str = "watsonx"  # or "openai", "ollama"
    llm_model: str = "ibm/granite-13b-chat-v2"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 500
    
    # API Keys (optional, loaded from environment)
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: Optional[str] = "https://us-south.ml.cloud.ibm.com"
    openai_api_key: Optional[str] = None
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)