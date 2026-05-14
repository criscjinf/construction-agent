from abc import ABC, abstractmethod


class DocumentIndexer(ABC):
    """Abstract base for document indexers (CSV, PDF, etc)."""

    @abstractmethod
    def load_and_index(self, file_path: str) -> int:
        """
        Load and index a document.

        Args:
            file_path: Path to document file

        Returns:
            Number of items/chunks indexed
        """
        pass
