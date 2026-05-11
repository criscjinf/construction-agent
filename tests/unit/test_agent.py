"""
Unit tests for agent tools and schemas.

Validates that tool definitions are properly structured for Claude API.
"""

import pytest
import json
from src.agent.tools import (
    DetectOutliersInput,
    DetectOutliersOutput,
    AggregateItemsInput,
    CompareBiddersInput,
    SearchInput,
    OutlierMethodEnum,
    get_tool_definitions,
)


class TestDetectOutliersSchema:
    """Tests for outlier detection tool schema."""

    def test_detect_outliers_input_valid(self):
        """Test valid outlier detection input."""
        inp = DetectOutliersInput(
            prices=[100, 101, 102, 103, 500],
            method=OutlierMethodEnum.ZSCORE,
            sensitivity=2.0,
            item_type="ASPHALT"
        )

        assert inp.prices == [100, 101, 102, 103, 500]
        assert inp.method == OutlierMethodEnum.ZSCORE
        assert inp.sensitivity == 2.0
        assert inp.item_type == "ASPHALT"

    def test_detect_outliers_input_default_method(self):
        """Test default method is ZSCORE."""
        inp = DetectOutliersInput(prices=[1, 2, 3])

        assert inp.method == OutlierMethodEnum.ZSCORE
        assert inp.sensitivity == 2.0

    def test_detect_outliers_input_iqr_method(self):
        """Test IQR method option."""
        inp = DetectOutliersInput(
            prices=[1, 2, 3, 4, 5],
            method=OutlierMethodEnum.IQR,
            sensitivity=1.5
        )

        assert inp.method == OutlierMethodEnum.IQR
        assert inp.sensitivity == 1.5

    def test_detect_outliers_input_json_schema(self):
        """Test JSON schema generation."""
        schema = DetectOutliersInput.model_json_schema()

        assert "properties" in schema
        assert "prices" in schema["properties"]
        assert "method" in schema["properties"]
        assert "sensitivity" in schema["properties"]

    def test_detect_outliers_input_serialization(self):
        """Test input can be serialized to JSON."""
        inp = DetectOutliersInput(
            prices=[100, 101, 102],
            method=OutlierMethodEnum.ZSCORE
        )

        json_str = inp.model_dump_json()
        assert "prices" in json_str
        assert "100" in json_str
        assert "zscore" in json_str

    def test_detect_outliers_output_valid(self):
        """Test valid outlier detection output."""
        out = DetectOutliersOutput(
            count=100,
            mean=500.0,
            median=480.0,
            stdev=150.0,
            outlier_count=3,
            outliers=[
                {"value": 1500, "zscore": 6.7, "percentile": 99.5, "description": "3.2σ above mean"},
                {"value": 50, "zscore": -3.0, "percentile": 0.5, "description": "2.1σ below mean"}
            ],
            interpretation="2 high outliers (price anomalies) detected. Recommend bidder review."
        )

        assert out.count == 100
        assert out.mean == 500.0
        assert out.median == 480.0
        assert out.stdev == 150.0
        assert out.outlier_count == 3
        assert len(out.outliers) == 2
        assert "anomalies" in out.interpretation

    def test_detect_outliers_output_json_schema(self):
        """Test JSON schema for output."""
        schema = DetectOutliersOutput.model_json_schema()

        assert "properties" in schema
        assert "count" in schema["properties"]
        assert "mean" in schema["properties"]
        assert "median" in schema["properties"]
        assert "stdev" in schema["properties"]
        assert "outlier_count" in schema["properties"]
        assert "outliers" in schema["properties"]
        assert "interpretation" in schema["properties"]

    def test_detect_outliers_output_serialization(self):
        """Test output can be serialized to JSON."""
        out = DetectOutliersOutput(
            count=50,
            mean=1000.0,
            median=950.0,
            stdev=200.0,
            outlier_count=2,
            outliers=[{"value": 3000, "zscore": 10.0, "percentile": 99.9, "description": "High"}],
            interpretation="Data looks normal"
        )

        json_str = out.model_dump_json()
        assert "count" in json_str
        assert "50" in json_str
        assert "1000" in json_str
        assert "Data looks normal" in json_str


class TestAggregateItemsSchema:
    """Tests for aggregation tool schema."""

    def test_aggregate_items_input_valid(self):
        """Test valid aggregation input."""
        inp = AggregateItemsInput(
            metric="unit_price",
            limit=5,
            order="desc"
        )

        assert inp.metric == "unit_price"
        assert inp.limit == 5
        assert inp.order == "desc"

    def test_aggregate_items_input_defaults(self):
        """Test default values."""
        inp = AggregateItemsInput()

        assert inp.metric == "unit_price"
        assert inp.limit == 5
        assert inp.order == "desc"

    def test_aggregate_items_input_metrics(self):
        """Test different metrics."""
        for metric in ["unit_price", "qty", "ext_amt"]:
            inp = AggregateItemsInput(metric=metric)
            assert inp.metric == metric

    def test_aggregate_items_input_json_schema(self):
        """Test JSON schema."""
        schema = AggregateItemsInput.model_json_schema()

        assert "properties" in schema
        assert "metric" in schema["properties"]
        assert "limit" in schema["properties"]
        assert "order" in schema["properties"]


class TestCompareBiddersSchema:
    """Tests for bidder comparison tool schema."""

    def test_compare_bidders_input_valid(self):
        """Test valid comparison input."""
        inp = CompareBiddersInput(item_no="1031000")

        assert inp.item_no == "1031000"

    def test_compare_bidders_input_json_schema(self):
        """Test JSON schema."""
        schema = CompareBiddersInput.model_json_schema()

        assert "properties" in schema
        assert "item_no" in schema["properties"]
        assert schema["required"] == ["item_no"]


class TestSearchSchema:
    """Tests for search tool schema."""

    def test_search_input_valid(self):
        """Test valid search input."""
        inp = SearchInput(
            query="asphalt paving costs",
            limit=10,
            threshold=0.5
        )

        assert inp.query == "asphalt paving costs"
        assert inp.limit == 10
        assert inp.threshold == 0.5

    def test_search_input_defaults(self):
        """Test default values."""
        inp = SearchInput(query="drainage")

        assert inp.query == "drainage"
        assert inp.limit == 5
        assert inp.threshold == 0.5

    def test_search_input_json_schema(self):
        """Test JSON schema."""
        schema = SearchInput.model_json_schema()

        assert "properties" in schema
        assert "query" in schema["properties"]
        assert "limit" in schema["properties"]
        assert "threshold" in schema["properties"]


class TestToolDefinitions:
    """Tests for tool definitions list."""

    def test_get_tool_definitions_returns_list(self):
        """Test that tool definitions are returned."""
        tools = get_tool_definitions()

        assert isinstance(tools, list)
        assert len(tools) == 4

    def test_get_tool_definitions_names(self):
        """Test tool names."""
        tools = get_tool_definitions()
        names = {t.name for t in tools}

        assert "detect_outliers" in names
        assert "aggregate_items" in names
        assert "compare_bidders" in names
        assert "search" in names

    def test_tool_definitions_have_descriptions(self):
        """Test each tool has a description."""
        tools = get_tool_definitions()

        for tool in tools:
            assert tool.description
            assert len(tool.description) > 20

    def test_tool_definitions_have_schemas(self):
        """Test each tool has a JSON schema."""
        tools = get_tool_definitions()

        for tool in tools:
            assert tool.input_schema
            assert isinstance(tool.input_schema, dict)
            assert "properties" in tool.input_schema

    def test_tool_schemas_valid_json(self):
        """Test schemas can be serialized to JSON."""
        tools = get_tool_definitions()

        for tool in tools:
            json_str = json.dumps(tool.input_schema)
            assert json_str
            assert len(json_str) > 50
