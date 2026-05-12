#!/usr/bin/env python3
"""
Interactive test mode for Construction Agent.
No API keys required - uses local tools directly.
"""

import sys
import tempfile
import os
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(".env")

try:
    from src.data.parsers import CSVParser
    from src.agent.executors import AgentFactory
except ImportError:
    print("❌ Error: Cannot import modules. Make sure you're in the project root.")
    sys.exit(1)


def main():
    print("\n" + "=" * 90)
    print("🤖 CONSTRUCTION BID ANALYSIS AGENT - INTERACTIVE MODE")
    print("=" * 90)

    # Load data
    print("\n📂 Loading construction bid data...")
    csv_path = "data/sample_bid_tabulation.csv"

    if not Path(csv_path).exists():
        print(f"❌ Error: {csv_path} not found")
        sys.exit(1)

    try:
        projects = CSVParser().parse(csv_path)
        print(f"✅ Loaded {len(projects)} projects with {sum(len(p.items) for p in projects)} items")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)

    # Initialize agent
    print("\n🔧 Initializing agent...")

    try:
        # Create agent with prefer_mock=True for instant startup (no API calls)
        agent = AgentFactory.create_agent(
            projects=projects,
            vector_store=None,
            embedding_client=None,
            prefer_mock=True
        )
        print(f"✅ Agent ready with {len(agent.tools)} tools (Mock mode)")
        print("   Tools available:")
        print("     • Top Items (aggregation)")
        print("     • Outlier Detection")
        print("     • Bidder Comparison")
    except KeyboardInterrupt:
        print("\n❌ Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)

    # Interactive loop
    print("\n" + "=" * 90)
    print("📝 INTERACTIVE MODE")
    print("=" * 90)
    print("\nAvailable tools:")
    print("  1. Search     - Find items by name/description")
    print("  2. Outliers   - Detect unusual prices")
    print("  3. Top Items  - Find most expensive items")
    print("  4. Compare    - Compare bidder prices on an item")
    print("\nCommands:")
    print("  help      - Show this message")
    print("  examples  - Show example queries")
    print("  quit      - Exit")
    print("=" * 90 + "\n")

    while True:
        try:
            query = input("📍 Your query: ").strip()

            if not query:
                continue

            if query.lower() == "quit":
                print("\n👋 Goodbye!\n")
                break

            if query.lower() == "help":
                print("\n" + "=" * 90)
                print("HELP - Available Tools & Examples")
                print("=" * 90)
                print("\n🔍 SEARCH TOOL:")
                print("  Use: Find items by description")
                print("  Examples:")
                print("    - 'Search for MOBILIZATION'")
                print("    - 'Find ASPHALT items'")
                print("    - 'What are the pavement items?'")

                print("\n📊 OUTLIER DETECTION:")
                print("  Use: Find unusual prices")
                print("  Examples:")
                print("    - 'Are there any suspicious prices?'")
                print("    - 'Check for price outliers'")
                print("    - 'Detect unusual pricing'")

                print("\n📈 TOP ITEMS:")
                print("  Use: Find most expensive or most frequent items")
                print("  Examples:")
                print("    - 'Top 5 most expensive items'")
                print("    - 'Show top items by unit price'")
                print("    - 'What are the highest priced items?'")

                print("\n🔄 COMPARISON:")
                print("  Use: Compare bidder prices on specific item")
                print("  Examples:")
                print("    - 'Compare MOBILIZATION prices'")
                print("    - 'How do bidders price item 1031000?'")
                print("    - 'Price spread on TRAFFIC CONTROL'")
                print("=" * 90 + "\n")
                continue

            if query.lower() == "examples":
                print("\n" + "=" * 90)
                print("EXAMPLE QUERIES")
                print("=" * 90)
                examples = [
                    "What are the top 5 most expensive items?",
                    "Find items with unusual prices",
                    "Compare MOBILIZATION across bidders",
                    "Search for ASPHALT items",
                    "Are there any price outliers?",
                    "Show highest unit prices",
                    "How do bidders compare on drainage?",
                ]
                for i, ex in enumerate(examples, 1):
                    print(f"  {i}. {ex}")
                print("=" * 90 + "\n")
                continue

            # Route query to appropriate tool
            print("\n" + "-" * 90)
            _process_query(agent, query)
            print("-" * 90 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")



def _process_query(agent, query: str) -> None:
    """Process query through agent."""
    try:
        result = agent.query(query)
        print(result)
    except Exception as e:
        print(f"❌ Error processing query: {e}")


if __name__ == "__main__":
    main()
