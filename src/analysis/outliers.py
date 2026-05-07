"""
Outlier detection for bid data analysis.

Supports Z-score and IQR methods for detecting anomalous values.
"""

import logging
import statistics
from typing import Optional
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class OutlierMethod(str, Enum):
    """Outlier detection method."""

    ZSCORE = "zscore"
    IQR = "iqr"


class Outlier:
    """Represents a detected outlier."""

    def __init__(
        self,
        value: float,
        index: int,
        zscore: Optional[float] = None,
        percentile: Optional[float] = None,
        description: str = "",
    ):
        self.value = value
        self.index = index
        self.zscore = zscore
        self.percentile = percentile
        self.description = description

    def __repr__(self) -> str:
        return f"Outlier(value={self.value}, zscore={self.zscore}, description='{self.description}')"


class OutlierDetector:
    """Detect outliers in numerical data."""

    @staticmethod
    def detect_outliers(
        values: list[float],
        method: OutlierMethod = OutlierMethod.ZSCORE,
        sensitivity: float = 2.0,
    ) -> list[Outlier]:
        """
        Detect outliers in a list of values.

        Args:
            values: Numerical data to analyze
            method: Detection method (zscore or iqr)
            sensitivity: Threshold for outlier detection
                - Z-score: flag if |z| > sensitivity (default 2.0σ)
                - IQR: flag if value < Q1 - sensitivity*IQR or > Q3 + sensitivity*IQR

        Returns:
            List of Outlier objects
        """
        if not values or len(values) < 3:
            return []

        # Filter out NaN/inf values
        clean_values = [v for v in values if isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v)]

        if len(clean_values) < 3:
            return []

        if method == OutlierMethod.ZSCORE:
            return OutlierDetector._detect_zscore(clean_values, sensitivity)
        elif method == OutlierMethod.IQR:
            return OutlierDetector._detect_iqr(clean_values, sensitivity)
        else:
            raise ValueError(f"Unknown method: {method}")

    @staticmethod
    def _detect_zscore(values: list[float], threshold: float = 2.0) -> list[Outlier]:
        """Detect outliers using Z-score method."""
        if len(set(values)) == 1:  # All values equal
            return []

        try:
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
        except (ValueError, statistics.StatisticsError):
            return []

        if stdev == 0:
            return []

        outliers = []

        for idx, value in enumerate(values):
            zscore = (value - mean) / stdev

            if abs(zscore) > threshold:
                percentile = OutlierDetector._calculate_percentile(values, value)
                description = f"{abs(zscore):.2f}σ {'above' if zscore > 0 else 'below'} mean"

                outliers.append(
                    Outlier(
                        value=value,
                        index=idx,
                        zscore=zscore,
                        percentile=percentile,
                        description=description,
                    )
                )

        return sorted(outliers, key=lambda x: abs(x.zscore), reverse=True)

    @staticmethod
    def _detect_iqr(values: list[float], multiplier: float = 1.5) -> list[Outlier]:
        """Detect outliers using Interquartile Range (IQR) method."""
        if len(set(values)) == 1:  # All values equal
            return []

        sorted_values = sorted(values)
        n = len(sorted_values)

        # Calculate quartiles
        q1_idx = n // 4
        q3_idx = (3 * n) // 4

        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        outliers = []

        for idx, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                percentile = OutlierDetector._calculate_percentile(values, value)
                location = "below lower bound" if value < lower_bound else "above upper bound"
                description = f"{location} (IQR method)"

                outliers.append(
                    Outlier(
                        value=value,
                        index=idx,
                        percentile=percentile,
                        description=description,
                    )
                )

        return sorted(outliers, key=lambda x: x.value, reverse=True)

    @staticmethod
    def _calculate_percentile(values: list[float], value: float) -> float:
        """Calculate what percentile a value is in."""
        below = sum(1 for v in values if v < value)
        return (below / len(values)) * 100


def detect_price_outliers(
    prices: list[float],
    item_type: str = "",
    method: str = "zscore",
    sensitivity: float = 2.0,
) -> dict:
    """
    Convenience function to detect price outliers.

    Returns:
        Dict with outliers, mean, median, stdev
    """
    if not prices:
        return {
            "outliers": [],
            "mean": 0.0,
            "median": 0.0,
            "stdev": 0.0,
            "count": 0,
        }

    clean_prices = [p for p in prices if isinstance(p, (int, float)) and p > 0]

    if len(clean_prices) < 3:
        return {
            "outliers": [],
            "mean": statistics.mean(clean_prices) if clean_prices else 0.0,
            "median": statistics.median(clean_prices) if clean_prices else 0.0,
            "stdev": 0.0,
            "count": len(clean_prices),
        }

    method_enum = OutlierMethod.ZSCORE if method == "zscore" else OutlierMethod.IQR
    outliers = OutlierDetector.detect_outliers(clean_prices, method=method_enum, sensitivity=sensitivity)

    return {
        "outliers": outliers,
        "mean": statistics.mean(clean_prices),
        "median": statistics.median(clean_prices),
        "stdev": statistics.stdev(clean_prices) if len(clean_prices) > 1 else 0.0,
        "count": len(clean_prices),
        "item_type": item_type,
    }
