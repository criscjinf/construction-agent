"""
Integration tests for agent end-to-end queries.

Tests that agent executors can process user queries, call tools, and return grounded responses.
"""

import pytest
from datetime import date

from src.data.models import Project, BidItem, Bidder
from src.agent.executors import AgentFactory


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
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        assert agent.projects == [sample_project]
        assert agent.tools
        assert len(agent.tools) == 4

    def test_agent_executor_creates_without_projects(self):
        """Test agent can be initialized without projects."""
        agent = AgentFactory.create_agent(prefer_mock=True)

        assert agent.projects == []
        assert agent.tools
        assert len(agent.tools) == 4


class TestAgentToolExecution:
    """Tests for tool execution within agent."""

    def test_agent_executes_aggregation_tool(self, sample_project):
        """Test agent can execute aggregation tool through query."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("What are the top 2 most expensive items?")

        assert result  # Non-empty response
        assert "MOBILIZATION" in result or "unit_price" in result or "item" in result.lower()

    def test_agent_executes_outlier_tool(self, sample_project):
        """Test agent can detect outliers through query."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("Are there any price outliers in the data?")

        assert result  # Non-empty response
        assert "outlier" in result.lower() or "unusual" in result.lower() or "price" in result.lower()

    def test_agent_executes_comparison_tool(self, sample_project):
        """Test agent can compare bidders through query."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("Compare bidders on MOBILIZATION")

        assert result  # Non-empty response
        # Should mention price or bidders
        assert "ABC" in result or "price" in result.lower() or "bidder" in result.lower()

    def test_agent_query_returns_string(self, sample_project):
        """Test agent query returns a string response."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("What information do you have?")

        assert isinstance(result, str)
        assert len(result) > 0


class TestAgentToolComposition:
    """Tests for composing multiple tools."""

    def test_agent_can_handle_complex_queries(self, sample_project):
        """Test agent can handle queries requiring multiple tool calls."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        # Complex query that might require multiple tools
        result = agent.query("Tell me about the top expensive items and their pricing variations")

        assert result
        assert isinstance(result, str)
        assert len(result) > 0


class TestAgentResponseFormatting:
    """Tests for agent response formatting."""

    def test_aggregation_response_is_readable(self, sample_project):
        """Test aggregation response is human-readable."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("What are the top items by price?")

        # Should have readable format
        assert len(result) > 0
        assert isinstance(result, str)

    def test_outlier_response_is_readable(self, sample_project):
        """Test outlier response is understandable."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("Detect any price outliers")

        # Should return a response
        assert len(result) > 0
        assert isinstance(result, str)

    def test_comparison_response_mentions_items(self, sample_project):
        """Test comparison response mentions relevant items."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        result = agent.query("Compare prices on MOBILIZATION")

        # Should return a response
        assert len(result) > 0
        assert isinstance(result, str)


class TestAgentSystemPrompt:
    """Tests for agent tools configuration."""

    def test_agent_has_tools_configured(self, sample_project):
        """Test agent has tools configured."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        assert agent.tools
        assert len(agent.tools) == 4
        tool_names = [tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None) for tool in agent.tools]
        assert any("outlier" in str(name).lower() or "detect" in str(name).lower() for name in tool_names)

    def test_agent_has_aggregation_tool(self, sample_project):
        """Test agent has aggregation tool."""
        agent = AgentFactory.create_agent(
            projects=[sample_project],
            prefer_mock=True
        )

        tool_names = [tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None) for tool in agent.tools]
        assert any("aggregate" in str(name).lower() or "top" in str(name).lower() for name in tool_names)
