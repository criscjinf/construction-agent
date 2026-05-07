"""
Tests for data validators.
"""

import pytest
from datetime import date
from pydantic import ValidationError

from src.data.models import Project, BidItem, Bidder
from src.data.validators import DataValidator, check_data_quality


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_validate_valid_project(self):
        """Test validating a properly formed project."""
        project = Project(proj_id="0676350", let_dt=date(2026, 3, 10))

        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)

        project.items.append(item)
        project.bidders["ABC CONSTRUCTION"] = bidder
        project.bidder_items["ABC CONSTRUCTION"] = [item]

        report = DataValidator.validate_project(project)

        # Valid project should have no issues
        assert not report.has_issues()

    def test_validate_project_missing_bidders(self):
        """Test validating project with no bidders."""
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

        report = DataValidator.validate_project(project)

        assert report.has_issues()
        assert any("No bidders" in w for w in report.warnings)

    def test_validate_project_missing_items(self):
        """Test validating project with no items."""
        project = Project(proj_id="0676350")

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)
        project.bidders["ABC CONSTRUCTION"] = bidder

        report = DataValidator.validate_project(project)

        assert report.has_issues()
        assert any("No items" in w for w in report.warnings)

    def test_validate_item_negative_qty(self):
        """Test validating item with negative quantity."""
        # Pydantic should reject negative qty before validator sees it
        with pytest.raises(ValidationError):
            BidItem(
                item_no="1031000",
                item_desc="MOBILIZATION",
                unit="LS",
                qty=-1.0,  # Invalid
                unit_price=16500.0,
                ext_amt=-16500.0,
            )

    def test_validate_item_with_empty_fields(self):
        """Test validating item with empty description."""
        # Pydantic rejects empty descriptions
        with pytest.raises(ValidationError):
            BidItem(
                item_no="1031000",
                item_desc="",  # Empty - rejected by Pydantic
                unit="LS",
                qty=1.0,
                unit_price=16500.0,
                ext_amt=16500.0,
            )

    def test_validate_item_inconsistent_ext_amt(self):
        """Test validating item with inconsistent extended amount."""
        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=2.0,
            unit_price=100.0,
            ext_amt=150.0,  # Should be 200.0 (2 × 100)
        )

        report = DataValidator.validate_item(item)

        assert report.has_issues()
        assert any("ext_amt" in inc for inc in report.inconsistencies)

    def test_validate_bidder_with_invalid_rank(self):
        """Test validating bidder with invalid rank."""
        # Pydantic should reject negative rank
        with pytest.raises(ValidationError):
            Bidder(
                name="ABC CONSTRUCTION",
                bid_rank=-1,  # Invalid
                bid_total=337288.86,
            )

    def test_validate_bidder_negative_total(self):
        """Test validating bidder with negative total."""
        # Pydantic should reject negative bid_total
        with pytest.raises(ValidationError):
            Bidder(
                name="ABC CONSTRUCTION",
                bid_rank=1,
                bid_total=-100.0,  # Invalid
            )

    def test_validate_multiple_projects(self):
        """Test validating multiple projects."""
        project1 = Project(proj_id="0676350")
        project2 = Project(proj_id="5275280")

        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        project1.items.append(item)
        project2.items.append(item)

        reports = DataValidator.validate_projects([project1, project2])

        assert "0676350" in reports
        assert "5275280" in reports

    def test_check_data_quality_pass(self):
        """Test check_data_quality with valid data."""
        project = Project(proj_id="0676350")

        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=16500.0,
            ext_amt=16500.0,
        )

        bidder = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)

        project.items.append(item)
        project.bidders["ABC CONSTRUCTION"] = bidder
        project.bidder_items["ABC CONSTRUCTION"] = [item]

        result = check_data_quality([project])

        assert result is True

    def test_check_data_quality_fail(self):
        """Test check_data_quality with invalid data."""
        project = Project(proj_id="0676350")

        # Create item with invalid calculation
        item = BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=2.0,
            unit_price=100.0,
            ext_amt=100.0,  # Wrong: should be 200
        )

        project.items.append(item)

        result = check_data_quality([project])

        # Should fail due to inconsistency
        assert result is False
