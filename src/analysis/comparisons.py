"""
Bidder and item comparison functions.

Compare prices across bidders, analyze bidder strategies.
"""

import logging
import statistics
from typing import Optional

from src.data.models import Project, Bidder

logger = logging.getLogger(__name__)


class BidderComparison:
    """Comparison result for a bidder on a specific item."""

    def __init__(
        self,
        bidder_name: str,
        bid_rank: int,
        unit_price: float,
        median_price: float,
        variance: float,
    ):
        self.bidder_name = bidder_name
        self.bid_rank = bid_rank
        self.unit_price = unit_price
        self.median_price = median_price
        self.variance = variance  # Percentage difference from median

    def __repr__(self) -> str:
        return (
            f"BidderComparison({self.bidder_name}: rank={self.bid_rank}, "
            f"price={self.unit_price:.2f}, variance={self.variance:+.1f}%)"
        )


class ComparisonService:
    """Service for comparing bidders and items."""

    @staticmethod
    def compare_bidders_on_item(
        project: Project,
        item_no: str,
    ) -> list[BidderComparison]:
        """
        Compare all bidders on a specific item.

        Args:
            project: Project containing the item and bidders
            item_no: Item number to compare

        Returns:
            List of BidderComparison objects, sorted by price ascending
        """
        comparisons = []

        # Collect all prices for this item from all bidders
        prices = []
        bidder_prices = {}

        for bidder_name, items in project.bidder_items.items():
            for item in items:
                if item.item_no == item_no:
                    prices.append(item.unit_price)
                    bidder_prices[bidder_name] = item.unit_price
                    break

        if not prices:
            return []

        median_price = statistics.median(prices)

        for bidder_name, unit_price in bidder_prices.items():
            bidder = project.bidders.get(bidder_name)
            if not bidder:
                continue

            variance = ((unit_price - median_price) / median_price) * 100 if median_price > 0 else 0.0

            comparison = BidderComparison(
                bidder_name=bidder_name,
                bid_rank=bidder.bid_rank,
                unit_price=unit_price,
                median_price=median_price,
                variance=variance,
            )

            comparisons.append(comparison)

        # Sort by price ascending
        comparisons.sort(key=lambda x: x.unit_price)

        return comparisons

    @staticmethod
    def analyze_bidder(
        project: Project,
        bidder_name: str,
    ) -> dict:
        """
        Analyze a single bidder's bidding strategy.

        Args:
            project: Project
            bidder_name: Name of bidder

        Returns:
            Dict with bidder statistics
        """
        if bidder_name not in project.bidder_items:
            return {}

        items = project.bidder_items[bidder_name]

        if not items:
            return {}

        prices = [item.unit_price for item in items]
        quantities = [item.qty for item in items]
        extended_amounts = [item.ext_amt for item in items]

        bidder = project.bidders.get(bidder_name)

        return {
            "bidder_name": bidder_name,
            "bid_rank": bidder.bid_rank if bidder else None,
            "bid_total": bidder.bid_total if bidder else None,
            "item_count": len(items),
            "avg_price": statistics.mean(prices) if prices else 0.0,
            "median_price": statistics.median(prices) if prices else 0.0,
            "min_price": min(prices) if prices else 0.0,
            "max_price": max(prices) if prices else 0.0,
            "total_quantity": sum(quantities),
            "total_extended_amount": sum(extended_amounts),
        }

    @staticmethod
    def compare_all_bidders(project: Project) -> list[dict]:
        """
        Compare all bidders on the project.

        Returns:
            List of bidder analysis dicts, sorted by bid_rank
        """
        comparisons = []

        for bidder_name in project.bidders.keys():
            analysis = ComparisonService.analyze_bidder(project, bidder_name)
            if analysis:
                comparisons.append(analysis)

        # Sort by bid_rank
        comparisons.sort(key=lambda x: x.get("bid_rank", 999))

        return comparisons

    @staticmethod
    def get_price_variance_for_item(
        project: Project,
        item_no: str,
    ) -> Optional[float]:
        """
        Calculate coefficient of variation for an item's prices across bidders.

        Returns:
            Standard deviation / mean (normalized measure of price variance)
        """
        comparisons = ComparisonService.compare_bidders_on_item(project, item_no)

        if len(comparisons) < 2:
            return None

        prices = [c.unit_price for c in comparisons]
        mean = statistics.mean(prices)

        if mean == 0:
            return None

        stdev = statistics.stdev(prices) if len(prices) > 1 else 0.0

        return stdev / mean

    @staticmethod
    def find_most_competitive_items(
        project: Project,
        limit: int = 5,
    ) -> list[tuple[str, float]]:
        """
        Find items with highest price variance (most competition).

        Returns:
            List of (item_no, coefficient_of_variation) tuples
        """
        variance_by_item = []

        # Get all unique items
        for item in project.items:
            cv = ComparisonService.get_price_variance_for_item(project, item.item_no)
            if cv is not None:
                variance_by_item.append((item.item_no, cv))

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique = []
        for item_no, cv in variance_by_item:
            if item_no not in seen:
                seen.add(item_no)
                unique.append((item_no, cv))

        # Sort by variance descending (highest competition)
        unique.sort(key=lambda x: x[1], reverse=True)

        return unique[:limit]

    @staticmethod
    def rank_bidders_on_item(
        project: Project,
        item_no: str,
        metric: str = "price",
    ) -> list[tuple[str, float, int]]:
        """
        Rank bidders on a specific item by price.

        Args:
            project: Project
            item_no: Item to rank by
            metric: "price" (unit_price) or "total" (extended amount)

        Returns:
            List of (bidder_name, metric_value, rank) tuples
        """
        if metric not in ["price", "total"]:
            raise ValueError(f"Unknown metric: {metric}")

        comparisons = ComparisonService.compare_bidders_on_item(project, item_no)

        if not comparisons:
            return []

        ranked = []

        for rank, comparison in enumerate(comparisons, start=1):
            value = comparison.unit_price if metric == "price" else comparison.unit_price
            ranked.append((comparison.bidder_name, value, rank))

        return ranked
