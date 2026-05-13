"""
Centralized configuration management for Construction Estimating Agent.

All environment variables are read and validated here, ensuring consistent
defaults and type safety throughout the application.
"""

import os
from typing import Literal


class Config:
    """Application configuration from environment variables."""

    # API Keys (Required)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Models (Configurable)
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "text-embedding-3-small"
    )
    AGENT_MODEL: str = os.getenv(
        "AGENT_MODEL", "claude-sonnet-4-6"
    )

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str | None = os.getenv("LOG_FILE")

    @classmethod
    def is_debug(cls) -> bool:
        """Check if debug mode is enabled."""
        return cls.LOG_LEVEL == "DEBUG"

    @classmethod
    def validate(cls) -> None:
        """
        Validate critical configuration.

        Raises:
            ValueError: If required config is missing or invalid
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "❌ OPENAI_API_KEY not configured\n"
                "Set in .env file for embedding generation"
            )

        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY not configured\n"
                "Set in .env file to use Claude agent"
            )

        # Validate model names
        if not cls.EMBEDDING_MODEL:
            raise ValueError("EMBEDDING_MODEL must be specified")

        if not cls.AGENT_MODEL:
            raise ValueError("AGENT_MODEL must be specified")

    @classmethod
    def get_embedding_model(cls) -> str:
        """Get configured embedding model."""
        return cls.EMBEDDING_MODEL

    @classmethod
    def get_agent_model(cls) -> str:
        """Get configured agent model."""
        return cls.AGENT_MODEL

    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary (without sensitive keys)."""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "agent_model": cls.AGENT_MODEL,
            "log_level": cls.LOG_LEVEL,
            "log_file": cls.LOG_FILE,
        }

    @classmethod
    def __repr__(cls) -> str:
        """Return config summary for logging."""
        return (
            f"Config(embedding_model={cls.EMBEDDING_MODEL}, "
            f"agent_model={cls.AGENT_MODEL}, log_level={cls.LOG_LEVEL})"
        )
