"""Configuration management for Pipecat Agent Builder."""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings


class AIServiceConfig(BaseModel):
    """Configuration for AI services."""
    name: str
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    voice_id: Optional[str] = None
    language: str = "en"


class DeploymentConfig(BaseModel):
    """Configuration for deployment settings."""
    platform: str = "pipecat-cloud"
    scaling_min: int = 1
    scaling_max: int = 10
    region: str = "us-west-2"
    environment: str = "production"


class KnowledgeSourceConfig(BaseModel):
    """Configuration for knowledge sources."""
    type: str  # "web", "document", "api", "database"
    source: str  # URL, file path, API endpoint, etc.
    processing_options: dict = Field(default_factory=dict)


class AgentRequirements(BaseModel):
    """User requirements for the agent being built."""
    name: str
    description: str
    use_case: str
    channels: List[str] = Field(default_factory=list)  # ["phone", "web", "mobile"]
    languages: List[str] = Field(default_factory=lambda: ["en"])
    personality: str = "helpful and professional"
    
    # Service preferences
    stt_service: Optional[AIServiceConfig] = None
    llm_service: Optional[AIServiceConfig] = None
    tts_service: Optional[AIServiceConfig] = None
    
    # Knowledge and integrations
    knowledge_sources: List[KnowledgeSourceConfig] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    
    # Deployment preferences
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    pipecat_cloud_api_key: Optional[str] = None
    pipecat_cloud_org_id: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepgram_api_key: Optional[str] = None
    cartesia_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    daily_api_key: Optional[str] = None
    
    # Telephony
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    telnyx_api_key: Optional[str] = None
    
    # Vector Database
    chroma_persist_directory: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # MCP Configuration
    mcp_server_url: str = "ws://localhost:8765"
    windsurf_cascade_endpoint: Optional[str] = None
    
    # Docker
    docker_hub_username: Optional[str] = None
    docker_hub_token: Optional[str] = None
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
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
