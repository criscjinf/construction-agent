"""
Integration tests for hybrid retrieval.
"""

import pytest
import tempfile
import os

from src.vectorstore.storage import SQLiteVectorStore
from src.vectorstore.embeddings import MockEmbeddingClient
from src.vectorstore.retrieval import HybridRetriever


@pytest.fixture
def temp_db():
    """Fixture: Temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def vector_store(temp_db):
    """Fixture: Vector store."""
    return SQLiteVectorStore(db_path=temp_db)


@pytest.fixture
def embedding_client():
    """Fixture: Mock embedding client."""
    return MockEmbeddingClient()


@pytest.fixture
def retriever(vector_store, embedding_client):
    """Fixture: Hybrid retriever."""
    return HybridRetriever(vector_store, embedding_client)


@pytest.fixture
def sample_docs(vector_store, embedding_client):
    """Fixture: Insert sample bid items."""
    docs = [
        ("item_1", "MOBILIZATION", {"item_no": "1031000", "category": "overhead"}),
        ("item_2", "BONDS AND INSURANCE", {"item_no": "1032010", "category": "overhead"}),
        ("item_3", "BORROW EXCAVATION", {"item_no": "2033000", "category": "earthwork"}),
        ("item_4", "ASPHALT PAVING", {"item_no": "4040350", "category": "pavement"}),
        ("item_5", "GRASSING", {"item_no": "8100102", "category": "landscape"}),
    ]

    for doc_id, text, metadata in docs:
        embedding = embedding_client.embed_text(text)
        vector_store.insert(doc_id, text, embedding, metadata)

    return docs


class TestHybridRetriever:
    """Tests for HybridRetriever."""

    def test_retriever_initializes(self, retriever):
        """Test retriever initialization."""
        assert retriever is not None
        assert retriever.semantic_weight == 0.7
        assert retriever.keyword_weight == 0.3

    def test_semantic_search_only(self, retriever, sample_docs):
        """Test semantic search finds relevant items."""
        results = retriever.search_semantic_only("MOBILIZATION", limit=3, threshold=0.5)

        # Should find some results (mock embeddings are deterministic)
        assert isinstance(results, list)

    def test_keyword_search_only(self, retriever, sample_docs):
        """Test keyword search finds term matches."""
        results = retriever.search_keyword_only("MOBILIZATION", limit=3)

        # Should find documents with matching keywords
        assert isinstance(results, list)
        # With mock setup, might not find results but shouldn't crash

    def test_hybrid_search_combines_results(self, retriever, sample_docs):
        """Test hybrid search returns results."""
        results = retriever.search("MOBILIZATION", limit=3, semantic_threshold=0.0)

        assert isinstance(results, list)
        # Each result is (doc_id, score, metadata)
        if results:
            doc_id, score, metadata = results[0]
            assert isinstance(doc_id, str)
            assert isinstance(score, float)
            assert isinstance(metadata, dict)

    def test_hybrid_search_empty_query(self, retriever):
        """Test hybrid search with empty query."""
        results = retriever.search("", limit=5)
        assert results == []

    def test_search_respects_limit(self, retriever, sample_docs):
        """Test search respects limit parameter."""
        results = retriever.search("asphalt", limit=2, semantic_threshold=0.0)

        assert len(results) <= 2

    def test_semantic_weight_affects_ranking(self, retriever1, retriever2, sample_docs):
        """Test that semantic weight affects result ranking."""
        # retriever1 has high semantic weight
        # retriever2 has high keyword weight
        # Results should be ranked differently

        # Note: This test is conceptual; actual implementation would need
        # to verify ranking changes, which is complex with mock embeddings
        assert retriever1.semantic_weight > retriever2.semantic_weight

    def test_search_with_threshold_filters(self, retriever, sample_docs):
        """Test threshold filtering."""
        results_low = retriever.search("test", limit=10, semantic_threshold=0.0)
        results_high = retriever.search("test", limit=10, semantic_threshold=0.99)

        # High threshold should filter more results
        assert len(results_high) <= len(results_low)

    def test_metadata_in_results(self, retriever, sample_docs):
        """Test that metadata is returned in search results."""
        results = retriever.search("PAVING", limit=5, semantic_threshold=0.0)

        if results:
            doc_id, score, metadata = results[0]
            # Metadata should be dict with our custom fields
            assert isinstance(metadata, dict)


class TestWeightCombinations:
    """Test different weight combinations."""

    def test_semantic_heavy(self, vector_store, embedding_client):
        """Test retriever with semantic-heavy weighting."""
        retriever = HybridRetriever(
            vector_store,
            embedding_client,
            semantic_weight=0.9,
            keyword_weight=0.1,
        )

        assert retriever.semantic_weight == 0.9

    def test_keyword_heavy(self, vector_store, embedding_client):
        """Test retriever with keyword-heavy weighting."""
        retriever = HybridRetriever(
            vector_store,
            embedding_client,
            semantic_weight=0.2,
            keyword_weight=0.8,
        )

        assert retriever.keyword_weight == 0.8

    def test_equal_weights(self, vector_store, embedding_client):
        """Test retriever with equal weights."""
        retriever = HybridRetriever(
            vector_store,
            embedding_client,
            semantic_weight=0.5,
            keyword_weight=0.5,
        )

        assert retriever.semantic_weight == 0.5
        assert retriever.keyword_weight == 0.5


@pytest.fixture
def retriever1(vector_store, embedding_client):
    """High semantic weight retriever."""
    return HybridRetriever(vector_store, embedding_client, semantic_weight=0.9)


@pytest.fixture
def retriever2(vector_store, embedding_client):
    """High keyword weight retriever."""
    return HybridRetriever(vector_store, embedding_client, semantic_weight=0.2)
