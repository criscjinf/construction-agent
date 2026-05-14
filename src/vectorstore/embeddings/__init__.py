"""Embedding clients for generating vector representations."""

from src.vectorstore.embeddings.base import EmbeddingClient
from src.vectorstore.embeddings.openai import OpenAIEmbeddingClient
from src.vectorstore.embeddings.mock import MockEmbeddingClient

__all__ = [
    "EmbeddingClient",
    "OpenAIEmbeddingClient",
    "MockEmbeddingClient",
]
