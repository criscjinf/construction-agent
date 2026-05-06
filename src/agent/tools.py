"""
Tool definitions for Claude agent (Pydantic models with JSON schemas).

Tools enable Claude to call Python functions for construction bid analysis:
- Outlier detection (prices deviating from mean)
- Item aggregation (top-N by metric)
- Bidder comparisons (price analysis across bidders)
- Semantic search (vector embeddings + keyword)
"""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class OutlierMethodEnum(str, Enum):
    """Outlier detection method."""
    ZSCORE = "zscore"
    IQR = "iqr"


class DetectOutliersInput(BaseModel):
    """Input for outlier detection tool."""

    prices: list[float] = Field(
        ...,
        description="List of prices (unit prices or extended amounts)",
        examples=[[100, 101, 102, 103, 500]]
    )
    method: OutlierMethodEnum = Field(
        default=OutlierMethodEnum.ZSCORE,
        description="Detection method: zscore or iqr"
    )
    sensitivity: float = Field(
        default=2.0,
        ge=0.5,
        le=5.0,
        description="Outlier threshold (higher = stricter). Z-score default 2.0σ, IQR default 1.5x"
    )
    item_type: Optional[str] = Field(
        default=None,
        description="Item type/category (for context in response)"
    )


class DetectOutliersOutput(BaseModel):
    """Output from outlier detection."""

    count: int = Field(..., description="Number of prices analyzed")
    mean: float = Field(..., description="Mean price")
    median: float = Field(..., description="Median price")
    stdev: float = Field(..., description="Standard deviation")
    outlier_count: int = Field(..., description="Number of outliers detected")
    outliers: list[dict] = Field(
        ...,
        description="List of outliers with value, z-score, percentile, description"
    )
    interpretation: str = Field(
        ...,
        description="Human-readable interpretation of outliers"
    )


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


class SearchInput(BaseModel):
    """Input for semantic + keyword search."""

    query: str = Field(
        ...,
        description="Natural language search query",
        examples=["drainage requirements", "asphalt paving costs", "mobilization"]
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return"
    )
    threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )


class SearchOutput(BaseModel):
    """Output from search."""

    query: str = Field(..., description="Original search query")
    result_count: int = Field(..., description="Number of results found")
    results: list[dict] = Field(
        ...,
        description="List of results with content, source, similarity score"
    )
    interpretation: str = Field(
        ...,
        description="Summary of search results"
    )


class ToolDefinition(BaseModel):
    """Definition of a tool for Claude to call."""

    name: str
    description: str
    input_schema: dict


def get_tool_definitions() -> list[ToolDefinition]:
    """
    Return list of tool definitions for Claude agent.

    Each tool corresponds to a function the agent can call.
    Claude will invoke these based on the user query.
    """
    return [
        ToolDefinition(
            name="detect_outliers",
            description="Detect outlier prices using Z-score or IQR method. Returns statistics and outlier details.",
            input_schema=DetectOutliersInput.model_json_schema()
        ),
        ToolDefinition(
            name="aggregate_items",
            description="Get top bid items by metric (unit_price, qty, ext_amt). Useful for 'top 5 most expensive' queries.",
            input_schema=AggregateItemsInput.model_json_schema()
        ),
        ToolDefinition(
            name="compare_bidders",
            description="Compare prices of all bidders on a specific item. Shows competition level and outliers.",
            input_schema=CompareBiddersInput.model_json_schema()
        ),
        ToolDefinition(
            name="search",
            description="Search bid data and PDF content using semantic + keyword search. Find items, costs, requirements.",
            input_schema=SearchInput.model_json_schema()
        ),
    ]
