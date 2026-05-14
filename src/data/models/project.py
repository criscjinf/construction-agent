from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from src.data.models.bidder import Bidder
from src.data.models.bid_item import BidItem


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
