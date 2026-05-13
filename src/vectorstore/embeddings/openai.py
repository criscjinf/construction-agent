"""OpenAI embedding client implementation."""

import logging
import os
from typing import Optional

from openai import OpenAI

from src.config import Config
from src.vectorstore.embeddings.base import EmbeddingClient

logger = logging.getLogger(__name__)


class OpenAIEmbeddingClient(EmbeddingClient):
    """Client for generating embeddings using OpenAI API."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Initialize OpenAI embedding client.

        Args:
            model: OpenAI embedding model (defaults to Config.EMBEDDING_MODEL)
            api_key: OpenAI API key (from env if not provided)
            verbose: Enable debug logging
        """
        self.model = model or Config.get_embedding_model()
        self.verbose = verbose

        # Get API key from argument or environment
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not provided and not in environment")

        self.client = OpenAI(api_key=key)

        # Dimension for text-embedding-3-small is 1536
        self.embedding_dim = 1536 if "small" in self.model else 3072

        if self.verbose:
            logger.info(f"OpenAIEmbeddingClient initialized: model={self.model}, dim={self.embedding_dim}")

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

    def batch_embed(self, texts: list[str], batch_size: int = 1000) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Process in batches of this size (default: 1000)

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
