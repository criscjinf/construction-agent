"""Mock agent executor for testing and fallback."""

import logging
from typing import Optional

from src.data.models import Project
from src.vectorstore.embeddings import EmbeddingClient
from src.vectorstore.storage import VectorStore
from src.agent.executors.base import BaseAgentExecutor
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


class MockAgentExecutor(BaseAgentExecutor):
    """Mock agent executor for testing and offline fallback."""

    def __init__(
        self,
        projects: list[Project],
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
    ):
        """
        Initialize mock agent executor.

        Args:
            projects: List of loaded Project objects
            vector_store: Vector store for semantic search (optional)
            embedding_client: Embedding client for generating vectors (optional)
        """
        super().__init__(projects, vector_store, embedding_client)
        logger.info("Using MockAgentExecutor (offline mode, no API calls)")

    def query(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Execute query using mock logic (no API calls).

        Args:
            user_message: User's natural language query
            max_iterations: Ignored (mock doesn't iterate)

        Returns:
            Mock response based on query pattern
        """
        logger.info(f"Mock query: {user_message[:100]}")

        # Simple pattern matching for mock responses
        query_lower = user_message.lower()

        # Detect query type and return mock response
        if any(word in query_lower for word in ["top", "highest", "most expensive"]):
            return self._mock_aggregate(query_lower)
        elif any(word in query_lower for word in ["outlier", "anomaly", "deviate", "unusual"]):
            return self._mock_outliers(query_lower)
        elif any(word in query_lower for word in ["compare", "bidder", "competition", "vs"]):
            return self._mock_comparison(query_lower)
        elif any(word in query_lower for word in ["search", "find", "about", "say"]):
            return self._mock_search(query_lower)
        else:
            return self._mock_default(query_lower)

    def _mock_aggregate(self, query: str) -> str:
        """Mock aggregation response."""
        # Try to get real data if available
        if not self.projects:
            return "📊 [MOCK] Top 5 items:\n1. Item A: $1000\n2. Item B: $900\n3. Item C: $800"

        top_items = AggregationService.get_top_items(
            projects=self.projects,
            metric="unit_price",
            limit=5,
            order="desc"
        )

        if not top_items:
            return "📊 [MOCK] No items found in projects"

        result_strs = ["📊 [MOCK - No API] Top items by unit price:"]
        for i, (item_no, item_desc, value) in enumerate(top_items, 1):
            result_strs.append(f"  {i}. {item_desc}: ${value:.2f}")

        return "\n".join(result_strs)

    def _mock_outliers(self, query: str) -> str:
        """Mock outlier detection response."""
        if not self.projects:
            return "🔴 [MOCK] Outlier analysis:\n• 2 outliers detected\n• Above 2.0σ threshold"

        # Collect all prices from projects
        all_prices = []
        for project in self.projects:
            for item in project.items:
                all_prices.append(item.unit_price)

        if not all_prices:
            return "🔴 [MOCK] No pricing data available"

        result = detect_price_outliers(prices=all_prices)

        result_strs = [f"🔴 [MOCK - No API] Outlier Analysis:"]
        result_strs.append(f"  • Analyzed: {result['count']} prices")
        result_strs.append(f"  • Mean: ${result['mean']:.2f}")
        result_strs.append(f"  • Stdev: ${result['stdev']:.2f}")
        result_strs.append(f"  • Outliers: {len(result.get('outliers', []))}")

        return "\n".join(result_strs)

    def _mock_comparison(self, query: str) -> str:
        """Mock bidder comparison response."""
        if not self.projects:
            return "🏆 [MOCK] Bidder Comparison:\n• Bidder A: $100 (Rank 1)\n• Bidder B: $120 (Rank 2)"

        # Get first item from first project
        for project in self.projects:
            if project.items:
                item = project.items[0]
                return f"""🏆 [MOCK - No API] Bidders on {item.item_desc}:
  • Median: ${item.unit_price:.2f}
  • Bidders: {len(project.bidders) if hasattr(project, 'bidders') else 3}
  • Competition: Medium variance"""

        return "🏆 [MOCK] No comparison data available"

    def _mock_search(self, query: str) -> str:
        """Mock semantic search response."""
        if self.vector_store:
            return f"""🔍 [MOCK - Vector Store Available]
  Query: {query}
  Results: 3 relevant documents
  (Real search would require embeddings)"""

        return f"""🔍 [MOCK - No Vector Store]
  Query: {query}
  Results: 2 keyword matches
  • Document 1: Sample content...
  • Document 2: Another result..."""

    def _mock_default(self, query: str) -> str:
        """Default mock response."""
        project_count = len(self.projects)
        item_count = sum(len(p.items) for p in self.projects) if self.projects else 0

        return f"""✨ [MOCK RESPONSE - No API Called]

Your query: "{query[:60]}"

Available data:
  • Projects: {project_count}
  • Items: {item_count}
  • Vector Store: {"Available" if self.vector_store else "Offline"}

💡 Fallback activated: Running with mock data.
   Switch to AnthropicAgentExecutor for full AI capabilities.

This is a test response. Real Claude would provide detailed analysis."""
