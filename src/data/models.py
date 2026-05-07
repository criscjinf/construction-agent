"""
Data models for Construction Estimating Agent using Pydantic with validation.

Core models:
- Project: A single bid project with metadata
- BidItem: A line item in a bid (quantity, unit price, extended amount)
- Bidder: A company submitting a bid
- BidTabulation: Complete tabulation for a project
"""

from datetime import date
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Bidder(BaseModel):
    """A company submitting a bid."""

    name: str = Field(..., min_length=1, description="Bidder company name")
    bid_rank: int = Field(..., gt=0, description="Ranking in bid competition (1 = lowest)")
    bid_total: float = Field(..., ge=0, description="Total bid amount in dollars")

    class Config:
        frozen = True


class BidItem(BaseModel):
    """A single line item in a bid tabulation."""

    item_no: str = Field(..., min_length=1, description="Item number (e.g., '1031000')")
    item_desc: str = Field(..., min_length=1, description="Item description")
    unit: str = Field(..., min_length=1, description="Unit of measure (e.g., 'LS', 'CY', 'TON')")
    qty: float = Field(..., ge=0, description="Quantity")
    eng_est_unit_pr: float = Field(default=0.0, ge=0, description="Engineer estimate unit price")
    unit_price: float = Field(..., ge=0, description="Bid unit price")
    ext_amt: float = Field(..., ge=0, description="Extended amount (qty × unit_price)")

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: float, info) -> float:
        """Ensure unit price is reasonable (not NaN or infinite)."""
        if not (-1e10 < v < 1e10):
            raise ValueError(f"Unit price out of reasonable range: {v}")
        return v

    @field_validator("ext_amt")
    @classmethod
    def validate_ext_amt(cls, v: float, info) -> float:
        """Ensure extended amount is reasonable."""
        if not (-1e10 < v < 1e10):
            raise ValueError(f"Extended amount out of reasonable range: {v}")
        return v

    def is_reasonable(self) -> bool:
        """Check if item has reasonable values (for flagging outliers later)."""
        if self.qty < 0 or self.unit_price < 0 or self.ext_amt < 0:
            return False
        if self.qty > 0 and abs(self.ext_amt - self.qty * self.unit_price) > 0.01:
            return False  # ext_amt doesn't match qty * unit_price
        return True


class BidderItem(BaseModel):
    """A bid item with its bidder context."""

    bidder: Bidder
    item: BidItem


class Project(BaseModel):
    """A construction project with bid information."""

    proj_id: str = Field(..., min_length=1, description="Project ID")
    let_dt: Optional[date] = Field(None, description="Letting date")
    county: Optional[str] = Field(None, description="County")
    bidders: dict[str, Bidder] = Field(default_factory=dict, description="Bidders by rank")
    items: list[BidItem] = Field(default_factory=list, description="All bid items")
    bidder_items: dict[str, list[BidItem]] = Field(
        default_factory=dict, description="Items grouped by bidder name"
    )

    def get_items_for_bidder(self, bidder_name: str) -> list[BidItem]:
        """Get all items for a specific bidder."""
        return self.bidder_items.get(bidder_name, [])

    def get_item_by_number(self, item_no: str) -> Optional[BidItem]:
        """Get a specific item by item number."""
        for item in self.items:
            if item.item_no == item_no:
                return item
        return None

    def total_by_bidder(self, bidder_name: str) -> float:
        """Get total bid amount for a bidder."""
        bidder = next((b for b in self.bidders.values() if b.name == bidder_name), None)
        return bidder.bid_total if bidder else 0.0


class PDFContent(BaseModel):
    """Extracted content from a PDF document."""

    filename: str = Field(..., description="PDF filename")
    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    content: str = Field(..., description="Extracted text content")
    is_scanned: bool = Field(default=False, description="Whether content came from OCR")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="OCR confidence if scanned")


class DataQualityReport(BaseModel):
    """Report of data quality issues found during parsing."""

    warnings: list[str] = Field(default_factory=list, description="Non-fatal issues")
    missing_fields: dict[str, int] = Field(default_factory=dict, description="Field: count of missing")
    inconsistencies: list[str] = Field(default_factory=list, description="Data type or value issues")

    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return bool(self.warnings or self.missing_fields or self.inconsistencies)
