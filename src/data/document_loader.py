"""
Document loader orchestrator that uses IndexersFactory to dispatch to appropriate indexers.
Handles:
- CSV bid tabulation data (delegated to CSVIndexer via factory)
- PDF plan sets (delegated to PDFIndexer via factory)
"""

import logging
from pathlib import Path
from src.data.indexers import IndexersFactory

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Orchestrate document indexing by delegating to factory-provided indexers."""

    def __init__(self, indexers_factory: IndexersFactory):
        """
        Initialize document loader with indexers factory.

        Args:
            indexers_factory: IndexersFactory instance for getting appropriate indexer
        """
        self.factory = indexers_factory

    def load_and_index(self, file_path: str) -> int:
        """
        Load and index a document (CSV or PDF) by auto-detecting type.

        Args:
            file_path: Path to CSV or PDF file

        Returns:
            Number of items/chunks indexed
        """
        indexer = self.factory.get_indexer(file_path)
        if not indexer:
            ext = Path(file_path).suffix.lower()
            logger.error(f"Unsupported file format: {ext}")
            return 0
        return indexer.load_and_index(file_path)

    def load_all_documents(self, data_dir: str = "data") -> dict:
        """Load all CSV and PDF files from a directory."""
        data_path = Path(data_dir)
        results = {"csv": 0, "pdf": 0, "errors": []}

        for pattern, doc_type in [("*.csv", "csv"), ("*.pdf", "pdf")]:
            for file_path in data_path.glob(pattern):
                try:
                    indexer = self.factory.get_indexer(str(file_path))
                    if indexer:
                        count = indexer.load_and_index(str(file_path))
                        results[doc_type] += count
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
                    results["errors"].append(str(file_path))

        return results
