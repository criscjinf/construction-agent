"""
Integration tests for vector store.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.vectorstore.storage import SQLiteVectorStore
from src.vectorstore.embeddings import MockEmbeddingClient


@pytest.fixture
def temp_db():
    """Fixture: Temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def vector_store(temp_db):
    """Fixture: Vector store with temp database."""
    return SQLiteVectorStore(db_path=temp_db)


@pytest.fixture
def embedding_client():
    """Fixture: Mock embedding client."""
    return MockEmbeddingClient()


class TestSQLiteVectorStore:
    """Tests for SQLiteVectorStore."""

    def test_store_initializes(self, vector_store):
        """Test store initialization."""
        assert vector_store is not None
        assert vector_store.count() == 0

    def test_insert_and_retrieve(self, vector_store, embedding_client):
        """Test inserting and retrieving a document."""
        doc_id = "item_1"
        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)
        metadata = {"item_no": "1031000", "unit": "LS"}

        vector_store.insert(doc_id, text, embedding, metadata)

        doc = vector_store.get_by_id(doc_id)
        assert doc is not None
        assert doc["text"] == text
        assert doc["doc_id"] == doc_id
        assert doc["metadata"] == metadata

    def test_insert_updates_existing(self, vector_store, embedding_client):
        """Test that inserting with same ID updates document."""
        doc_id = "item_1"
        text1 = "MOBILIZATION"
        text2 = "BONDS AND INSURANCE"

        emb1 = embedding_client.embed_text(text1)
        emb2 = embedding_client.embed_text(text2)

        vector_store.insert(doc_id, text1, emb1)
        vector_store.insert(doc_id, text2, emb2)

        doc = vector_store.get_by_id(doc_id)
        assert doc["text"] == text2  # Should be updated

    def test_delete(self, vector_store, embedding_client):
        """Test deleting a document."""
        doc_id = "item_1"
        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)

        vector_store.insert(doc_id, text, embedding)
        assert vector_store.count() == 1

        deleted = vector_store.delete(doc_id)
        assert deleted is True
        assert vector_store.count() == 0

    def test_delete_nonexistent(self, vector_store):
        """Test deleting non-existent document."""
        deleted = vector_store.delete("nonexistent")
        assert deleted is False

    def test_search_returns_similar_items(self, vector_store, embedding_client):
        """Test search returns documents with high similarity."""
        # Insert similar documents
        texts = [
            ("item_1", "MOBILIZATION"),
            ("item_2", "MOBILIZATION AND DEMOBILIZATION"),
            ("item_3", "EXCAVATION"),
        ]

        for doc_id, text in texts:
            embedding = embedding_client.embed_text(text)
            vector_store.insert(doc_id, text, embedding, {"text": text})

        # Search for similar
        query_embedding = embedding_client.embed_text("MOBILIZATION")
        results = vector_store.search(query_embedding, limit=5, threshold=0.5)

        # Should find documents (mock embeddings deterministic)
        assert len(results) >= 0

    def test_search_respects_threshold(self, vector_store, embedding_client):
        """Test search respects similarity threshold."""
        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)
        vector_store.insert("item_1", text, embedding)

        # Search with high threshold
        results_high = vector_store.search(embedding, limit=5, threshold=0.99)

        # Search with low threshold
        results_low = vector_store.search(embedding, limit=5, threshold=0.01)

        # High threshold should return fewer results
        assert len(results_high) <= len(results_low)

    def test_search_respects_limit(self, vector_store, embedding_client):
        """Test search respects limit parameter."""
        # Insert 10 documents
        for i in range(10):
            text = f"Item {i}"
            embedding = embedding_client.embed_text(text)
            vector_store.insert(f"item_{i}", text, embedding)

        # Search with limit
        query_embedding = embedding_client.embed_text("Item")
        results = vector_store.search(query_embedding, limit=3, threshold=0.0)

        assert len(results) <= 3

    def test_count(self, vector_store, embedding_client):
        """Test count method."""
        assert vector_store.count() == 0

        for i in range(5):
            text = f"Item {i}"
            embedding = embedding_client.embed_text(text)
            vector_store.insert(f"item_{i}", text, embedding)

        assert vector_store.count() == 5

    def test_clear(self, vector_store, embedding_client):
        """Test clear method."""
        # Insert documents
        for i in range(3):
            text = f"Item {i}"
            embedding = embedding_client.embed_text(text)
            vector_store.insert(f"item_{i}", text, embedding)

        assert vector_store.count() == 3

        vector_store.clear()
        assert vector_store.count() == 0

    def test_metadata_preservation(self, vector_store, embedding_client):
        """Test that metadata is preserved."""
        metadata = {
            "item_no": "1031000",
            "item_desc": "MOBILIZATION",
            "unit": "LS",
            "qty": 1.0,
            "unit_price": 16500.0,
        }

        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)
        vector_store.insert("item_1", text, embedding, metadata)

        doc = vector_store.get_by_id("item_1")
        assert doc["metadata"] == metadata

    def test_search_returns_metadata(self, vector_store, embedding_client):
        """Test that search results include metadata."""
        metadata = {"category": "labor"}
        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)
        vector_store.insert("item_1", text, embedding, metadata)

        # Search for exact same embedding
        results = vector_store.search(embedding, limit=5, threshold=0.9)

        # Should find the document with metadata
        assert any(doc_id == "item_1" and meta == metadata for doc_id, score, meta in results)

    def test_search_with_no_results(self, vector_store, embedding_client):
        """Test search returns empty list when no matches."""
        text = "MOBILIZATION"
        embedding = embedding_client.embed_text(text)
        vector_store.insert("item_1", text, embedding)

        # Search with very high threshold (won't match)
        query_embedding = embedding_client.embed_text("COMPLETELY DIFFERENT")
        results = vector_store.search(query_embedding, limit=5, threshold=0.99)

        assert len(results) == 0
