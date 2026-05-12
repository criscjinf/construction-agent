"""Abstract vector store interface for repository pattern."""

from abc import ABC, abstractmethod
from typing import Optional


class VectorStore(ABC):
    """Abstract vector store interface."""

    @abstractmethod
    def insert(
        self, doc_id: str, text: str, embedding: list[float], metadata: Optional[dict] = None
    ) -> None:
        """Insert document with embedding."""
        pass

    @abstractmethod
    def search(
        self, query_embedding: list[float], limit: int = 5, threshold: float = 0.7
    ) -> list[tuple[str, float, dict]]:
        """Search for similar documents. Returns (doc_id, score, metadata)."""
        pass

    @abstractmethod
    def delete(self, doc_id: str) -> bool:
        """Delete document by ID."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents."""
        pass

    @abstractmethod
    def get_by_id(self, doc_id: str) -> Optional[dict]:
        """Retrieve document by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get total number of documents."""
        pass

    @abstractmethod
    def get_all_doc_ids(self) -> list[str]:
        """Get all document IDs in store."""
        pass
