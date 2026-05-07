"""
Tests for embedding clients.
"""

import pytest
from src.vectorstore.embeddings import EmbeddingClient, MockEmbeddingClient


class TestMockEmbeddingClient:
    """Tests for MockEmbeddingClient (no API calls)."""

    def test_client_initializes(self):
        """Test client initialization."""
        client = MockEmbeddingClient()
        assert client is not None
        assert client.embedding_dim == 1536

    def test_embed_single_text(self):
        """Test embedding a single text."""
        client = MockEmbeddingClient()
        text = "What are the top bid items?"
        embedding = client.embed_text(text)

        assert embedding is not None
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_same_text_returns_same_embedding(self):
        """Test that same text returns same embedding (deterministic)."""
        client = MockEmbeddingClient()
        text = "MOBILIZATION"

        embedding1 = client.embed_text(text)
        embedding2 = client.embed_text(text)

        assert embedding1 == embedding2

    def test_embed_different_texts_return_different_embeddings(self):
        """Test that different texts return different embeddings."""
        client = MockEmbeddingClient()

        emb1 = client.embed_text("MOBILIZATION")
        emb2 = client.embed_text("BONDS AND INSURANCE")

        assert emb1 != emb2

    def test_batch_embed(self):
        """Test batch embedding."""
        client = MockEmbeddingClient()
        texts = ["Text 1", "Text 2", "Text 3"]

        embeddings = client.batch_embed(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)

    def test_embed_empty_text(self):
        """Test embedding empty text returns zero vector."""
        client = MockEmbeddingClient()
        embedding = client.embed_text("")

        assert embedding == [0.0] * 1536

    def test_embedding_dimension_small_model(self):
        """Test embedding dimension for text-embedding-3-small."""
        client = MockEmbeddingClient(model="text-embedding-3-small")
        assert client.get_dimension() == 1536

    def test_embedding_dimension_large_model(self):
        """Test embedding dimension for text-embedding-3-large."""
        client = MockEmbeddingClient(model="text-embedding-3-large")
        assert client.get_dimension() == 3072

    def test_embeddings_are_normalized_range(self):
        """Test embeddings are in reasonable range."""
        client = MockEmbeddingClient()
        embedding = client.embed_text("test text")

        # Mock embeddings should be in [-1, 1] range
        assert all(-1.1 <= x <= 1.1 for x in embedding)
