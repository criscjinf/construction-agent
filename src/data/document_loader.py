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

    @staticmethod
    def discover_files(folder_path: str) -> tuple[list[str], dict]:
        """
        Discover all CSV and PDF files in a folder without requiring indexers.
        Static method for lightweight file discovery (no indexing).

        Args:
            folder_path: Path to folder containing documents

        Returns:
            Tuple of (file_paths, results) with counts and errors
        """
        data_path = Path(folder_path)

        if not data_path.exists():
            logger.error(f"Folder not found: {folder_path}")
            return [], {"csv": 0, "pdf": 0, "errors": [f"Folder not found: {folder_path}"]}

        if not data_path.is_dir():
            logger.error(f"Not a directory: {folder_path}")
            return [], {"csv": 0, "pdf": 0, "errors": [f"Not a directory: {folder_path}"]}

        file_paths = []
        results = {"csv": 0, "pdf": 0, "errors": []}

        # Find all CSV and PDF files
        for pattern, doc_type in [("*.csv", "csv"), ("*.pdf", "pdf")]:
            for file_path in data_path.glob(pattern):
                try:
                    file_paths.append(str(file_path))
                    results[doc_type] += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results["errors"].append(str(file_path))

        return file_paths, results

    def load_folder(self, folder_path: str) -> dict:
        """
        Load and index all CSV and PDF files from a folder.
        Discovers files and indexes each one.

        Args:
            folder_path: Path to folder containing documents

        Returns:
            Results dict with indexed counts and errors
        """
        # Discover files in folder (uses static method)
        file_paths, results = self.discover_files(folder_path)

        if not file_paths:
            logger.warning(f"No CSV or PDF files found in {folder_path}")
            return results

        # Index each discovered file
        indexed_count = 0
        for file_path in file_paths:
            try:
                count = self.load_and_index(file_path)
                if count > 0:
                    indexed_count += count
                    logger.debug(f"Indexed {count} items from {Path(file_path).name}")
            except Exception as e:
                logger.error(f"Error indexing {file_path}: {e}")
                results["errors"].append(str(file_path))

        results["indexed"] = indexed_count
        return results
