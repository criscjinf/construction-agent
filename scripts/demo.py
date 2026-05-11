#!/usr/bin/env python3
"""
Demo - Mostra o fluxo completo com dados já em data/
"""

import sys
from pathlib import Path

# Add project root to path so imports work from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import os
import shutil
from dotenv import load_dotenv

load_dotenv(".env")

try:
    from src.data.loaders import DataLoader
    from src.data.document_loader import DocumentLoader
    from src.vectorstore.storage import SQLiteVectorStore
    from src.agent.core import AgentExecutor
    from src.data.models import Project
except ImportError:
    print("❌ Cannot import modules")
    sys.exit(1)


def main():
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
                new_projects = DataLoader.load(str(csv_file))
                projects.extend(new_projects)
                print(f"   ✅ CSV: {csv_file.name}")
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

    # Create vector store
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Index documents
    print("\n📊 Indexing documents...")
    vector_store = SQLiteVectorStore(db_path=db_path)
    doc_loader = DocumentLoader(vector_store=vector_store, use_mock_embeddings=True)

    results = {"csv": 0, "pdf": 0}

    for file_path in uploaded_files:
        ext = Path(file_path).suffix.lower()

        try:
            if ext == ".csv":
                count = doc_loader.load_and_index_csv(file_path)
                results["csv"] += count
                print(f"   ✅ CSV indexed: {count} items")

            elif ext == ".pdf":
                count = doc_loader.load_and_index_pdf(file_path)
                results["pdf"] += count
                print(f"   ✅ PDF indexed: {count} chunks")

        except Exception as e:
            print(f"   ⚠️  Error: {e}")

    print(f"\n✅ Total indexed: {results['csv'] + results['pdf']} documents")

    # Initialize agent
    print("\n🤖 Initializing agent...")

    if not projects:
        projects = [Project(proj_id="DOCS", proj_name="Documents", items=[])]

    try:
        agent = AgentExecutor(projects=projects, vector_store=vector_store)
        print(f"✅ Agent ready with {len(agent.tools)} tools")

    except Exception as e:
        print(f"❌ Error: {e}")
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
