"""Item aggregation tool definitions."""

from pydantic import BaseModel, Field


class AggregateItemsInput(BaseModel):
    """Input for aggregation (top items, statistics)."""

    metric: str = Field(
        default="unit_price",
        description="Metric to aggregate: unit_price, qty, ext_amt",
        examples=["unit_price", "qty", "ext_amt"]
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of top items to return"
    )
    order: str = Field(
        default="desc",
        description="Sort order: desc (highest first) or asc (lowest first)"
    )


class AggregateItemsOutput(BaseModel):
    """Output from aggregation."""

    count: int = Field(..., description="Number of items analyzed")
    top_items: list[dict] = Field(
        ...,
        description="List of (item_no, item_desc, metric_value) tuples"
    )
    interpretation: str = Field(
        ...,
        description="Summary of top items"
    )
