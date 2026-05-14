"""Abstract base class for embedding clients."""

from abc import ABC, abstractmethod


class EmbeddingClient(ABC):
    """Abstract embedding client interface."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    def batch_embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass
