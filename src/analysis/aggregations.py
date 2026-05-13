"""
Aggregation and statistical functions for bid data.

Compute summary statistics, ranking, and grouping.
"""

import logging
import statistics
from typing import Optional
from collections import defaultdict

from src.data.models import Project, BidItem

logger = logging.getLogger(__name__)


class BidStatistics:
    """Summary statistics for a group of values."""

    def __init__(
        self,
        values: list[float],
        label: str = "",
    ):
        self.label = label
        self.count = len(values)

        if self.count == 0:
            self.mean = 0.0
            self.median = 0.0
            self.stdev = 0.0
            self.min = 0.0
            self.max = 0.0
            return

        self.mean = statistics.mean(values)
        self.median = statistics.median(values)
        self.min = min(values)
        self.max = max(values)

        if self.count > 1:
            self.stdev = statistics.stdev(values)
        else:
            self.stdev = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "mean": self.mean,
            "median": self.median,
            "stdev": self.stdev,
            "min": self.min,
            "max": self.max,
        }

    def __repr__(self) -> str:
        return (
            f"Stats({self.label}): count={self.count}, mean={self.mean:.2f}, "
            f"median={self.median:.2f}, stdev={self.stdev:.2f}"
        )


class AggregationService:
    """Aggregation and analysis operations on bid data."""

    @staticmethod
    def get_top_items(
        projects: list[Project],
        metric: str = "unit_price",
        limit: int = 5,
        order: str = "desc",
    ) -> list[tuple[str, str, float]]:
        """
        Get top bid items by metric.

        Args:
            projects: List of projects
            metric: "unit_price", "qty", or "ext_amt"
            limit: Number of top items to return
            order: "desc" (highest first) or "asc" (lowest first)

        Returns:
            List of (item_no, item_desc, metric_value) tuples
        """
        items = []

        for project in projects:
            for item in project.items:
                value = getattr(item, metric, 0.0)
                items.append((item.item_no, item.item_desc, value))

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_items = []
        for item in items:
            key = (item[0], item[1])  # (item_no, item_desc)
            if key not in seen:
                seen.add(key)
                unique_items.append(item)

        # Sort
        reverse = order == "desc"
        unique_items.sort(key=lambda x: x[2], reverse=reverse)

        return unique_items[:limit]

    @staticmethod
    def compute_item_statistics(
        projects: list[Project],
        item_no: str,
    ) -> Optional[BidStatistics]:
        """
        Compute statistics for a specific item across all bidders.

        Args:
            projects: List of projects
            item_no: Item number to analyze

        Returns:
            BidStatistics with aggregated data
        """
        prices = []

        for project in projects:
            item = project.get_item_by_number(item_no)
            if item:
                prices.append(item.unit_price)

        if not prices:
            return None

        return BidStatistics(prices, label=item_no)

    @staticmethod
    def compute_category_statistics(
        projects: list[Project],
        category_prefix: str,
    ) -> Optional[BidStatistics]:
        """
        Compute statistics for items matching a category prefix.

        Args:
            projects: List of projects
            category_prefix: Prefix to match (e.g., "ASPHALT", "EXCAVATION")

        Returns:
            BidStatistics for matching items
        """
        prices = []

        for project in projects:
            for item in project.items:
                if category_prefix.upper() in item.item_desc.upper():
                    prices.append(item.unit_price)

        if not prices:
            return None

        return BidStatistics(prices, label=category_prefix)

    @staticmethod
    def group_by_item_type(projects: list[Project]) -> dict[str, list[BidItem]]:
        """
        Group items by item description.

        Returns:
            Dict mapping item_desc → list of BidItem objects
        """
        groups = defaultdict(list)

        for project in projects:
            for item in project.items:
                groups[item.item_desc].append(item)

        return dict(groups)

    @staticmethod
    def summarize_project(project: Project) -> dict:
        """
        Create a summary of a project.

        Returns:
            Dict with project stats
        """
        if not project.items:
            return {
                "proj_id": project.proj_id,
                "bidder_count": len(project.bidders),
                "item_count": 0,
                "total_qty": 0.0,
                "total_value": 0.0,
            }

        total_qty = sum(item.qty for item in project.items)
        total_value = sum(item.ext_amt for item in project.items)

        return {
            "proj_id": project.proj_id,
            "bidder_count": len(project.bidders),
            "item_count": len(project.items),
            "total_qty": total_qty,
            "total_value": total_value,
            "avg_item_price": total_value / len(project.items) if project.items else 0.0,
        }

    @staticmethod
    def get_median_item_price(
        projects: list[Project],
        item_type_pattern: str = "",
    ) -> Optional[float]:
        """
        Get median price for items matching pattern.

        Args:
            projects: List of projects
            item_type_pattern: Pattern to match in item description (case-insensitive)

        Returns:
            Median unit price or None if no matches
        """
        prices = []

        for project in projects:
            for item in project.items:
                if not item_type_pattern or item_type_pattern.upper() in item.item_desc.upper():
                    prices.append(item.unit_price)

        if not prices:
            return None

        return statistics.median(prices)

    @staticmethod
    def get_price_range(
        projects: list[Project],
        item_type_pattern: str = "",
    ) -> Optional[tuple[float, float]]:
        """
        Get min and max prices for items matching pattern.

        Returns:
            (min_price, max_price) or None if no matches
        """
        prices = []

        for project in projects:
            for item in project.items:
                if not item_type_pattern or item_type_pattern.upper() in item.item_desc.upper():
                    prices.append(item.unit_price)

        if not prices:
            return None

        return (min(prices), max(prices))

    @staticmethod
    def aggregate_unmapped_field(
        projects: list[Project],
        field_name: str,
        operation: str = "sum",
    ) -> Optional[float]:
        """
        Aggregate an unmapped field across all items.

        Args:
            projects: List of projects
            field_name: Name of the unmapped field
            operation: "sum", "min", "max", "avg", "median"

        Returns:
            Aggregated value or None if field not found or no valid values
        """
        values = []

        for project in projects:
            for item in project.items:
                if field_name in item.unmapped_fields:
                    unmapped = item.unmapped_fields[field_name]

                    # If already parsed as numeric, use it
                    if unmapped.inferred_type == "numeric" and unmapped.parsed_value is not None:
                        values.append(unmapped.parsed_value)
                    # Try to convert string to numeric
                    elif unmapped.inferred_type == "string":
                        try:
                            numeric_val = float(unmapped.raw)
                            values.append(numeric_val)
                        except ValueError:
                            # Skip invalid values
                            pass

        if not values:
            return None

        if operation == "sum":
            return sum(values)
        elif operation == "min":
            return min(values)
        elif operation == "max":
            return max(values)
        elif operation == "avg":
            return statistics.mean(values)
        elif operation == "median":
            return statistics.median(values)

        return None

    @staticmethod
    def compute_unmapped_field_statistics(
        projects: list[Project],
        field_name: str,
    ) -> Optional[BidStatistics]:
        """
        Compute statistics for an unmapped field.

        Args:
            projects: List of projects
            field_name: Name of the unmapped field

        Returns:
            BidStatistics or None if field not found
        """
        values = []

        for project in projects:
            for item in project.items:
                if field_name in item.unmapped_fields:
                    unmapped = item.unmapped_fields[field_name]

                    # If already parsed as numeric, use it
                    if unmapped.inferred_type == "numeric" and unmapped.parsed_value is not None:
                        values.append(unmapped.parsed_value)
                    # Try to convert string to numeric
                    elif unmapped.inferred_type == "string":
                        try:
                            numeric_val = float(unmapped.raw)
                            values.append(numeric_val)
                        except ValueError:
                            # Skip invalid values
                            pass

        if not values:
            return None

        return BidStatistics(values, label=field_name)
