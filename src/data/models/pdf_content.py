from typing import Optional
from pydantic import BaseModel, Field


class PDFContent(BaseModel):
    """Extracted content from a PDF document."""

    filename: str = Field(..., description="PDF filename")
    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    content: str = Field(..., description="Extracted text content")
    is_scanned: bool = Field(default=False, description="Whether content came from OCR")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="OCR confidence if scanned")
