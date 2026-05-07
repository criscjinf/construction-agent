"""
PDF parser for construction plans and documents.

Strategy: Try PyPDF2 (text-native), fallback to pytesseract (scanned images).
Gracefully handles OCR errors and missing text.
"""

import logging
from typing import Optional
from pathlib import Path

from src.data.models import Project, PDFContent
from src.data.parsers import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """PDF parser with text extraction and OCR fallback."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.use_ocr = self._check_ocr_available()

    def parse(self, file_path: str) -> list[Project]:
        """
        Parse PDF file and extract text content.

        Returns a list with one Project containing PDFContent.
        In a real implementation, this could extract structured bid data.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            text = self._extract_text(str(path))
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            text = ""

        if not text:
            logger.warning(f"No text extracted from {file_path}")

        # Create a PDFContent object (not a Project, but compatible data model)
        pdf_content = PDFContent(
            filename=path.name,
            text=text if text else "Could not extract text from PDF"
        )

        if self.verbose:
            logger.info(f"Extracted {len(text)} characters from {path.name}")

        # Return empty projects list (PDF parsing is for vector store embedding, not structured data)
        return []

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2, fallback to OCR."""
        try:
            # Try PyPDF2 first (fast, works for text-native PDFs)
            import PyPDF2

            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()

            if text.strip():
                logger.debug(f"Extracted text from PDF using PyPDF2")
                return text

        except ImportError:
            logger.warning("PyPDF2 not installed, skipping PyPDF2 extraction")
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        # Fallback to OCR if PyPDF2 didn't work
        if self.use_ocr:
            try:
                return self._extract_with_ocr(file_path)
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")

        return ""

    def _extract_with_ocr(self, file_path: str) -> str:
        """Extract text from scanned PDF using pytesseract."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
        except ImportError:
            logger.warning("pytesseract or pdf2image not installed, skipping OCR")
            return ""

        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path)
            text = ""

            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                text += f"\n--- Page {i+1} ---\n{page_text}"

            logger.debug(f"Extracted text from PDF using OCR ({len(images)} pages)")
            return text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    @staticmethod
    def _check_ocr_available() -> bool:
        """Check if pytesseract and tesseract binary are available."""
        try:
            import pytesseract
            # This will raise TesseractNotFoundError if tesseract binary is missing
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
