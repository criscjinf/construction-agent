"""Base agent executor interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.data.models import Project
from src.vectorstore.embeddings import EmbeddingClient
from src.vectorstore.storage import VectorStore
from src.agent.tools import get_tool_definitions


class BaseAgentExecutor(ABC):
    """Abstract base for all agent executors."""

    def __init__(
        self,
        projects: list[Project],
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
    ):
        """
        Initialize agent executor.

        Args:
            projects: List of loaded Project objects
            vector_store: Vector store for semantic search (optional)
            embedding_client: Embedding client for vectors (required if vector_store provided)
        """
        self.projects = projects
        self.vector_store = vector_store
        self.embedding_client = embedding_client
        self.tools = get_tool_definitions()

        # Validate dependencies
        if self.vector_store and not self.embedding_client:
            raise ValueError("embedding_client is required when vector_store is provided")

        # Index projects if vector store available
        if self.vector_store:
            self._index_projects_in_vector_store()

    @abstractmethod
    def query(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Execute agent loop: process query, call tools, format response.

        Args:
            user_message: User's natural language query
            max_iterations: Max tool-call iterations (prevent infinite loops)

        Returns:
            Final response with sources cited
        """
        pass

    def _index_projects_in_vector_store(self) -> None:
        """Index project items in vector store for semantic search."""
        from src.agent.prompts import EXAMPLE_QUERIES

        if not self.vector_store or not self.embedding_client:
            return

        # Index example queries as context
        for i, example in enumerate(EXAMPLE_QUERIES):
            try:
                embedding = self.embedding_client.embed_text(example["query"])
                self.vector_store.insert(
                    doc_id=f"example_query_{i}",
                    text=example["query"],
                    embedding=embedding,
                    metadata={
                        "source": "example",
                        "explanation": example["explanation"],
                    }
                )
            except Exception as e:
                # Log but don't fail
                import logging
                logging.warning(f"Failed to index example query {i}: {e}")
