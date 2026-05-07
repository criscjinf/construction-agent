"""
Tests for Pydantic data models.
"""

import pytest
from datetime import date

from src.data.models import BidItem, Bidder, Project


class TestBidItem:
    """Tests for BidItem model."""

    def test_biditem_creation_valid(self):
        """Test creating valid BidItem."""
        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        assert item.item_no == "1031000"
        assert item.item_desc == "MOBILIZATION"
        assert item.qty == 1.0

    def test_biditem_negative_qty_rejected(self):
        """Test BidItem rejects negative quantity."""
        with pytest.raises(ValueError):
            BidItem(
                item_no="1031000",
                item_desc="MOBILIZATION",
                unit="LS",
                qty=-1.0,
                unit_price=16500.0,
                ext_amt=-16500.0,
            )

    def test_biditem_negative_price_rejected(self):
        """Test BidItem rejects negative price."""
        with pytest.raises(ValueError):
            BidItem(
                item_no="1031000",
                item_desc="MOBILIZATION",
                unit="LS",
                qty=1.0,
                unit_price=-100.0,
                ext_amt=-100.0,
            )

    def test_biditem_is_reasonable_valid(self):
        """Test is_reasonable() for valid item."""
        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        assert item.is_reasonable()

    def test_biditem_with_zero_values(self):
        """Test BidItem with zero quantity."""
        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=0.0,
            unit_price=16500.0,
            ext_amt=0.0,
        )

        assert item.is_reasonable()


class TestBidder:
    """Tests for Bidder model."""

    def test_bidder_creation_valid(self):
        """Test creating valid Bidder."""
        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)

        assert bidder.name == "ABC CONSTRUCTION"
        assert bidder.bid_rank == 1
        assert bidder.bid_total == 337288.86

    def test_bidder_rejects_invalid_rank(self):
        """Test Bidder rejects invalid bid_rank."""
        with pytest.raises(ValueError):
            Bidder(name="ABC CONSTRUCTION", bid_rank=0, bid_total=337288.86)

        with pytest.raises(ValueError):
            Bidder(name="ABC CONSTRUCTION", bid_rank=-1, bid_total=337288.86)

    def test_bidder_rejects_negative_total(self):
        """Test Bidder rejects negative bid_total."""
        with pytest.raises(ValueError):
            Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=-100.0)

    def test_bidder_frozen(self):
        """Test Bidder is frozen (immutable)."""
        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)

        with pytest.raises(Exception):  # Pydantic frozen raises ValidationError
            bidder.name = "XYZ CORP"


class TestProject:
    """Tests for Project model."""

    def test_project_creation(self):
        """Test creating Project."""
        project = Project(proj_id="0676350", let_dt=date(2026, 3, 10), county="Barnwell")

        assert project.proj_id == "0676350"
        assert project.let_dt == date(2026, 3, 10)
        assert project.county == "Barnwell"
        assert len(project.items) == 0

    def test_project_add_items(self):
        """Test adding items to Project."""
        project = Project(proj_id="0676350")

        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        project.items.append(item)

        assert len(project.items) == 1
        assert project.items[0].item_no == "1031000"

    def test_project_add_bidders(self):
        """Test adding bidders to Project."""
        project = Project(proj_id="0676350")

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)
        project.bidders["ABC CONSTRUCTION"] = bidder

        assert "ABC CONSTRUCTION" in project.bidders
        assert project.bidders["ABC CONSTRUCTION"].bid_total == 337288.86

    def test_project_get_item_by_number(self):
        """Test get_item_by_number method."""
        project = Project(proj_id="0676350")

        item1 = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        item2 = BidItem(
            item_no="1032010",
            item_desc="BONDS AND INSURANCE",
            unit="LS",
            qty=1.0,
            unit_price=800.0,
            ext_amt=800.0,
        )

        project.items.append(item1)
        project.items.append(item2)

        found = project.get_item_by_number("1032010")
        assert found is not None
        assert found.item_desc == "BONDS AND INSURANCE"

        not_found = project.get_item_by_number("9999999")
        assert not_found is None

    def test_project_total_by_bidder(self):
        """Test total_by_bidder method."""
        project = Project(proj_id="0676350")

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)
        project.bidders["ABC CONSTRUCTION"] = bidder

        total = project.total_by_bidder("ABC CONSTRUCTION")
        assert total == 337288.86

        total_unknown = project.total_by_bidder("UNKNOWN CORP")
        assert total_unknown == 0.0
