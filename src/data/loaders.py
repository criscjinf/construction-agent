"""
Data loaders with auto-detection of file format.

Factory pattern: load(file_path) → auto-detects format → dispatches to appropriate parser.
"""

import logging
from pathlib import Path
from typing import Optional

from src.data.models import Project
from src.data.parsers import BaseParser, CSVParser
from src.data.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class DataLoader:
    """Factory for loading data files with format auto-detection."""

    # Map extensions to parser classes
    PARSER_MAP = {
        ".csv": CSVParser,
        ".pdf": PDFParser,
        # ".json": JSONParser,  # Future
    }

    @staticmethod
    def load(file_path: str, verbose: bool = False) -> list[Project]:
        """
        Load data file with automatic format detection.

        Args:
            file_path: Path to input file (CSV, PDF, JSON)
            verbose: Enable debug logging

        Returns:
            List of Project objects

        Raises:
            ValueError: If format not supported or file doesn't exist
            Exception: If parsing fails
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect format from extension
        ext = path.suffix.lower()

        if ext not in DataLoader.PARSER_MAP:
            raise ValueError(
                f"Unsupported file format: {ext}. Supported: {', '.join(DataLoader.PARSER_MAP.keys())}"
            )

        # Get parser and parse
        parser_class = DataLoader.PARSER_MAP[ext]
        parser = parser_class(verbose=verbose)

        logger.info(f"Loading {path.name} with {parser_class.__name__}")
        projects = parser.parse(file_path)

        logger.info(f"Successfully loaded {len(projects)} projects from {path.name}")
        return projects

    @staticmethod
    def register_parser(extension: str, parser_class: type[BaseParser]) -> None:
        """
        Register a new parser for a file extension.

        This allows adding new formats (PDF, JSON, etc) without modifying DataLoader.
        Example:
            DataLoader.register_parser(".pdf", PDFParser)
        """
        ext = extension if extension.startswith(".") else f".{extension}"
        DataLoader.PARSER_MAP[ext] = parser_class
        logger.info(f"Registered parser {parser_class.__name__} for {ext}")
