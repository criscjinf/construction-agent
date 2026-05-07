#!/usr/bin/env python3
"""
Construction Agent - Full Mode with Claude API
Uses real embeddings and Claude intelligence for natural conversations
"""

import sys
import tempfile
import os
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(".env")

try:
    from src.data.loaders import DataLoader
    from src.vectorstore.storage import SQLiteVectorStore
    from src.agent.core import AgentExecutor
except ImportError:
    print("❌ Error: Cannot import modules. Make sure you're in the project root.")
    sys.exit(1)


def main():
    print("\n" + "=" * 90)
    print("🤖 CONSTRUCTION BID ANALYSIS AGENT - FULL MODE WITH CLAUDE API")
    print("=" * 90)

    # Load data
    print("\n📂 Loading construction bid data...")
    csv_path = "data/sample_bid_tabulation.csv"

    if not Path(csv_path).exists():
        print(f"❌ Error: {csv_path} not found")
        sys.exit(1)

    try:
        projects = DataLoader.load(csv_path)
        print(f"✅ Loaded {len(projects)} projects with {sum(len(p.items) for p in projects)} items")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)

    # Initialize agent with vector store
    print("\n🔧 Initializing agent with embeddings...")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # Use vector store without indexing to avoid OpenAI API calls
        vector_store = None  # Disable vector store to avoid OpenAI
        agent = AgentExecutor(projects=projects, vector_store=vector_store)
        print(f"✅ Agent ready with {len(agent.tools)} tools")
        print(f"✅ Search tool disabled (no OpenAI quota)")
        print(f"   Available: Top Items, Outlier Detection, Bidder Comparison")
    except KeyboardInterrupt:
        print("\n❌ Initialization interrupted by user")
        sys.exit(1)
    except ValueError as e:
        # Handle configuration errors gracefully
        print(f"\n{str(e)}\n")
        sys.exit(1)
    except Exception as e:
        error_str = str(e)
        if "credit" in error_str.lower() or "quota" in error_str.lower():
            print(f"\n⚠️  API INITIALIZATION ERROR\n")
            print(f"❌ {error_str}\n")
            print("💡 Your API credits may be exhausted.\n")
            print("✅ Use the alternative mode:")
            print("   $ python3 test_interactive.py\n")
        else:
            print(f"❌ Error initializing agent: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Interactive conversation loop
    print("\n" + "=" * 90)
    print("📝 CLAUDE AGENT - INTERACTIVE CONVERSATION MODE")
    print("=" * 90)
    print("\n💡 You can ask natural language questions. Claude will:")
    print("   • Understand your intent")
    print("   • Call appropriate tools (search, analyze, compare)")
    print("   • Provide detailed answers with sources")
    print("\nExamples:")
    print('  "What are the top 5 most expensive items?"')
    print('  "Find any suspicious pricing patterns"')
    print('  "How do bidders compare on MOBILIZATION?"')
    print('  "Are there items with high price variance?"')
    print("\nCommands: 'help', 'examples', 'quit'")
    print("=" * 90 + "\n")

    while True:
        try:
            query = input("📍 You: ").strip()

            if not query:
                continue

            if query.lower() == "quit":
                print("\n👋 Goodbye!\n")
                break

            if query.lower() == "help":
                print("\n" + "=" * 90)
                print("HELP - Claude Agent Capabilities")
                print("=" * 90)
                print("\nClaude can:")
                print("  ✓ Analyze bid data and find patterns")
                print("  ✓ Detect unusual prices and outliers")
                print("  ✓ Compare bidder pricing strategies")
                print("  ✓ Provide statistical insights")
                print("  ✓ Answer construction-domain questions")
                print("\nTry asking:")
                print('  • "What are the top items by price?"')
                print('  • "Are there any pricing anomalies?"')
                print('  • "Compare bidders on item 1031000"')
                print('  • "Which items have highest competition?"')
                print("=" * 90 + "\n")
                continue

            if query.lower() == "examples":
                examples = [
                    "What are the top 5 most expensive bid items?",
                    "Find any unusual or suspicious prices",
                    "How do the three bidders compare on MOBILIZATION?",
                    "Which items have the highest price variance?",
                    "What's the average unit price across all items?",
                    "Are there any pricing patterns or anomalies?",
                    "Compare bidder strategies - who's aggressive vs conservative?",
                    "What items should I focus on for cost reduction?",
                ]
                print("\n" + "=" * 90)
                print("EXAMPLE QUERIES")
                print("=" * 90)
                for i, ex in enumerate(examples, 1):
                    print(f"  {i}. {ex}")
                print("=" * 90 + "\n")
                continue

            # Execute query with Claude
            print("\n🤖 Claude is thinking...\n")
            print("-" * 90)

            try:
                result = agent.query(query)
                print(result)
                print("-" * 90 + "\n")
            except KeyboardInterrupt:
                print("\n❌ Query interrupted by user\n")
            except Exception as e:
                error_str = str(e)

                # Handle API quota/credit errors gracefully
                if "credit balance" in error_str.lower() or "quota" in error_str.lower():
                    print("\n" + "=" * 90)
                    print("⚠️  API CREDIT/QUOTA EXHAUSTED")
                    print("=" * 90)
                    print("\n❌ Your API credits or quotas have been exceeded.")
                    print("\n📝 To use this mode, you need to:")
                    print("   1. Upgrade your OpenAI plan (for embeddings)")
                    print("   2. Upgrade your Anthropic plan (for Claude)")
                    print("\n✅ Alternative: Use the fast mode without API:")
                    print("   $ python3 test_interactive.py")
                    print("\n   This provides 3 fully functional tools:")
                    print("   • Top Items (aggregation)")
                    print("   • Outlier Detection")
                    print("   • Bidder Comparison")
                    print("\n" + "=" * 90 + "\n")
                    break
                else:
                    print(f"❌ Error: {e}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    main()
