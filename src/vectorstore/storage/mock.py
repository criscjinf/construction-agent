import logging
from src.vectorstore.storage.base import VectorStore

logger = logging.getLogger(__name__)


class MockVectorStore(VectorStore):
    """In-memory mock vector store for testing without database I/O."""

    def __init__(self):
        """Initialize in-memory storage."""
        self.documents = {}  # doc_id -> {text, embedding, metadata}

    def insert(self, doc_id: str, text: str, embedding: list[float], metadata: dict = None) -> None:
        """Insert document into in-memory store."""
        self.documents[doc_id] = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
        }
        logger.debug(f"Mock insert: {doc_id}")

    def search(self, embedding: list[float], limit: int = 5, threshold: float = 0.0) -> list[tuple]:
        """Search by cosine similarity (all results above threshold)."""
        if not self.documents:
            return []

        results = []
        for doc_id, doc in self.documents.items():
            similarity = self._cosine_similarity(embedding, doc["embedding"])
            if similarity >= threshold:
                results.append((doc_id, similarity, doc["metadata"]))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def delete(self, doc_id: str) -> None:
        """Delete document from in-memory store."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            logger.debug(f"Mock delete: {doc_id}")

    def clear(self) -> None:
        """Clear all documents from in-memory store."""
        self.documents.clear()
        logger.debug("Mock clear all")

    def get_by_id(self, doc_id: str) -> dict | None:
        """Get document by ID."""
        return self.documents.get(doc_id)

    def count(self) -> int:
        """Return total document count."""
        return len(self.documents)

    def get_all_doc_ids(self) -> list[str]:
        """Return all document IDs."""
        return list(self.documents.keys())

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)
