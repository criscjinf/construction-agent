"""Mock embedding client for testing (no API calls)."""

import logging
import random

from src.vectorstore.embeddings.base import EmbeddingClient

logger = logging.getLogger(__name__)


class MockEmbeddingClient(EmbeddingClient):
    """Mock embedding client for testing (doesn't call OpenAI API)."""

    def __init__(self, model: str = "text-embedding-3-small", verbose: bool = False):
        """Initialize mock client (no API key needed)."""
        self.model = model
        self.verbose = verbose
        self.embedding_dim = 1536 if "small" in model else 3072
        self.cache = {}

        if self.verbose:
            logger.info(f"MockEmbeddingClient initialized (no API calls)")

    def embed_text(self, text: str) -> list[float]:
        """
        Generate mock embedding (deterministic hash-based).

        Same text always returns same embedding.
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dim

        # Use hash for deterministic but varied embeddings
        if text not in self.cache:
            # Simple hash-based embedding: normalize hash to [-1, 1]
            h = hash(text)
            # Create vector from hash (deterministic)
            rng = random.Random(h)
            self.cache[text] = [rng.uniform(-1, 1) for _ in range(self.embedding_dim)]

        return self.cache[text]

    def batch_embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.embed_text(text) for text in texts]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim
