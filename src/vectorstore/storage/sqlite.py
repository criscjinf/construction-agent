"""SQLite implementation of vector store."""

import sqlite3
import logging
import json
from typing import Optional

from src.vectorstore.storage.base import VectorStore
from src.vectorstore.similarity import VectorSimilarity

logger = logging.getLogger(__name__)


class SQLiteVectorStore(VectorStore):
    """SQLite-based vector store implementation."""

    def __init__(self, db_path: str = "./construction_agent.db"):
        """Initialize SQLite vector store."""
        self.db_path = db_path
        self._init_db()
        logger.info(f"SQLiteVectorStore initialized at {db_path}")

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create table for documents with embeddings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index for faster lookups
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_doc_id ON documents(doc_id)
            """
            )

            conn.commit()

    def insert(
        self, doc_id: str, text: str, embedding: list[float], metadata: Optional[dict] = None
    ) -> None:
        """Insert document with embedding into store."""
        try:
            embedding_json = json.dumps(embedding)
            metadata_json = json.dumps(metadata) if metadata else None

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert or replace
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO documents (doc_id, text, embedding, metadata)
                    VALUES (?, ?, ?, ?)
                """,
                    (doc_id, text, embedding_json, metadata_json),
                )

                conn.commit()

            logger.debug(f"Inserted document {doc_id}")

        except Exception as e:
            logger.error(f"Failed to insert document {doc_id}: {e}")
            raise

    def search(
        self, query_embedding: list[float], limit: int = 5, threshold: float = 0.7
    ) -> list[tuple[str, float, dict]]:
        """
        Search for similar documents using cosine similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (doc_id, score, metadata) tuples, sorted by score descending
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Fetch all documents
                cursor.execute("SELECT doc_id, embedding, metadata FROM documents")
                results = []

                for doc_id, embedding_json, metadata_json in cursor.fetchall():
                    embedding = json.loads(embedding_json)

                    # Calculate cosine similarity
                    similarity = VectorSimilarity.cosine(query_embedding, embedding)

                    # Filter by threshold
                    if similarity >= threshold:
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        results.append((doc_id, similarity, metadata))

            # Sort by similarity descending, limit results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
                conn.commit()

                deleted = cursor.rowcount > 0
                logger.debug(f"Document {doc_id} deleted: {deleted}")
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise

    def clear(self) -> None:
        """Clear all documents."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents")
                conn.commit()
                logger.info("Vector store cleared")

        except Exception as e:
            logger.error(f"Failed to clear store: {e}")
            raise

    def get_by_id(self, doc_id: str) -> Optional[dict]:
        """Retrieve document by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT text, embedding, metadata FROM documents WHERE doc_id = ?", (doc_id,))
                row = cursor.fetchone()

                if row:
                    return {
                        "doc_id": doc_id,
                        "text": row[0],
                        "embedding": json.loads(row[1]),
                        "metadata": json.loads(row[2]) if row[2] else {},
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise

    def count(self) -> int:
        """Get total number of documents in store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            raise

    def get_all_doc_ids(self) -> list[str]:
        """Get all document IDs in store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT doc_id FROM documents")
                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get all doc IDs: {e}")
            raise
