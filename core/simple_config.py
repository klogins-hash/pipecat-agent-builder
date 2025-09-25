"""Simplified configuration for MVP."""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class AIServiceConfig(BaseModel):
    """Configuration for AI services."""
    name: str
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    voice_id: Optional[str] = None


class KnowledgeSourceConfig(BaseModel):
    """Configuration for knowledge sources."""
    type: str  # "web", "document", "api"
    source: str
    processing_options: dict = {}


class DeploymentConfig(BaseModel):
    """Configuration for deployment."""
    platform: str = "pipecat-cloud"
    scaling_min: int = 1
    scaling_max: int = 5
    region: str = "us-west-2"


class AgentRequirements(BaseModel):
    """Agent requirements specification - simplified for MVP."""
    name: str
    description: str
    use_case: str
    channels: List[str] = ["web"]
    languages: List[str] = ["en"]
    personality: str = "helpful and professional"
    
    # AI Services (optional for MVP)
    stt_service: Optional[AIServiceConfig] = None
    llm_service: Optional[AIServiceConfig] = None
    tts_service: Optional[AIServiceConfig] = None
    
    # Knowledge and integrations (optional)
    knowledge_sources: List[KnowledgeSourceConfig] = []
    integrations: List[str] = []
    deployment: Optional[DeploymentConfig] = None


class Settings(BaseSettings):
    """Simplified application settings for MVP."""
    
    # Essential API Keys
    openai_api_key: Optional[str] = None
    deepgram_api_key: Optional[str] = None
    cartesia_api_key: Optional[str] = None
    
    # Vector Database
    chroma_persist_directory: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Application
    debug: bool = True  # Default to debug for MVP
    log_level: str = "INFO"
    
    # Paths
    docs_path: str = "/Users/franksimpson/CascadeProjects/docs-2"
    templates_path: str = "./templates"
    output_path: str = "./generated_agents"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Global settings instance
settings = Settings()

# Ensure required directories exist
Path(settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
Path(settings.output_path).mkdir(parents=True, exist_ok=True)
Path("./logs").mkdir(exist_ok=True)
