"""
Configuration management for Construction Agent
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file"""

    # API Configuration
    openai_api_key: str
    anthropic_api_key: str

    # Models
    embedding_model: str = "text-embedding-3-small"
    agent_model: str = "claude-sonnet-4-6"

    # Database
    database_url: str = "sqlite:///./construction_agent.db"

    # File Handling
    max_file_size_mb: int = 10
    max_files_per_upload: int = 5

    # Embedding Settings
    embedding_batch_size: int = 100
    embedding_cache_enabled: bool = True

    # Outlier Detection
    outlier_zscore_threshold: float = 2.0
    outlier_iqr_multiplier: float = 1.5

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/construction_agent.log"

    # Development
    debug: bool = False
    verbose: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
