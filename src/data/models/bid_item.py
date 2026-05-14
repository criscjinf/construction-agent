from pydantic import BaseModel, Field, field_validator
from src.data.models.bidder import Bidder
from src.data.models.unmapped_field import UnmappedField


class BidItem(BaseModel):
    """A single line item in a bid tabulation."""

    item_no: str = Field(..., min_length=1, description="Item number (e.g., '1031000')")
    item_desc: str = Field(..., min_length=1, description="Item description")
    unit: str = Field(..., min_length=1, description="Unit of measure (e.g., 'LS', 'CY', 'TON')")
    qty: float = Field(..., ge=0, description="Quantity")
    eng_est_unit_pr: float = Field(default=0.0, ge=0, description="Engineer estimate unit price")
    unit_price: float = Field(..., ge=0, description="Bid unit price")
    ext_amt: float = Field(..., ge=0, description="Extended amount (qty × unit_price)")
    unmapped_fields: dict[str, UnmappedField] = Field(
        default_factory=dict, description="Unknown CSV columns with inferred types"
    )

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
            return False
        return True


class BidderItem(BaseModel):
    """A bid item with its bidder context."""

    bidder: Bidder
    item: BidItem
