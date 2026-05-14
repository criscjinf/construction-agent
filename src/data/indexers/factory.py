import logging
from pathlib import Path
from src.data.indexers.csv_indexer import CSVIndexer
from src.data.indexers.pdf_indexer import PDFIndexer
from src.vectorstore.storage import VectorStore
from src.vectorstore.embeddings import EmbeddingClient

logger = logging.getLogger(__name__)


class IndexersFactory:
    """Factory for creating and retrieving appropriate indexers based on file type."""

    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        """
        Initialize factory and create indexer instances.

        Args:
            vector_store: VectorStore instance for storing embeddings
            embedding_client: EmbeddingClient instance for generating embeddings
        """
        self.indexers = {
            ".csv": CSVIndexer(vector_store=vector_store, embedding_client=embedding_client),
            ".pdf": PDFIndexer(vector_store=vector_store, embedding_client=embedding_client),
        }

    def get_indexer(self, file_path: str):
        """
        Get indexer for file based on extension.

        Args:
            file_path: Path to file

        Returns:
            DocumentIndexer instance or None if unsupported type
        """
        ext = Path(file_path).suffix.lower()
        return self.indexers.get(ext)
