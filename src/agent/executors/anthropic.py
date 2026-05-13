"""Anthropic Claude agent executor."""

import logging
from typing import Optional
from anthropic import Anthropic

from src.config import Config
from src.data.models import Project
from src.vectorstore.embeddings import EmbeddingClient
from src.vectorstore.retrieval import HybridRetriever
from src.vectorstore.storage import VectorStore
from src.agent.executors.base import BaseAgentExecutor
from src.agent.prompts import get_system_prompt
from src.agent.tools import (
    DetectOutliersInput,
    AggregateItemsInput,
    CompareBiddersInput,
    SearchInput,
)
from src.analysis.outliers import detect_price_outliers
from src.analysis.aggregations import AggregationService
from src.analysis.comparisons import ComparisonService

logger = logging.getLogger(__name__)


class AnthropicAgentExecutor(BaseAgentExecutor):
    """Execute Claude agent with tool-use for construction bid analysis."""

    def __init__(
        self,
        projects: list[Project],
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
        model: Optional[str] = None
    ):
        """
        Initialize Anthropic agent executor.

        Args:
            projects: List of loaded Project objects
            vector_store: Vector store for semantic search (optional)
            embedding_client: Embedding client for generating vectors
            model: Claude model to use (defaults to Config.AGENT_MODEL)

        Raises:
            ValueError: If ANTHROPIC_API_KEY not configured
        """
        # Get API key from config
        api_key = Config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY not configured\n\n"
                "To use the Claude Agent, configure:\n"
                "  1. ANTHROPIC_API_KEY in .env file\n"
                "  2. Ensure you have active credits\n\n"
                "💡 Fallback: Use MockAgentExecutor for testing"
            )

        super().__init__(projects, vector_store, embedding_client)

        self.client = Anthropic(api_key=api_key)
        self.model = model or Config.get_agent_model()

    def query(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Execute agent loop with Claude API.

        Args:
            user_message: User's natural language query
            max_iterations: Max tool-call iterations

        Returns:
            Final response with sources cited
        """
        messages = [{"role": "user", "content": user_message}]

        for iteration in range(max_iterations):
            logger.info(f"Agent iteration {iteration + 1}/{max_iterations}")

            # Call Claude with tools
            tool_defs = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.input_schema
                }
                for t in self.tools
            ]

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=get_system_prompt(),
                tools=tool_defs,
                messages=messages
            )

            # Check if agent is done
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                return "No response generated"

            # Process tool calls
            if response.stop_reason != "tool_use":
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                return "Unexpected stop reason"

            # Extract tool calls from response
            tool_calls = []
            text_parts = []
            for block in response.content:
                if hasattr(block, 'text'):
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_calls.append(block)

            # If no tool calls, return what we have
            if not tool_calls:
                return "\n".join(text_parts) if text_parts else "No response"

            # Execute tools and collect results
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_call in tool_calls:
                try:
                    result = self._execute_tool(tool_call.name, tool_call.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result
                    })
                except Exception as e:
                    logger.error(f"Tool execution failed: {tool_call.name}: {e}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })

            messages.append({"role": "user", "content": tool_results})

        return "Max iterations reached"

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a single tool and return result as string."""
        if tool_name == "detect_outliers":
            return self._tool_detect_outliers(tool_input)
        elif tool_name == "aggregate_items":
            return self._tool_aggregate_items(tool_input)
        elif tool_name == "compare_bidders":
            return self._tool_compare_bidders(tool_input)
        elif tool_name == "search":
            return self._tool_search(tool_input)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _tool_detect_outliers(self, params: dict) -> str:
        """Execute outlier detection tool."""
        inp = DetectOutliersInput(**params)

        result = detect_price_outliers(
            prices=inp.prices,
            item_type=inp.item_type or "",
            method=inp.method.value,
            sensitivity=inp.sensitivity
        )

        outlier_strs = []
        for outlier in result.get("outliers", []):
            outlier_strs.append(
                f"  • {outlier.value:.2f} ({outlier.description})"
            )

        interpretation = f"""
Analyzed {result['count']} prices for {inp.item_type or 'items'}:
• Mean: ${result['mean']:.2f}
• Median: ${result['median']:.2f}
• Stdev: ${result['stdev']:.2f}
• Outliers detected: {len(result['outliers'])}
"""
        if result.get("outliers"):
            interpretation += "\nOutlier values:\n" + "\n".join(outlier_strs)

        return interpretation.strip()

    def _tool_aggregate_items(self, params: dict) -> str:
        """Execute aggregation tool."""
        inp = AggregateItemsInput(**params)

        # Check if metric is a known field or unmapped field
        known_metrics = {"unit_price", "qty", "ext_amt"}

        if inp.metric in known_metrics:
            # Use standard aggregation for known metrics
            top_items = AggregationService.get_top_items(
                projects=self.projects,
                metric=inp.metric,
                limit=inp.limit,
                order=inp.order
            )

            if not top_items:
                return f"No items found with metric '{inp.metric}'"

            order_label = "highest" if inp.order == "desc" else "lowest"
            result_strs = []
            for i, (item_no, item_desc, value) in enumerate(top_items, 1):
                result_strs.append(f"{i}. {item_desc} (#{item_no}): {value:.2f}")

            interpretation = f"""
Top {inp.limit} {order_label} items by {inp.metric}:
""" + "\n".join(result_strs)

            return interpretation.strip()
        else:
            # Use unmapped field aggregation
            result = AggregationService.aggregate_unmapped_field(
                projects=self.projects,
                field_name=inp.metric,
                operation=inp.operation
            )

            if result is None:
                return f"No valid values found for unmapped field '{inp.metric}'"

            return f"""
Aggregation result for '{inp.metric}' ({inp.operation}): {result:.2f}

Note: This field was detected as an unknown/unmapped column in your CSV.
The system automatically inferred its type and aggregated the values.
"""

    def _tool_compare_bidders(self, params: dict) -> str:
        """Execute bidder comparison tool."""
        inp = CompareBiddersInput(**params)

        for project in self.projects:
            item = project.get_item_by_number(inp.item_no)
            if item:
                comparisons = ComparisonService.compare_bidders_on_item(project, inp.item_no)

                if not comparisons:
                    return f"Item {inp.item_no} not found across bidders"

                result_strs = [f"Item {inp.item_no}: {item.item_desc}"]
                result_strs.append(f"Median unit price: ${comparisons[0].median_price:.2f}")
                result_strs.append(f"Bidders: {len(comparisons)}")
                result_strs.append("")

                for comp in comparisons:
                    result_strs.append(
                        f"  • {comp.bidder_name}: ${comp.unit_price:.2f} "
                        f"(rank {comp.bid_rank}, {comp.variance:+.1f}% vs median)"
                    )

                variance = ComparisonService.get_price_variance_for_item(project, inp.item_no)
                competitive = "High" if variance and variance > 0.15 else "Low"
                result_strs.append(f"\nCompetition level: {competitive} variance")

                return "\n".join(result_strs)

        return f"Item {inp.item_no} not found in any project"

    def _tool_search(self, params: dict) -> str:
        """Execute semantic search tool."""
        inp = SearchInput(**params)

        if not self.vector_store or not self.embedding_client:
            return "Vector store or embedding client not available for search"

        retriever = HybridRetriever(
            vector_store=self.vector_store,
            embedding_client=self.embedding_client,
            semantic_weight=0.7,
            keyword_weight=0.3
        )

        results = retriever.search(
            query=inp.query,
            limit=inp.limit,
            semantic_threshold=inp.threshold,
            keyword_threshold=0.0
        )

        if not results:
            return f"No results found for: {inp.query}"

        result_strs = [f"Found {len(results)} results for: {inp.query}\n"]
        for i, (doc_id, score, metadata) in enumerate(results, 1):
            doc = self.vector_store.get_by_id(doc_id)
            if not doc:
                continue

            content = doc.get("text", "")
            source = metadata.get("source", doc_id)
            result_strs.append(
                f"{i}. [{source}] (similarity: {score:.2f})\n{content[:200]}..."
            )

        return "\n".join(result_strs)
