"""Document indexing orchestration service."""

import logging
from pathlib import Path
from typing import Tuple

from src.config import Config
from src.data.indexers.factory import IndexersFactory
from src.vectorstore.storage import SQLiteVectorStore
from src.vectorstore.embeddings import OpenAIEmbeddingClient


class IndexOrchestrator:
    """Orchestrates the document indexing pipeline."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize index orchestrator.

        Args:
            logger: Logger instance
        """
        self.log = logger

    def index_files(
        self,
        uploaded_files: list[str],
        db_path: str
    ) -> Tuple[SQLiteVectorStore, OpenAIEmbeddingClient, dict]:
        """
        Index documents into vector store.

        Args:
            uploaded_files: List of file paths to index
            db_path: Path to SQLite database

        Returns:
            Tuple of (vector_store, embedding_client, results)

        Raises:
            ValueError: If OpenAI API key not configured or embedding fails
        """
        # Import here to avoid circular dependency
        from src.data.document_loader import DocumentLoader

        self._print_header("📊 INDEXING DOCUMENTS")

        self.log.info(f"📊 Initializing SQLite vector store at {db_path}")
        vector_store = SQLiteVectorStore(db_path=db_path)
        self.log.debug("✅ Vector store initialized")

        if not Config.OPENAI_API_KEY:
            self.log.error("❌ OPENAI_API_KEY not configured in .env")
            self.log.info("To use document indexing, set OPENAI_API_KEY in your .env file")
            raise ValueError("OPENAI_API_KEY not configured")

        try:
            embedding_client = OpenAIEmbeddingClient()
            self.log.info("📦 Initializing indexers with OpenAI embeddings")
            self.log.debug("Using OpenAI text-embedding-3-small")
        except Exception as e:
            self.log.error(f"❌ Failed to initialize OpenAI embeddings: {e}")
            self.log.info("Check that OPENAI_API_KEY is valid and you have sufficient credits")
            raise ValueError(f"Failed to initialize embeddings: {e}")

        indexers_factory = IndexersFactory(vector_store=vector_store, embedding_client=embedding_client)
        doc_loader = DocumentLoader(indexers_factory=indexers_factory)
        self.log.debug("✅ DocumentLoader initialized with factory")

        results = {"csv": 0, "pdf": 0}
        self.log.info(f"📄 Starting indexing of {len(uploaded_files)} documents...")

        for file_path in uploaded_files:
            filename = Path(file_path).name
            ext = Path(file_path).suffix.lower()

            try:
                self.log.debug(f"🔄 Indexing {ext.upper()}: {filename}")
                count = doc_loader.load_and_index(file_path)

                if ext == ".csv":
                    results["csv"] += count
                    self.log.info(f"   ✅ CSV indexed: {filename} ({count} items)")
                elif ext == ".pdf":
                    results["pdf"] += count
                    self.log.info(f"   ✅ PDF indexed: {filename} ({count} chunks)")

            except Exception as e:
                is_debug = Config.is_debug()
                self.log.error(f"❌ Error indexing {filename}: {e}", exc_info=is_debug)
                print(f"⚠️  Error indexing {filename}: {e}")

        self.log.info(f"✅ Indexing complete: CSV={results['csv']}, PDF={results['pdf']}")
        print(f"\n✅ Indexing complete:")
        print(f"   • CSV items: {results['csv']}")
        print(f"   • PDF chunks: {results['pdf']}")
        print(f"   • Total: {results['csv'] + results['pdf']}")

        return vector_store, embedding_client, results

    @staticmethod
    def _print_header(title: str) -> None:
        """Print formatted header."""
        print("\n" + "=" * 90)
        print(f"  {title}")
        print("=" * 90)
