#!/usr/bin/env python3
"""
Demo - Shows complete workflow with data in data/ folder
"""

import os
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

# Initialize logging at runtime (in main())
from src.config import Config
from src.logging_config import initialize_logging, get_logger

try:
    from src.data.parsers import CSVParser, CSVValidationError
    from src.data.document_loader import DocumentLoader
    from src.data.indexers import IndexersFactory
    from src.vectorstore.storage import SQLiteVectorStore
    from src.vectorstore.embeddings import MockEmbeddingClient
    from src.agent.executors import AgentFactory
    from src.data.models import Project
except ImportError:
    print("❌ Cannot import modules")
    import sys
    sys.exit(1)


def main():
    # Initialize logging at runtime (not at import time)
    initialize_logging()
    log = get_logger("construction_agent.demo")

    print("\n" + "=" * 90)
    print("🤖 CONSTRUCTION AGENT - DEMO")
    print("=" * 90)

    # Create temp directory
    upload_dir = tempfile.mkdtemp(prefix="construction_agent_")
    uploaded_files = []
    projects = []

    # Auto-load from data/ folder
    print("\n📂 Loading documents from data/ folder...")
    data_path = Path("data")

    if data_path.exists():
        # Load CSVs
        for csv_file in data_path.glob("*.csv"):
            try:
                shutil.copy(str(csv_file), upload_dir)
                uploaded_files.append(str(Path(upload_dir) / csv_file.name))
                new_projects = CSVParser().parse(str(csv_file))
                projects.extend(new_projects)
                print(f"   ✅ CSV: {csv_file.name}")
            except CSVValidationError as e:
                print(f"   ❌ {csv_file.name}: Invalid format - {e}")
            except Exception as e:
                print(f"   ❌ {csv_file.name}: {e}")

        # Load PDFs
        for pdf_file in data_path.glob("*.pdf"):
            try:
                shutil.copy(str(pdf_file), upload_dir)
                uploaded_files.append(str(Path(upload_dir) / pdf_file.name))
                print(f"   ✅ PDF: {pdf_file.name}")
            except Exception as e:
                print(f"   ❌ {pdf_file.name}: {e}")

    print(f"\n✅ Loaded {len(uploaded_files)} documents")

    # Get database path (from config or temporary)
    db_path = Config.get_database_path()

    # Index documents
    print("\n📊 Indexing documents...")
    vector_store = SQLiteVectorStore(db_path=db_path)
    embedding_client = MockEmbeddingClient()
    indexers_factory = IndexersFactory(vector_store=vector_store, embedding_client=embedding_client)
    doc_loader = DocumentLoader(indexers_factory=indexers_factory)

    results = {"csv": 0, "pdf": 0}

    for file_path in uploaded_files:
        ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name

        try:
            count = doc_loader.load_and_index(file_path)

            if ext == ".csv":
                results["csv"] += count
                print(f"   ✅ CSV indexed: {count} items")
            elif ext == ".pdf":
                results["pdf"] += count
                print(f"   ✅ PDF indexed: {count} chunks")

        except Exception as e:
            print(f"   ⚠️  Error indexing {filename}: {e}")

    print(f"\n✅ Total indexed: {results['csv'] + results['pdf']} documents")

    # Initialize agent
    print("\n🤖 Initializing agent...")
    if projects:
        print(f"   📊 Using {len(projects)} projects from CSV data")
    else:
        print("   📄 No CSV projects. Agent will analyze documents only.")

    try:
        agent = AgentFactory.create_agent(
            projects=projects,
            vector_store=vector_store,
            embedding_client=embedding_client,
            allow_fallback=True
        )
        executor_type = type(agent).__name__
        print(f"✅ Agent ready ({executor_type}) with {len(agent.tools)} tools")

    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)

    # Demo queries
    print("\n" + "=" * 90)
    print("💬 DEMO - Example Queries")
    print("=" * 90)

    demo_queries = [
        "What are the top 3 most expensive items?",
        "Are there any pricing anomalies or outliers?",
        "What information is in the plan documents?",
    ]

    for query in demo_queries:
        print(f"\n📍 Question: {query}")
        print("-" * 90)

        try:
            result = agent.query(query)
            # Print first 500 chars to keep it short
            output = result[:500] + "..." if len(result) > 500 else result
            print(output)
        except Exception as e:
            print(f"❌ Error: {e}")

    # Cleanup
    print("\n" + "=" * 90)
    shutil.rmtree(upload_dir, ignore_errors=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    print("✅ Demo complete\n")


if __name__ == "__main__":
    main()
