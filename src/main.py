#!/usr/bin/env python3
"""
Construction Estimating Agent - Single Entry Point
Upload documents (CSV/PDF) OR load from data/ folder, then ask questions
"""

import tempfile
import os
import shutil
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(".env")

# Logging (initialized in main())
from src.logging_config import initialize_logging, get_logger
log = None  # Will be initialized in main()

try:
    from src.data.parsers import CSVParser
    from src.data.document_loader import DocumentLoader
    from src.data.indexers import IndexersFactory
    from src.vectorstore.storage import SQLiteVectorStore
    from src.vectorstore.embeddings import OpenAIEmbeddingClient
    from src.agent.executors import AgentFactory
except ImportError:
    print("❌ Error: Cannot import modules. Make sure you're in the project root.")
    import sys
    sys.exit(1)


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)


def upload_file(upload_dir: str) -> tuple[str, str]:
    """
    Prompt user to upload a file and detect type automatically.
    Returns: (file_path, file_type) where file_type is 'csv' or 'pdf'
    Returns: ('', '') if cancelled or invalid
    """
    print("\n📁 FILE UPLOAD")
    print("-" * 90)
    print("Supported formats: CSV, PDF")
    print()

    while True:
        file_path = input("📂 Enter file path (or 'cancel'): ").strip()

        if file_path.lower() == "cancel":
            return "", ""

        path = Path(file_path)

        # Check file exists
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        # Check extension
        ext = path.suffix.lower()
        if ext not in [".csv", ".pdf"]:
            print(f"❌ Invalid format: '.{ext[1:] if ext else 'no extension'}'")
            print(f"   Supported: .csv, .pdf")
            continue

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            print(f"❌ File too large: {size_mb:.1f}MB (max 100MB)")
            continue

        # Copy file
        try:
            dest = Path(upload_dir) / path.name
            shutil.copy(str(path), str(dest))
            file_type = "csv" if ext == ".csv" else "pdf"
            print(f"✅ Uploaded: {path.name} ({size_mb:.1f}MB)")
            print(f"   Detected type: {file_type.upper()}")
            return str(dest), file_type
        except Exception as e:
            print(f"❌ Error: {e}")


def load_documents():
    """
    Upload documents loop: let user upload multiple files or start analysis.
    Returns: (upload_dir, uploaded_files, projects)
    """
    upload_dir = tempfile.mkdtemp(prefix="construction_agent_")
    uploaded_files = []
    projects = []

    print_header("📄 DOCUMENT LOADING")

    while True:
        print("\nOptions:")
        print("  1. Upload a file (auto-detect CSV/PDF)")
        print("  2. Start analysis")

        choice = input("\n👉 Choose (1-2): ").strip()

        if choice == "1":
            file_path, file_type = upload_file(upload_dir)
            if file_path:
                uploaded_files.append(file_path)

                # Auto-process based on detected type
                if file_type == "csv":
                    try:
                        new_projects = CSVParser().parse(file_path)
                        projects.extend(new_projects)
                        print(f"   ✅ CSV parsed: {len(new_projects)} projects")
                    except Exception as e:
                        print(f"   ⚠️  Error parsing CSV: {e}")
                elif file_type == "pdf":
                    print(f"   ✅ PDF will be indexed during analysis")

        elif choice == "2":
            break
        else:
            print("❌ Invalid option")

    if uploaded_files:
        print(f"\n✅ Documents ready for indexing: {len(uploaded_files)}")
    else:
        print("\n⚠️  No documents loaded. Using empty dataset.")

    return upload_dir, uploaded_files, projects


def main():
    global log

    # Initialize logging at runtime (not at import time)
    initialize_logging()
    log = get_logger("construction_agent")

    print_header("🤖 CONSTRUCTION ESTIMATING AGENT")

    log.info("=" * 80)
    log.info(f"Starting Construction Agent | Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    log.info(f"Config: LOG_LEVEL={os.getenv('LOG_LEVEL', 'INFO')}, LOG_FILE={os.getenv('LOG_FILE')}")
    log.info("=" * 80)

    # Load documents (upload or from data/)
    log.info("📄 Starting document loading process...")
    upload_dir, uploaded_files, projects = load_documents()
    log.debug(f"Document loading complete: {len(uploaded_files)} files, {len(projects)} projects")

    # Create vector store
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    log.debug(f"Created temporary database: {db_path}")

    try:
        # Initialize vector store and index documents
        print_header("📊 INDEXING DOCUMENTS")

        log.info(f"📊 Initializing SQLite vector store at {db_path}")
        vector_store = SQLiteVectorStore(db_path=db_path)
        log.debug("✅ Vector store initialized")

        # Initialize embedding client (must have OpenAI API key)
        openai_key = os.getenv("OPENAI_API_KEY")

        if not openai_key:
            log.error("❌ OPENAI_API_KEY not configured in .env")
            log.info("To use document indexing, set OPENAI_API_KEY in your .env file")
            import sys
            sys.exit(1)

        try:
            embedding_client = OpenAIEmbeddingClient()
            log.info("📦 Initializing indexers with OpenAI embeddings")
            log.debug("Using OpenAI text-embedding-3-small")
        except Exception as e:
            log.error(f"❌ Failed to initialize OpenAI embeddings: {e}")
            log.info("Check that OPENAI_API_KEY is valid and you have sufficient credits")
            import sys
            sys.exit(1)

        indexers_factory = IndexersFactory(vector_store=vector_store, embedding_client=embedding_client)
        doc_loader = DocumentLoader(indexers_factory=indexers_factory)
        log.debug("✅ DocumentLoader initialized with factory")

        results = {"csv": 0, "pdf": 0}

        log.info(f"📄 Starting indexing of {len(uploaded_files)} documents...")
        for file_path in uploaded_files:
            filename = Path(file_path).name
            ext = Path(file_path).suffix.lower()

            try:
                log.debug(f"🔄 Indexing {ext.upper()}: {filename}")
                count = doc_loader.load_and_index(file_path)

                if ext == ".csv":
                    results["csv"] += count
                    log.info(f"   ✅ CSV indexed: {filename} ({count} items)")
                elif ext == ".pdf":
                    results["pdf"] += count
                    log.info(f"   ✅ PDF indexed: {filename} ({count} chunks)")

            except Exception as e:
                is_debug = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
                log.error(f"❌ Error indexing {filename}: {e}", exc_info=is_debug)
                print(f"⚠️  Error indexing {filename}: {e}")

        log.info(f"✅ Indexing complete: CSV={results['csv']}, PDF={results['pdf']}")
        print(f"\n✅ Indexing complete:")
        print(f"   • CSV items: {results['csv']}")
        print(f"   • PDF chunks: {results['pdf']}")
        print(f"   • Total: {results['csv'] + results['pdf']}")

        # Initialize agent
        print_header("🤖 INITIALIZING AGENT")

        log.info("🤖 Initializing Claude agent...")
        if not projects:
            from src.data.models import Project
            projects = [Project(proj_id="DOCS", proj_name="Uploaded Documents", items=[])]
            log.debug("Created dummy project for documents without CSV data")

        log.debug(f"Creating agent with {len(projects)} projects and vector_store")
        agent = AgentFactory.create_agent(
            projects=projects,
            vector_store=vector_store,
            embedding_client=embedding_client,
            allow_fallback=True
        )
        executor_type = type(agent).__name__
        log.info(f"✅ Agent ready: {executor_type} with {len(agent.tools)} tools")

        print(f"✅ Agent ready with {len(agent.tools)} tools")
        print("   • Search (CSV + PDF)")
        print("   • Top Items")
        print("   • Outlier Detection")
        print("   • Bidder Comparison")

    except KeyboardInterrupt:
        print("\n❌ Initialization interrupted")
        import sys
        sys.exit(1)
    except ValueError as e:
        print(f"\n{str(e)}\n")
        import sys
        sys.exit(1)
    except Exception as e:
        error_str = str(e)
        if "credit" in error_str.lower() or "quota" in error_str.lower():
            print(f"\n⚠️  API INITIALIZATION ERROR\n")
            print(f"❌ {error_str}\n")
            print("💡 Using mock embeddings instead.\n")
        else:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        import sys
        sys.exit(1)

    # Interactive conversation loop
    print_header("💬 ANALYSIS MODE")
    print("\n💡 Ask questions about your documents!")
    print("\nExamples:")
    print('  • "What are the top 5 most expensive items?"')
    print('  • "What does the plan say about drainage?"')
    print('  • "Are there pricing anomalies?"')
    print('  • "Find information about..."')
    print("\nCommands: 'help', 'examples', 'quit'")
    print("=" * 90 + "\n")

    log.info("=" * 80)
    log.info("Ready for user queries")
    log.info("=" * 80)

    while True:
        try:
            query = input("📍 You: ").strip()

            if not query:
                log.debug("Empty query received, skipping...")
                continue

            log.info(f"📍 User query: {query[:100]}{'...' if len(query) > 100 else ''}")

            if query.lower() == "quit":
                log.info("User requested quit")
                print("\n👋 Goodbye!\n")
                break

            if query.lower() == "help":
                log.debug("User requested help")
                print("\n" + "=" * 90)
                print("HELP")
                print("=" * 90)
                print("\nClaude can analyze your documents:")
                print("\n📊 CSV Data:")
                print("  • Find top/bottom items")
                print("  • Detect price anomalies")
                print("  • Compare bidders")
                print("  • Statistical analysis")
                print("\n📄 PDF Documents:")
                print("  • Search for information")
                print("  • Extract specifications")
                print("  • Answer questions")
                print("\nJust ask in natural language!")
                print("=" * 90 + "\n")
                continue

            if query.lower() == "examples":
                log.debug("User requested examples")
                print("\n" + "=" * 90)
                print("EXAMPLE QUERIES")
                print("=" * 90)
                examples = [
                    "What are the top 5 most expensive bid items?",
                    "Are there any pricing anomalies?",
                    "Compare bidders on MOBILIZATION",
                    "What does the plan say about drainage?",
                    "What are the key project specifications?",
                    "Which items have highest price variance?",
                    "Summarize the plan content",
                    "Find information about pavement marking",
                ]
                for i, ex in enumerate(examples, 1):
                    print(f"  {i}. {ex}")
                print("=" * 90 + "\n")
                continue

            # Execute query
            log.debug(f"🔄 Executing agent.query() for: {query[:80]}")
            print("\n🤖 Claude is analyzing...\n")
            print("-" * 90)

            try:
                log.info("🔧 Agent processing query...")
                result = agent.query(query)
                log.info("✅ Agent returned response")
                log.debug(f"Response length: {len(result)} characters")
                print(result)
                print("-" * 90 + "\n")

            except KeyboardInterrupt:
                log.warning("Query interrupted by user")
                print("\n❌ Query interrupted\n")
            except Exception as e:
                error_str = str(e)
                is_debug = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
                log.error(f"❌ Query execution failed: {error_str}", exc_info=is_debug)
                if "credit" in error_str.lower() or "quota" in error_str.lower():
                    print(f"\n⚠️  API Credits/Quota Exceeded\n")
                    print("Using mock embeddings - search may be less accurate.")
                else:
                    print(f"❌ Error: {e}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    # Cleanup
    log.info("🧹 Cleaning up resources...")
    log.debug(f"Removing temporary directory: {upload_dir}")
    shutil.rmtree(upload_dir, ignore_errors=True)

    log.debug(f"Removing database: {db_path}")
    if os.path.exists(db_path):
        os.remove(db_path)

    log.info("=" * 80)
    log.info("✅ Agent session completed successfully")
    log.info("=" * 80)


if __name__ == "__main__":
    main()
