"""
Hybrid search combining semantic embeddings and keyword matching.

Retrieval strategy: Fusion of semantic similarity and keyword overlap.
"""

import logging
from typing import Optional
from collections import Counter
import math

from src.vectorstore.storage import VectorStore
from src.vectorstore.embeddings import EmbeddingClient

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retrieval combining semantic and keyword search."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_client: EmbeddingClient,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        """
        Initialize hybrid retriever.

        Args:
            vector_store: Vector store for semantic search
            embedding_client: Embedding generator
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword overlap (0-1)
        """
        self.vector_store = vector_store
        self.embedding_client = embedding_client
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

        if abs(semantic_weight + keyword_weight - 1.0) > 0.01:
            logger.warning(f"Weights don't sum to 1.0: {semantic_weight} + {keyword_weight}")

    def search(
        self,
        query: str,
        limit: int = 5,
        semantic_threshold: float = 0.5,
        keyword_threshold: float = 0.0,
    ) -> list[tuple[str, float, dict]]:
        """
        Perform hybrid search.

        Args:
            query: Search query
            limit: Maximum results to return
            semantic_threshold: Minimum semantic similarity
            keyword_threshold: Minimum keyword overlap (0-1)

        Returns:
            List of (doc_id, hybrid_score, metadata) tuples
        """
        if not query or not query.strip():
            logger.warning("Empty query")
            return []

        # Get semantic results
        query_embedding = self.embedding_client.embed_text(query)
        semantic_results = self.vector_store.search(
            query_embedding, limit=limit * 2, threshold=semantic_threshold
        )

        # Get keyword results
        keyword_results = self._keyword_search(query, limit=limit * 2)

        # Fuse results
        fused = self._fuse_results(semantic_results, keyword_results)

        # Filter by keyword threshold
        filtered = [
            (doc_id, score, meta)
            for doc_id, score, meta in fused
            if score >= keyword_threshold or semantic_results  # Include if no keywords matched
        ]

        # Return top limit
        return filtered[:limit]

    def search_semantic_only(
        self, query: str, limit: int = 5, threshold: float = 0.5
    ) -> list[tuple[str, float, dict]]:
        """Search using semantic embeddings only."""
        query_embedding = self.embedding_client.embed_text(query)
        return self.vector_store.search(query_embedding, limit=limit, threshold=threshold)

    def search_keyword_only(self, query: str, limit: int = 5) -> list[tuple[str, float, dict]]:
        """Search using keywords only."""
        return self._keyword_search(query, limit=limit)

    def _keyword_search(self, query: str, limit: int = 5) -> list[tuple[str, float, dict]]:
        """
        Keyword search using term overlap.

        Returns: (doc_id, overlap_score, metadata)
        """
        query_terms = set(query.lower().split())

        if not query_terms:
            return []

        # Fetch all documents and score by keyword overlap
        results = []

        # We need to iterate through all documents
        # Since VectorStore doesn't have a method to fetch all, we use a trick:
        # Search with a very generic query to get embeddings, then score by keywords
        # For now, implement simple approach: search for each term

        term_scores = {}

        for doc_id in self._get_all_doc_ids():
            doc = self.vector_store.get_by_id(doc_id)
            if doc is None:
                continue

            text = doc["text"].lower()
            doc_terms = set(text.split())

            # Jaccard similarity (overlap / union)
            overlap = len(query_terms & doc_terms)
            union = len(query_terms | doc_terms)

            if union > 0:
                jaccard = overlap / union
                if jaccard > 0:
                    metadata = doc.get("metadata", {})
                    results.append((doc_id, jaccard, metadata))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _fuse_results(
        self,
        semantic_results: list[tuple[str, float, dict]],
        keyword_results: list[tuple[str, float, dict]],
    ) -> list[tuple[str, float, dict]]:
        """
        Fuse semantic and keyword results.

        Combine scores: hybrid_score = semantic_weight * sem_score + keyword_weight * kw_score
        """
        # Create score maps
        semantic_scores = {doc_id: (score, meta) for doc_id, score, meta in semantic_results}
        keyword_scores = {doc_id: (score, meta) for doc_id, score, meta in keyword_results}

        # Collect all doc IDs
        all_doc_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())

        fused = []

        for doc_id in all_doc_ids:
            sem_score, sem_meta = semantic_scores.get(doc_id, (0.0, {}))
            kw_score, kw_meta = keyword_scores.get(doc_id, (0.0, {}))

            # Fuse scores
            hybrid_score = self.semantic_weight * sem_score + self.keyword_weight * kw_score

            # Use metadata from whichever source had higher score
            metadata = sem_meta if sem_score >= kw_score else kw_meta

            fused.append((doc_id, hybrid_score, metadata))

        # Sort by hybrid score descending
        fused.sort(key=lambda x: x[1], reverse=True)

        return fused

    def _get_all_doc_ids(self) -> list[str]:
        """Get all document IDs in store."""
        return self.vector_store.get_all_doc_ids()
