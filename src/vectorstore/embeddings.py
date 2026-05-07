"""
Embedding client for generating vector representations of text.

Wraps OpenAI embeddings API with batching and caching support.
"""

import logging
from typing import Optional
import os

from openai import OpenAI

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for generating embeddings using OpenAI API."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Initialize embedding client.

        Args:
            model: OpenAI embedding model (default: text-embedding-3-small)
            api_key: OpenAI API key (from env if not provided)
            verbose: Enable debug logging
        """
        self.model = model
        self.verbose = verbose

        # Get API key from argument or environment
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not provided and not in environment")

        self.client = OpenAI(api_key=key)

        # Dimension for text-embedding-3-small is 1536
        self.embedding_dim = 1536 if "small" in model else 3072

        if self.verbose:
            logger.info(f"EmbeddingClient initialized: model={model}, dim={self.embedding_dim}")

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Vector representation (list of floats)
        """
        if not text or not text.strip():
            logger.warning("Attempting to embed empty text")
            return [0.0] * self.embedding_dim

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise

    def batch_embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Process in batches of this size

        Returns:
            List of vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                if self.verbose:
                    logger.info(f"Embedded batch {i // batch_size + 1} ({len(batch)} texts)")

            except Exception as e:
                logger.error(f"Failed to embed batch starting at {i}: {e}")
                raise

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim


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
            import random
            rng = random.Random(h)
            self.cache[text] = [rng.uniform(-1, 1) for _ in range(self.embedding_dim)]

        return self.cache[text]

    def batch_embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.embed_text(text) for text in texts]
