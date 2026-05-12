"""Bidder comparison tool definitions."""

from typing import Optional
from pydantic import BaseModel, Field


class CompareBiddersInput(BaseModel):
    """Input for bidder comparison on a specific item."""

    item_no: str = Field(
        ...,
        description="Item number to compare (e.g., '1031000')",
        examples=["1031000", "4040350"]
    )


class CompareBiddersOutput(BaseModel):
    """Output from bidder comparison."""

    item_no: str = Field(..., description="Item being compared")
    item_desc: Optional[str] = Field(default=None, description="Item description")
    bidder_count: int = Field(..., description="Number of bidders on this item")
    median_price: float = Field(..., description="Median unit price across bidders")
    comparisons: list[dict] = Field(
        ...,
        description="List of bidders with prices, ranks, variance from median"
    )
    most_competitive: bool = Field(
        ...,
        description="True if high variance (competitive), False if tight pricing"
    )
    interpretation: str = Field(
        ...,
        description="Analysis of bidder competition on this item"
    )
