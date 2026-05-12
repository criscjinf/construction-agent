"""Tool definitions factory."""

from src.agent.tools.base import ToolDefinition
from src.agent.tools.detect_outliers import DetectOutliersInput
from src.agent.tools.aggregate_items import AggregateItemsInput
from src.agent.tools.compare_bidders import CompareBiddersInput
from src.agent.tools.search import SearchInput


def get_tool_definitions() -> list[ToolDefinition]:
    """
    Return list of tool definitions for Claude agent.

    Each tool corresponds to a function the agent can call.
    Claude will invoke these based on the user query.
    """
    return [
        ToolDefinition(
            name="detect_outliers",
            description="Detect outlier prices using Z-score or IQR method. Returns statistics and outlier details.",
            input_schema=DetectOutliersInput.model_json_schema()
        ),
        ToolDefinition(
            name="aggregate_items",
            description="Get top bid items by metric (unit_price, qty, ext_amt). Useful for 'top 5 most expensive' queries.",
            input_schema=AggregateItemsInput.model_json_schema()
        ),
        ToolDefinition(
            name="compare_bidders",
            description="Compare prices of all bidders on a specific item. Shows competition level and outliers.",
            input_schema=CompareBiddersInput.model_json_schema()
        ),
        ToolDefinition(
            name="search",
            description="Search bid data and PDF content using semantic + keyword search. Find items, costs, requirements.",
            input_schema=SearchInput.model_json_schema()
        ),
    ]
