"""Example queries for agent documentation and testing."""

EXAMPLE_QUERIES = [
    {
        "query": "What are the top 5 most expensive bid items?",
        "tools": ["aggregate_items"],
        "explanation": "Ranks items by unit price to identify high-cost line items that impact the overall bid"
    },
    {
        "query": "Are there any items with unit prices that deviate significantly?",
        "tools": ["detect_outliers"],
        "explanation": "Finds statistical outliers using Z-score method (default 2.0σ) to highlight unusual pricing"
    },
    {
        "query": "How do bidders compare on MOBILIZATION?",
        "tools": ["compare_bidders"],
        "explanation": "Compares all bidders' prices on a specific item to show competition and outlier bidders"
    },
    {
        "query": "What does the plan set say about drainage?",
        "tools": ["search"],
        "explanation": "Semantic search on PDF content to find design requirements and specifications"
    },
    {
        "query": "Which items have the most bidder competition?",
        "tools": ["aggregate_items", "compare_bidders"],
        "explanation": "Chains tools: first gets all items, then calculates competition level (variance) for each"
    },
    {
        "query": "Top 3 items by extended amount, then check if any are outliers",
        "tools": ["aggregate_items", "detect_outliers"],
        "explanation": "Gets top items by total cost (qty × unit_price), then checks if prices are statistical outliers"
    },
    {
        "query": "Compare prices for ASPHALT SURFACE across all bidders",
        "tools": ["compare_bidders"],
        "explanation": "Shows how different contractors priced the same work item with variance analysis"
    },
]


def get_example_queries() -> list[dict]:
    """Get example queries for documentation and testing."""
    return EXAMPLE_QUERIES
