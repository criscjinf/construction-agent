"""Factory for creating appropriate agent executor."""

import logging
import os
from typing import Optional

from src.data.models import Project
from src.vectorstore.embeddings import EmbeddingClient
from src.vectorstore.storage import VectorStore
from src.agent.executors.base import BaseAgentExecutor
from src.agent.executors.anthropic import AnthropicAgentExecutor
from src.agent.executors.mock import MockAgentExecutor

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating agent executors with fallback support."""

    @staticmethod
    def create_agent(
        projects: Optional[list[Project]] = None,
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
        prefer_mock: bool = False,
        allow_fallback: bool = True,
    ) -> BaseAgentExecutor:
        """
        Create an agent executor with optional fallback.

        Args:
            projects: List of loaded Project objects (optional)
            vector_store: Vector store for semantic search (optional)
            embedding_client: Embedding client for vectors (optional)
            prefer_mock: If True, use MockAgentExecutor even if API available
            allow_fallback: If True, fall back to MockAgentExecutor on API error

        Returns:
            Agent executor instance (Anthropic or Mock)
        """
        # Prefer mock for testing/offline
        if prefer_mock:
            logger.info("Creating MockAgentExecutor (prefer_mock=True)")
            return MockAgentExecutor(projects, vector_store, embedding_client)

        # Try to create Anthropic agent
        try:
            if not os.getenv("ANTHROPIC_API_KEY"):
                if allow_fallback:
                    logger.warning("ANTHROPIC_API_KEY not set. Using MockAgentExecutor as fallback.")
                    return MockAgentExecutor(projects, vector_store, embedding_client)
                else:
                    raise ValueError("ANTHROPIC_API_KEY not configured")

            logger.info("Creating AnthropicAgentExecutor")
            return AnthropicAgentExecutor(projects, vector_store, embedding_client)

        except Exception as e:
            if allow_fallback:
                logger.warning(f"Failed to create AnthropicAgentExecutor: {e}. Using MockAgentExecutor.")
                return MockAgentExecutor(projects, vector_store, embedding_client)
            else:
                logger.error(f"Failed to create agent and fallback disabled: {e}")
                raise

    @staticmethod
    def get_executor_type(executor: BaseAgentExecutor) -> str:
        """Get the type name of an executor."""
        return type(executor).__name__
