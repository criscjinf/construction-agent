#!/usr/bin/env python3
"""
Document upload and analysis system.
Upload CSV and PDF files, then query the agent about them.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

try:
    from src.data.loaders import DataLoader
    from src.data.document_loader import DocumentLoader
    from src.vectorstore.storage import SQLiteVectorStore
    from src.agent.core import AgentExecutor
except ImportError:
    print("❌ Error: Cannot import modules")
    sys.exit(1)


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)


def upload_file(upload_dir: str) -> str:
    """
    Prompt user to upload a file.

    Args:
        upload_dir: Directory to store uploaded files

    Returns:
        Path to uploaded file or empty string if cancelled
    """
    print("\n📁 FILE UPLOAD")
    print("-" * 90)
    print("Supported formats:")
    print("  • CSV  — Bid tabulation data (any columns)")
    print("  • PDF  — Construction plans, specifications, etc")
    print()

    while True:
        file_path = input("📂 Enter file path (or 'cancel' to skip): ").strip()

        if file_path.lower() == "cancel":
            return ""

        path = Path(file_path)

        # Validate file exists
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        # Validate file type
        ext = path.suffix.lower()
        if ext not in [".csv", ".pdf"]:
            print(f"❌ Unsupported format: {ext}")
            print("   Supported: .csv, .pdf")
            continue

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            print(f"❌ File too large: {size_mb:.1f}MB (max 100MB)")
            continue

        # Copy file to upload directory
        try:
            dest = Path(upload_dir) / path.name
            shutil.copy(str(path), str(dest))
            print(f"✅ File uploaded: {path.name} ({size_mb:.1f}MB)")
            return str(dest)
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            continue


def main():
    print_header("🚀 CONSTRUCTION AGENT - DOCUMENT UPLOAD & ANALYSIS")

    # Create temporary directory for uploads
    upload_dir = tempfile.mkdtemp(prefix="construction_agent_")
    print(f"\n📂 Upload directory: {upload_dir}")

    # Create vector store
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    vector_store = SQLiteVectorStore(db_path=db_path)
    doc_loader = DocumentLoader(vector_store=vector_store, use_mock_embeddings=True)

    uploaded_files = []
    projects = []

    # Upload documents loop
    while True:
        print_header("📄 DOCUMENT UPLOAD")

        if uploaded_files:
            print("\n📋 Uploaded documents:")
            for i, f in enumerate(uploaded_files, 1):
                print(f"  {i}. {Path(f).name}")

        print("\nOptions:")
        print("  1. Upload CSV (bid tabulation data)")
        print("  2. Upload PDF (plans, specifications)")
        print("  3. Start analysis")
        print("  4. Quit")

        choice = input("\n👉 Choose option (1-4): ").strip()

        if choice == "1":
            file_path = upload_file(upload_dir)
            if file_path:
                uploaded_files.append(file_path)

                # Load projects from CSV
                try:
                    new_projects = DataLoader.load(file_path)
                    projects.extend(new_projects)
                    print(f"✅ Loaded {len(new_projects)} projects")
                except Exception as e:
                    print(f"❌ Error loading CSV: {e}")

        elif choice == "2":
            file_path = upload_file(upload_dir)
            if file_path:
                uploaded_files.append(file_path)

        elif choice == "3":
            if not uploaded_files:
                print("\n❌ No documents uploaded yet!")
                continue

            break

        elif choice == "4":
            print("\n👋 Goodbye!")
            shutil.rmtree(upload_dir)
            sys.exit(0)

        else:
            print("❌ Invalid option")

    # Index all uploaded documents
    print_header("📊 INDEXING DOCUMENTS")

    results = {"csv": 0, "pdf": 0}

    for file_path in uploaded_files:
        ext = Path(file_path).suffix.lower()

        try:
            if ext == ".csv":
                count = doc_loader.load_and_index_csv(file_path)
                results["csv"] += count
                print(f"✅ Indexed CSV: {count} items")

            elif ext == ".pdf":
                count = doc_loader.load_and_index_pdf(file_path)
                results["pdf"] += count
                print(f"✅ Indexed PDF: {count} chunks")

        except Exception as e:
            print(f"❌ Error indexing {Path(file_path).name}: {e}")

    print(f"\n📈 Indexing complete:")
    print(f"   • CSV items: {results['csv']}")
    print(f"   • PDF chunks: {results['pdf']}")
    print(f"   • Total: {results['csv'] + results['pdf']} documents")

    # Initialize agent
    print_header("🤖 INITIALIZING AGENT")

    try:
        if not projects:
            # Create dummy project if only PDFs were uploaded
            from src.data.models import Project
            projects = [Project(proj_id="PDF_DOCS", proj_name="Uploaded Documents", items=[])]

        agent = AgentExecutor(projects=projects, vector_store=vector_store)
        print(f"✅ Agent ready with {len(agent.tools)} tools")

    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)

    # Query loop
    print_header("💬 DOCUMENT ANALYSIS")
    print("\n💡 You can now ask questions about your uploaded documents!")
    print("\nExamples:")
    print('  • "What are the top items by price?"')
    print('  • "What does the plan say about...?"')
    print('  • "Find information about..."')
    print("\nCommands: 'help', 'quit'")

    while True:
        try:
            query = input("\n📍 Your question: ").strip()

            if not query:
                continue

            if query.lower() == "quit":
                print("\n👋 Goodbye!\n")
                break

            if query.lower() == "help":
                print_header("HELP")
                print("\nClaude can analyze your uploaded documents:")
                print("\n📊 CSV Data:")
                print("  • Find top/bottom items by any metric")
                print("  • Detect price anomalies")
                print("  • Compare bidders")
                print("  • Statistical analysis")

                print("\n📄 PDF Documents:")
                print("  • Search for specific information")
                print("  • Extract key details")
                print("  • Summarize content")
                print("  • Answer domain-specific questions")

                print("\nJust ask natural language questions!")
                continue

            # Execute query
            print("\n🤖 Analyzing documents...\n")
            print("-" * 90)

            try:
                result = agent.query(query)
                print(result)
                print("-" * 90)

            except KeyboardInterrupt:
                print("\n❌ Query interrupted")
            except Exception as e:
                error_str = str(e)
                if "credit" in error_str.lower():
                    print(f"\n⚠️  API Credits Exhausted")
                    print("\nUsing mock embeddings - search may be less accurate.")
                    print("Consider using test_pdf_agent.py for better performance.")
                else:
                    print(f"❌ Error: {e}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    # Cleanup
    print("\n🧹 Cleaning up...")
    shutil.rmtree(upload_dir)
    if os.path.exists(db_path):
        os.remove(db_path)

    print("✅ Done\n")


if __name__ == "__main__":
    main()
