from pydantic import BaseModel, Field


class Bidder(BaseModel):
    """A company submitting a bid."""

    name: str = Field(..., min_length=1, description="Bidder company name")
    bid_rank: int = Field(..., gt=0, description="Ranking in bid competition (1 = lowest)")
    bid_total: float = Field(..., ge=0, description="Total bid amount in dollars")

    class Config:
        frozen = True
