"""
Tests for analysis tools (outliers, aggregations, comparisons).
"""

import pytest
import statistics
from datetime import date

from src.data.models import Project, BidItem, Bidder
from src.analysis.outliers import OutlierDetector, OutlierMethod, detect_price_outliers
from src.analysis.aggregations import AggregationService, BidStatistics
from src.analysis.comparisons import ComparisonService


# ============================================================================
# OUTLIER DETECTION TESTS
# ============================================================================


class TestOutlierDetectionZScore:
    """Tests for Z-score outlier detection."""

    def test_detect_zscore_with_outliers(self):
        """Test Z-score detection finds outliers."""
        values = [10, 11, 10, 11, 12, 11, 10, 100]  # 100 is outlier

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
            sensitivity=2.0,
        )

        assert len(outliers) >= 1
        assert any(o.value == 100 for o in outliers)

    def test_detect_zscore_no_outliers(self):
        """Test Z-score finds no outliers in normal data."""
        values = [100, 101, 102, 103, 104, 105]

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
            sensitivity=2.0,
        )

        assert len(outliers) == 0

    def test_detect_zscore_all_equal(self):
        """Test Z-score with all values equal."""
        values = [100, 100, 100, 100]

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
            sensitivity=2.0,
        )

        assert len(outliers) == 0

    def test_detect_zscore_single_value(self):
        """Test Z-score with single value."""
        values = [100]

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
        )

        assert len(outliers) == 0

    def test_detect_zscore_empty(self):
        """Test Z-score with empty list."""
        values = []

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
        )

        assert len(outliers) == 0

    def test_zscore_sensitivity(self):
        """Test Z-score sensitivity parameter."""
        values = [10, 11, 12, 13, 30]

        # Strict threshold
        strict = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
            sensitivity=1.0,
        )

        # Loose threshold
        loose = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.ZSCORE,
            sensitivity=3.0,
        )

        assert len(strict) >= len(loose)


class TestOutlierDetectionIQR:
    """Tests for IQR outlier detection."""

    def test_detect_iqr_with_outliers(self):
        """Test IQR detection finds outliers."""
        values = [10, 11, 12, 13, 14, 15, 100]  # 100 is outlier

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.IQR,
            sensitivity=1.5,
        )

        assert len(outliers) >= 1
        assert any(o.value == 100 for o in outliers)

    def test_detect_iqr_no_outliers(self):
        """Test IQR with normal data."""
        values = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.IQR,
            sensitivity=1.5,
        )

        assert len(outliers) == 0

    def test_detect_iqr_all_equal(self):
        """Test IQR with all values equal."""
        values = [10, 10, 10, 10]

        outliers = OutlierDetector.detect_outliers(
            values,
            method=OutlierMethod.IQR,
        )

        assert len(outliers) == 0


# ============================================================================
# AGGREGATION TESTS
# ============================================================================


class TestAggregationService:
    """Tests for aggregation functions."""

    @pytest.fixture
    def sample_project(self):
        """Create sample project with items."""
        project = Project(proj_id="0676350", let_dt=date(2026, 3, 10))

        items = [
            BidItem(
                item_no="1031000",
                item_desc="MOBILIZATION",
                unit="LS",
                qty=1.0,
                unit_price=16500.0,
                ext_amt=16500.0,
            ),
            BidItem(
                item_no="1032010",
                item_desc="BONDS AND INSURANCE",
                unit="LS",
                qty=1.0,
                unit_price=800.0,
                ext_amt=800.0,
            ),
            BidItem(
                item_no="4040350",
                item_desc="ASPHALT SURFACE COURSE",
                unit="TON",
                qty=1497.32,
                unit_price=93.9,
                ext_amt=140598.35,
            ),
        ]

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)

        project.items = items
        project.bidders["ABC CONSTRUCTION"] = bidder
        project.bidder_items["ABC CONSTRUCTION"] = items

        return project

    def test_get_top_items_by_price(self, sample_project):
        """Test getting top items by price."""
        top = AggregationService.get_top_items(
            [sample_project],
            metric="unit_price",
            limit=2,
            order="desc",
        )

        assert len(top) <= 2
        # MOBILIZATION should be first (16500 is highest)
        assert top[0][0] == "1031000"

    def test_compute_statistics(self, sample_project):
        """Test computing statistics."""
        stats = BidStatistics([100, 101, 102, 103, 104])

        assert stats.count == 5
        assert stats.mean == 102.0
        assert stats.median == 102.0
        assert stats.min == 100.0
        assert stats.max == 104.0

    def test_compute_item_statistics(self, sample_project):
        """Test computing item statistics."""
        stats = AggregationService.compute_item_statistics(
            [sample_project],
            item_no="1031000",
        )

        assert stats is not None
        assert stats.count == 1
        assert stats.mean == 16500.0

    def test_summarize_project(self, sample_project):
        """Test project summary."""
        summary = AggregationService.summarize_project(sample_project)

        assert summary["proj_id"] == "0676350"
        assert summary["item_count"] == 3
        assert summary["bidder_count"] == 1


# ============================================================================
# COMPARISON TESTS
# ============================================================================


class TestComparisonService:
    """Tests for comparison functions."""

    @pytest.fixture
    def multi_bidder_project(self):
        """Create project with multiple bidders."""
        project = Project(proj_id="0676350")

        item1 = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        bidder1 = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)
        bidder2 = Bidder(name="XYZ CORP", bid_rank=2, bid_total=400000.0)

        project.bidders["ABC CONSTRUCTION"] = bidder1
        project.bidders["XYZ CORP"] = bidder2

        item2 = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=33500.0,
            ext_amt=33500.0,
        )

        project.items = [item1]
        project.bidder_items["ABC CONSTRUCTION"] = [item1]
        project.bidder_items["XYZ CORP"] = [item2]

        return project

    def test_compare_bidders_on_item(self, multi_bidder_project):
        """Test comparing bidders on item."""
        comparisons = ComparisonService.compare_bidders_on_item(
            multi_bidder_project,
            "1031000",
        )

        # Should find at least ABC CONSTRUCTION
        assert len(comparisons) > 0
        assert any(c.bidder_name == "ABC CONSTRUCTION" for c in comparisons)

    def test_analyze_bidder(self, multi_bidder_project):
        """Test analyzing single bidder."""
        analysis = ComparisonService.analyze_bidder(
            multi_bidder_project,
            "ABC CONSTRUCTION",
        )

        assert analysis["bidder_name"] == "ABC CONSTRUCTION"
        assert analysis["bid_rank"] == 1
        assert analysis["item_count"] == 1

    def test_compare_all_bidders(self, multi_bidder_project):
        """Test comparing all bidders."""
        comparisons = ComparisonService.compare_all_bidders(multi_bidder_project)

        assert len(comparisons) >= 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPriceOutliersConvenience:
    """Tests for convenience function."""

    def test_detect_price_outliers(self):
        """Test detect_price_outliers function."""
        prices = [100, 101, 102, 103, 104, 500]  # 500 is outlier

        result = detect_price_outliers(prices, item_type="ASPHALT", method="zscore")

        assert result["count"] == 6
        assert result["mean"] > 0
        assert len(result["outliers"]) >= 1

    def test_detect_price_outliers_empty(self):
        """Test with empty prices."""
        result = detect_price_outliers([], item_type="ASPHALT")

        assert result["count"] == 0
        assert len(result["outliers"]) == 0
