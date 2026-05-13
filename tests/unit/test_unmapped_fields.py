"""Tests for unmapped field detection and aggregation."""

import pytest
import pandas as pd
from io import StringIO

from src.data.parsers import CSVParser
from src.data.models import UnmappedField
from src.data.converters import ValueConverter
from src.analysis.aggregations import AggregationService


class TestValueConverterDetectType:
    """Test type detection for unmapped fields."""

    def test_detect_numeric_integer(self):
        """Should detect integer as numeric."""
        assert ValueConverter.detect_type("123") == "numeric"

    def test_detect_numeric_float(self):
        """Should detect float as numeric."""
        assert ValueConverter.detect_type("123.45") == "numeric"

    def test_detect_numeric_negative(self):
        """Should detect negative numbers as numeric."""
        assert ValueConverter.detect_type("-456.78") == "numeric"

    def test_detect_date(self):
        """Should detect dates."""
        assert ValueConverter.detect_type("2026-05-13") == "date"
        assert ValueConverter.detect_type("05/13/2026") == "date"

    def test_detect_string(self):
        """Should detect strings."""
        assert ValueConverter.detect_type("ASPHALT PAVING") == "string"
        assert ValueConverter.detect_type("abc123xyz") == "string"

    def test_detect_empty_string(self):
        """Should treat empty string as string."""
        assert ValueConverter.detect_type("") == "string"

    def test_detect_none(self):
        """Should treat None as string."""
        assert ValueConverter.detect_type(None) == "string"


class TestUnmappedFieldModel:
    """Test UnmappedField model."""

    def test_unmapped_field_numeric(self):
        """Should store numeric field correctly."""
        field = UnmappedField(raw="123.45", inferred_type="numeric", parsed_value=123.45)
        assert field.get_numeric_value() == 123.45
        assert field.get_string_value() == "123.45"

    def test_unmapped_field_string(self):
        """Should store string field correctly."""
        field = UnmappedField(raw="ASPHALT", inferred_type="string", parsed_value=None)
        assert field.get_numeric_value() is None
        assert field.get_string_value() == "ASPHALT"

    def test_unmapped_field_date(self):
        """Should store date field correctly."""
        field = UnmappedField(raw="2026-05-13", inferred_type="date", parsed_value=None)
        assert field.get_string_value() == "2026-05-13"


class TestCSVParserUnmappedFields:
    """Test CSV parser with unmapped fields."""

    def test_parse_csv_with_unmapped_columns(self):
        """Should capture unmapped columns in BidItem."""
        csv_data = """PROJ_ID,ITEM_NO,ITEM_DESC,UNIT,QTY,UNIT_PR,EXT_AMT,BIDDER,CUSTOM_COST,NOTES
001,1001,EXCAVATION,CY,100,25.50,2550.00,Bidder A,1500,Good quality
001,1002,PAVING,TON,50,75.00,3750.00,Bidder A,2000,Standard paving
"""
        parser = CSVParser()
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            projects = parser.parse(f.name)

            assert len(projects) == 1
            project = projects[0]
            assert len(project.items) == 2

            # Check first item
            item1 = project.items[0]
            assert "CUSTOM_COST" in item1.unmapped_fields
            assert "NOTES" in item1.unmapped_fields

            # CUSTOM_COST should be numeric
            custom_cost = item1.unmapped_fields["CUSTOM_COST"]
            assert custom_cost.inferred_type == "numeric"
            assert custom_cost.raw == "1500"
            assert custom_cost.parsed_value == 1500.0

            # NOTES should be string
            notes = item1.unmapped_fields["NOTES"]
            assert notes.inferred_type == "string"
            assert notes.raw == "Good quality"
            assert notes.parsed_value is None

    def test_parse_csv_with_no_unmapped_columns(self):
        """Should handle CSV with no unmapped columns."""
        csv_data = """PROJ_ID,ITEM_NO,ITEM_DESC,UNIT,QTY,UNIT_PR,EXT_AMT,BIDDER
001,1001,EXCAVATION,CY,100,25.50,2550.00,Bidder A
"""
        parser = CSVParser()
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            projects = parser.parse(f.name)

            assert len(projects) == 1
            item = projects[0].items[0]
            assert len(item.unmapped_fields) == 0


class TestAggregationServiceUnmappedFields:
    """Test aggregation of unmapped fields."""

    def test_aggregate_unmapped_numeric_sum(self):
        """Should sum numeric unmapped field."""
        from src.data.models import Project, BidItem, Bidder

        item1 = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
            unmapped_fields={
                "COST": UnmappedField(
                    raw="1500", inferred_type="numeric", parsed_value=1500.0
                )
            },
        )

        item2 = BidItem(
            item_no="2",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=200,
            ext_amt=200,
            unmapped_fields={
                "COST": UnmappedField(
                    raw="2500", inferred_type="numeric", parsed_value=2500.0
                )
            },
        )

        project = Project(proj_id="001")
        project.items = [item1, item2]

        result = AggregationService.aggregate_unmapped_field(
            [project], "COST", operation="sum"
        )

        assert result == 4000.0

    def test_aggregate_unmapped_field_avg(self):
        """Should compute average of unmapped field."""
        from src.data.models import Project, BidItem

        item1 = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
            unmapped_fields={
                "SCORE": UnmappedField(
                    raw="80", inferred_type="numeric", parsed_value=80.0
                )
            },
        )

        item2 = BidItem(
            item_no="2",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=200,
            ext_amt=200,
            unmapped_fields={
                "SCORE": UnmappedField(
                    raw="90", inferred_type="numeric", parsed_value=90.0
                )
            },
        )

        project = Project(proj_id="001")
        project.items = [item1, item2]

        result = AggregationService.aggregate_unmapped_field(
            [project], "SCORE", operation="avg"
        )

        assert result == 85.0

    def test_compute_unmapped_field_statistics(self):
        """Should compute statistics for unmapped field."""
        from src.data.models import Project, BidItem

        item1 = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
            unmapped_fields={
                "VALUE": UnmappedField(
                    raw="100", inferred_type="numeric", parsed_value=100.0
                )
            },
        )

        item2 = BidItem(
            item_no="2",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=200,
            ext_amt=200,
            unmapped_fields={
                "VALUE": UnmappedField(
                    raw="200", inferred_type="numeric", parsed_value=200.0
                )
            },
        )

        item3 = BidItem(
            item_no="3",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=300,
            ext_amt=300,
            unmapped_fields={
                "VALUE": UnmappedField(
                    raw="300", inferred_type="numeric", parsed_value=300.0
                )
            },
        )

        project = Project(proj_id="001")
        project.items = [item1, item2, item3]

        stats = AggregationService.compute_unmapped_field_statistics(
            [project], "VALUE"
        )

        assert stats is not None
        assert stats.count == 3
        assert stats.min == 100.0
        assert stats.max == 300.0
        assert stats.mean == 200.0
        assert stats.median == 200.0

    def test_aggregate_unmapped_field_missing(self):
        """Should return None if field not found."""
        from src.data.models import Project, BidItem

        item = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
        )

        project = Project(proj_id="001")
        project.items = [item]

        result = AggregationService.aggregate_unmapped_field(
            [project], "MISSING_FIELD", operation="sum"
        )

        assert result is None

    def test_aggregate_unmapped_string_to_numeric_conversion(self):
        """Should convert string to numeric in aggregation."""
        from src.data.models import Project, BidItem

        item1 = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
            unmapped_fields={
                "COST": UnmappedField(raw="1500", inferred_type="string", parsed_value=None)
            },
        )

        item2 = BidItem(
            item_no="2",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=200,
            ext_amt=200,
            unmapped_fields={
                "COST": UnmappedField(raw="2500", inferred_type="string", parsed_value=None)
            },
        )

        project = Project(proj_id="001")
        project.items = [item1, item2]

        result = AggregationService.aggregate_unmapped_field(
            [project], "COST", operation="sum"
        )

        assert result == 4000.0

    def test_aggregate_unmapped_field_invalid_numeric_skip(self):
        """Should skip invalid numeric values in aggregation."""
        from src.data.models import Project, BidItem

        item1 = BidItem(
            item_no="1",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=100,
            ext_amt=100,
            unmapped_fields={
                "COST": UnmappedField(raw="1500", inferred_type="numeric", parsed_value=1500.0)
            },
        )

        item2 = BidItem(
            item_no="2",
            item_desc="TEST",
            unit="EA",
            qty=1,
            unit_price=200,
            ext_amt=200,
            unmapped_fields={
                "COST": UnmappedField(
                    raw="INVALID", inferred_type="string", parsed_value=None
                )
            },
        )

        project = Project(proj_id="001")
        project.items = [item1, item2]

        result = AggregationService.aggregate_unmapped_field(
            [project], "COST", operation="sum"
        )

        # Should only count the valid numeric value
        assert result == 1500.0
