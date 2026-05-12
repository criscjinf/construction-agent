#!/usr/bin/env python3
"""
Test PDF analysis with agent - Fast mode
Uses mock embeddings to avoid API calls and token waste
"""

import sys
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

try:
    from src.data.parsers import CSVParser
    from src.vectorstore.storage import MockVectorStore
    from src.vectorstore.embeddings import MockEmbeddingClient
    from src.agent.core import AgentExecutor
    from src.data.document_loader import DocumentLoader
    from src.data.indexers import IndexersFactory
except ImportError:
    print("❌ Error: Cannot import modules")
    sys.exit(1)


def main():
    print("\n" + "=" * 90)
    print("🤖 CONSTRUCTION AGENT - PDF ANALYSIS MODE (FAST - Mock Embeddings)")
    print("=" * 90)

    # Load CSV data
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

    # Initialize vector store and index documents
    print("\n📄 Indexing documents (CSV + PDFs)...")

    try:
        # Use mock embeddings for fast testing (no OpenAI API calls)
        embedding_client = MockEmbeddingClient()
        vector_store = MockVectorStore()

        # Load and index all documents with mock embeddings
        indexers_factory = IndexersFactory(vector_store=vector_store, embedding_client=embedding_client)
        doc_loader = DocumentLoader(indexers_factory=indexers_factory)
        results = doc_loader.load_all_documents("data")

        print(f"✅ Indexing complete:")
        print(f"   • CSV items indexed: {results['csv']}")
        print(f"   • PDF chunks indexed: {results['pdf']}")

        if results["errors"]:
            print(f"   • Errors: {len(results['errors'])}")

        # Initialize agent with indexed documents
        print("\n🤖 Initializing agent...")
        agent = AgentExecutor(projects=projects, vector_store=vector_store, embedding_client=embedding_client)
        print(f"✅ Agent ready with {len(agent.tools)} tools")
        print("   Available: Search (PDFs + CSV), Top Items, Outlier Detection, Bidder Comparison")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Interactive loop
    print("\n" + "=" * 90)
    print("📝 PDF ANALYSIS MODE - Ask questions about construction plans!")
    print("=" * 90)
    print("\n💡 Example questions:")
    print('  • "What does the plan say about drainage?"')
    print('  • "What are the specification requirements?"')
    print('  • "Summarize key project information"')
    print('  • "What about runway construction details?"')
    print("\nCommands: 'help', 'quit'")
    print("=" * 90 + "\n")

    while True:
        try:
            query = input("📍 Your question: ").strip()

            if not query:
                continue

            if query.lower() == "quit":
                print("\n👋 Goodbye!\n")
                break

            if query.lower() == "help":
                print("\n" + "=" * 90)
                print("HELP - PDF Analysis")
                print("=" * 90)
                print("\nYou can ask Claude about:")
                print("  • Construction plan specifications")
                print("  • Bid tabulation data")
                print("  • Pricing information")
                print("  • Project details from documents")
                print("\nClaude will search PDFs and CSV data to answer your questions.")
                print("=" * 90 + "\n")
                continue

            # Execute query
            print("\n🤖 Claude is analyzing documents...\n")
            print("-" * 90)

            try:
                result = agent.query(query)
                print(result)
                print("-" * 90 + "\n")
            except KeyboardInterrupt:
                print("\n❌ Query interrupted\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
