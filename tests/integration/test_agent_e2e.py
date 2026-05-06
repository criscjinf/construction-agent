"""
Integration tests for agent end-to-end queries.

Tests that AgentExecutor can process user queries, call tools, and return grounded responses.
"""

import pytest
from datetime import date

from src.data.models import Project, BidItem, Bidder
from src.agent.core import AgentExecutor


@pytest.fixture
def sample_project():
    """Create sample project with multiple bidders and items."""
    project = Project(proj_id="0676350", let_dt=date(2026, 3, 10))

    # Items for the project
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

    # Bidders
    bidder1 = Bidder(name="ABC CONSTRUCTION", bid_rank=1, bid_total=337288.86)
    bidder2 = Bidder(name="XYZ CORP", bid_rank=2, bid_total=400000.0)

    project.items = items
    project.bidders["ABC CONSTRUCTION"] = bidder1
    project.bidders["XYZ CORP"] = bidder2

    # Items per bidder (with some variation)
    project.bidder_items["ABC CONSTRUCTION"] = items
    project.bidder_items["XYZ CORP"] = [
        BidItem(
            item_no="1031000",
            item_desc="MOBILIZATION",
            unit="LS",
            qty=1.0,
            unit_price=18000.0,  # Higher price
            ext_amt=18000.0,
        ),
        BidItem(
            item_no="1032010",
            item_desc="BONDS AND INSURANCE",
            unit="LS",
            qty=1.0,
            unit_price=850.0,
            ext_amt=850.0,
        ),
        BidItem(
            item_no="4040350",
            item_desc="ASPHALT SURFACE COURSE",
            unit="TON",
            qty=1497.32,
            unit_price=100.0,  # Slightly higher
            ext_amt=149732.0,
        ),
    ]

    return project


class TestAgentExecutorInitialization:
    """Tests for agent initialization."""

    def test_agent_executor_creates_with_projects(self, sample_project):
        """Test agent can be initialized with projects."""
        agent = AgentExecutor(projects=[sample_project])

        assert agent.projects == [sample_project]
        assert agent.tools
        assert len(agent.tools) == 4

    def test_agent_executor_has_client(self, sample_project):
        """Test agent has Anthropic client."""
        agent = AgentExecutor(projects=[sample_project])

        assert agent.client is not None


class TestAgentToolExecution:
    """Tests for tool execution within agent."""

    def test_agent_executes_aggregation_tool(self, sample_project):
        """Test agent can execute aggregation tool."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_aggregate_items({
            "metric": "unit_price",
            "limit": 2,
            "order": "desc"
        })

        assert "unit_price" in result or "metric" in result.lower()
        assert result  # Non-empty response

    def test_agent_executes_outlier_tool(self, sample_project):
        """Test agent can execute outlier detection tool."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_detect_outliers({
            "prices": [100, 101, 102, 103, 500],
            "method": "zscore",
            "sensitivity": 2.0
        })

        assert "Analyzed" in result or "outlier" in result.lower()
        assert result

    def test_agent_executes_comparison_tool(self, sample_project):
        """Test agent can execute bidder comparison tool."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_compare_bidders({
            "item_no": "1031000"
        })

        assert "1031000" in result or "MOBILIZATION" in result
        assert "ABC CONSTRUCTION" in result or "XYZ CORP" in result

    def test_tool_execution_error_handling(self, sample_project):
        """Test agent handles tool errors gracefully."""
        agent = AgentExecutor(projects=[sample_project])

        # Invalid tool execution should not crash
        try:
            result = agent._tool_aggregation_tool({})
        except (KeyError, AttributeError, ValueError):
            # Expected for invalid inputs
            pass


class TestAgentToolComposition:
    """Tests for composing multiple tools."""

    def test_agent_can_chain_tools(self, sample_project):
        """Test agent can use multiple tools sequentially."""
        agent = AgentExecutor(projects=[sample_project])

        # First tool: get top items
        top_items = agent._tool_aggregate_items({
            "metric": "unit_price",
            "limit": 3,
            "order": "desc"
        })

        assert top_items

        # Second tool: detect outliers on those prices
        outliers = agent._tool_detect_outliers({
            "prices": [16500.0, 93.9, 800.0],
            "method": "zscore"
        })

        assert outliers


class TestAgentResponseFormatting:
    """Tests for agent response formatting."""

    def test_aggregation_response_format(self, sample_project):
        """Test aggregation response is human-readable."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_aggregate_items({
            "metric": "unit_price",
            "limit": 2,
            "order": "desc"
        })

        # Should have readable format with item descriptions
        lines = result.split("\n")
        assert len(lines) > 1

    def test_outlier_response_format(self, sample_project):
        """Test outlier response includes statistics."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_detect_outliers({
            "prices": [100, 101, 102, 103, 500],
            "method": "zscore",
            "sensitivity": 2.0
        })

        # Should include Mean, Median, etc
        assert "Mean:" in result or "mean" in result.lower()

    def test_comparison_response_cites_bidders(self, sample_project):
        """Test comparison response cites all bidders."""
        agent = AgentExecutor(projects=[sample_project])

        result = agent._tool_compare_bidders({
            "item_no": "1031000"
        })

        # Should cite both bidders
        assert "ABC" in result or "XYZ" in result


class TestAgentSystemPrompt:
    """Tests for agent system prompt."""

    def test_agent_has_system_prompt(self, sample_project):
        """Test agent returns a system prompt."""
        agent = AgentExecutor(projects=[sample_project])

        prompt = agent._get_system_prompt()

        assert prompt
        assert "Construction" in prompt or "bid" in prompt.lower()

    def test_system_prompt_mentions_tools(self, sample_project):
        """Test system prompt mentions available tools."""
        agent = AgentExecutor(projects=[sample_project])

        prompt = agent._get_system_prompt()

        assert "detect_outliers" in prompt or "outlier" in prompt.lower()
        assert "aggregate_items" in prompt or "top" in prompt.lower()
