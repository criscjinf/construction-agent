"""Outlier detection tool definitions."""

from enum import Enum
from typing import Optional
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
