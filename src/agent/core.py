"""
Agent orchestrator using Claude API with tool-use patterns.

AgentExecutor:
- Initializes Claude SDK
- Processes tool calls from agent
- Executes Python functions
- Formats responses with sources
"""

import logging
import os
from typing import Optional
from anthropic import Anthropic

from src.data.models import Project
from src.data.loaders import DataLoader
from src.vectorstore.embeddings import EmbeddingClient, MockEmbeddingClient
from src.vectorstore.retrieval import HybridRetriever
from src.vectorstore.storage import SQLiteVectorStore
from src.analysis.outliers import OutlierDetector, OutlierMethod, detect_price_outliers
from src.analysis.aggregations import AggregationService
from src.analysis.comparisons import ComparisonService
from src.agent.tools import get_tool_definitions, DetectOutliersInput, AggregateItemsInput, CompareBiddersInput, SearchInput

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Execute Claude agent with tool-use for construction bid analysis."""

    def __init__(
        self,
        projects: list[Project],
        vector_store: Optional[SQLiteVectorStore] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Initialize agent executor.

        Args:
            projects: List of loaded Project objects
            vector_store: Vector store for semantic search (optional)
            model: Claude model to use
        """
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=api_key)
        self.projects = projects
        self.vector_store = vector_store
        self.model = model
        self.tools = get_tool_definitions()

        # Index projects in vector store for semantic search
        if self.vector_store:
            self._index_projects_in_vector_store()

    def query(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Execute agent loop: process query, call tools, format response.

        Args:
            user_message: User's natural language query
            max_iterations: Max tool-call iterations (prevent infinite loops)

        Returns:
            Final response with sources cited
        """
        messages = [
            {"role": "user", "content": user_message}
        ]

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
                system=self._get_system_prompt(),
                tools=tool_defs,
                messages=messages
            )

            # Check if agent is done
            if response.stop_reason == "end_turn":
                # Extract final text response
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                return "No response generated"

            # Process tool calls
            if response.stop_reason != "tool_use":
                # Shouldn't happen, but handle gracefully
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
        """
        Execute a single tool and return result as string.

        Args:
            tool_name: Name of tool to execute
            tool_input: Input parameters (dict)

        Returns:
            String representation of result
        """
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

    def _tool_compare_bidders(self, params: dict) -> str:
        """Execute bidder comparison tool."""
        inp = CompareBiddersInput(**params)

        # Find the project containing this item
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

        if not self.vector_store:
            return "Vector store not available for search"

        # Use MockEmbeddingClient for search (consistent with indexing fallback)
        embedding_client = MockEmbeddingClient()

        retriever = HybridRetriever(
            vector_store=self.vector_store,
            embedding_client=embedding_client,
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

    def _index_projects_in_vector_store(self) -> None:
        """Index bid items from projects into vector store for semantic search."""
        try:
            # Try to use real EmbeddingClient, fallback to Mock if API unavailable
            try:
                embedding_client = EmbeddingClient()
            except (ValueError, Exception) as e:
                logger.warning(f"OpenAI API unavailable ({type(e).__name__}), using MockEmbeddingClient")
                embedding_client = MockEmbeddingClient()

            count = 0

            for project in self.projects:
                # Index each bid item
                for item in project.items:
                    doc_id = f"{project.proj_id}_{item.item_no}"
                    text = f"{item.item_desc} - {item.unit} @ ${item.unit_price:.2f}"

                    try:
                        embedding = embedding_client.embed_text(text)
                        self.vector_store.insert(
                            doc_id=doc_id,
                            text=text,
                            embedding=embedding,
                            metadata={
                                "proj_id": project.proj_id,
                                "item_no": item.item_desc,
                                "unit_price": item.unit_price,
                                "source": "bid_items",
                            }
                        )
                        count += 1
                    except Exception as e:
                        logger.warning(f"Failed to embed item {doc_id}: {e}")

            logger.info(f"Indexed {count} bid items in vector store")

        except Exception as e:
            logger.error(f"Failed to index projects in vector store: {e}")

    def _get_system_prompt(self) -> str:
        """Return system prompt for agent."""
        return """You are an AI assistant for construction bid analysis. You help construction teams analyze bid tabulations and project plans.

You have access to the following tools:
1. detect_outliers - Find prices that deviate significantly from normal (Z-score or IQR method)
2. aggregate_items - Get top bid items by any metric (unit price, quantity, extended amount)
3. compare_bidders - Compare how different bidders priced a specific item
4. search - Search bid data and PDF content using semantic + keyword search

Instructions:
- Always cite sources and explain your reasoning
- Use outlier detection to find suspicious or interesting prices
- For "top X items" queries, use aggregate_items
- For bidder comparisons, use compare_bidders
- For document search (e.g., "what does the plan say..."), use search
- When multiple tools could help, chain them in one response
- If you don't have data, say so explicitly
- Format numbers with 2 decimal places for currency

Remember: Construction bid analysis requires accuracy. Show your work and cite sources."""
