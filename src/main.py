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


def _validate_file_path(file_path: str) -> tuple[Path, str, float] | None:
    """
    Validate file path, extension, and size.
    Returns: (Path, extension, size_mb) or None if invalid
    """
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    ext = path.suffix.lower()
    if ext not in [".csv", ".pdf"]:
        print(f"❌ Invalid format: '.{ext[1:] if ext else 'no extension'}'")
        print(f"   Supported: .csv, .pdf")
        return None

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 100:
        print(f"❌ File too large: {size_mb:.1f}MB (max 100MB)")
        return None

    return path, ext, size_mb


def upload_file(upload_dir: str) -> tuple[str, str]:
    """
    Prompt user to upload a file.
    Returns: (file_path, file_type) or ('', '') if cancelled
    """
    print("\n📁 FILE UPLOAD")
    print("-" * 90)
    print("Supported formats: CSV, PDF")
    print()

    while True:
        file_path = input("📂 Enter file path (or 'cancel'): ").strip()

        if file_path.lower() == "cancel":
            return "", ""

        # Validate file
        result = _validate_file_path(file_path)
        if not result:
            continue

        path, ext, size_mb = result

        # Copy file to upload directory
        try:
            dest = Path(upload_dir) / path.name
            shutil.copy(str(path), str(dest))
            file_type = "csv" if ext == ".csv" else "pdf"
            print(f"✅ Uploaded: {path.name} ({size_mb:.1f}MB)")
            print(f"   Detected type: {file_type.upper()}")
            return str(dest), file_type
        except Exception as e:
            print(f"❌ Error: {e}")


def _validate_folder_path() -> str:
    """Prompt user for folder path with validation. Returns path or empty string if cancelled."""
    print("\n📁 FOLDER LOADING")
    print("-" * 90)

    while True:
        folder_path = input("📂 Enter folder path (or 'cancel'): ").strip()

        if folder_path.lower() == "cancel":
            return ""

        path = Path(folder_path)

        if not path.exists():
            print(f"❌ Folder not found: {folder_path}")
            continue

        if not path.is_dir():
            print(f"❌ Not a folder: {folder_path}")
            continue

        return folder_path


def _copy_folder_files(upload_dir: str, file_paths: list[str]) -> list[str]:
    """Copy files from source folder to upload directory."""
    imported_files = []
    for file_path in file_paths:
        try:
            src = Path(file_path)
            dst = Path(upload_dir) / src.name
            shutil.copy(str(src), str(dst))
            imported_files.append(str(dst))
        except Exception as e:
            print(f"   ⚠️  Error copying {src.name}: {e}")
    return imported_files


def _parse_csv_files(file_paths: list[str]) -> list:
    """Parse CSV files and extract project data."""
    projects = []
    for file_path in file_paths:
        if file_path.lower().endswith('.csv'):
            try:
                new_projects = CSVParser().parse(file_path)
                projects.extend(new_projects)
            except Exception as e:
                print(f"   ⚠️  Error parsing {Path(file_path).name}: {e}")
    return projects


def load_folder(upload_dir: str) -> tuple[list[str], list]:
    """
    Load folder: discover, copy, and parse CSV projects.
    Indexing happens later in _index_documents() for all files together.

    Orchestrates: validate → discover → copy → parse.
    """
    from src.data.document_loader import DocumentLoader

    # Get and validate folder path
    folder_path = _validate_folder_path()
    if not folder_path:
        return [], []

    try:
        # Discover files in folder (uses static method)
        file_paths, results = DocumentLoader.discover_files(folder_path)

        if not file_paths:
            print(f"❌ No CSV or PDF files found in {folder_path}")
            return [], []

        # Copy files to upload directory
        imported_files = _copy_folder_files(upload_dir, file_paths)

        # Parse CSV files for project data
        projects = _parse_csv_files(imported_files)

        print(f"\n✅ Loaded folder: {folder_path}")
        print(f"   • CSV files: {results['csv']}")
        print(f"   • PDF files: {results['pdf']}")
        print(f"   • Total files: {results['csv'] + results['pdf']}")
        print(f"   ℹ️  Files will be indexed in analysis phase")

        return imported_files, projects

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []


def load_documents():
    """
    Document loading menu: upload files, load folder, or start analysis.
    Returns: (upload_dir, uploaded_files, projects)
    """
    upload_dir = tempfile.mkdtemp(prefix="construction_agent_")
    uploaded_files = []
    projects = []

    print_header("📄 DOCUMENT LOADING")

    while True:
        print("\nOptions:")
        print("  1. Upload a file (auto-detect CSV/PDF)")
        print("  2. Load folder")
        print("  3. Start analysis")

        choice = input("\n👉 Choose (1-3): ").strip()

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
            folder_files, folder_projects = load_folder(upload_dir)
            if folder_files:
                uploaded_files.extend(folder_files)
                projects.extend(folder_projects)
                print(f"   ✅ Folder loaded: {len(folder_files)} files")

        elif choice == "3":
            break
        else:
            print("❌ Invalid option")

    if uploaded_files:
        print(f"\n✅ Documents ready for indexing: {len(uploaded_files)}")
    else:
        print("\n⚠️  No documents loaded. Using empty dataset.")

    return upload_dir, uploaded_files, projects


def _index_documents(
    uploaded_files: list[str],
    db_path: str,
    log
) -> tuple:
    """Index documents into vector store. Returns (vector_store, embedding_client, results)."""
    print_header("📊 INDEXING DOCUMENTS")

    log.info(f"📊 Initializing SQLite vector store at {db_path}")
    vector_store = SQLiteVectorStore(db_path=db_path)
    log.debug("✅ Vector store initialized")

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

    return vector_store, embedding_client, results


def _initialize_agent(projects: list, vector_store, embedding_client, log):
    """Initialize and return the agent executor."""
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

    return agent


def _handle_help_command():
    """Display help information."""
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


def _handle_examples_command():
    """Display example queries."""
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


def _execute_query(query: str, agent, log) -> bool:
    """Execute a single query. Returns True if successful, False on interrupt."""
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
        return True
    except KeyboardInterrupt:
        log.warning("Query interrupted by user")
        print("\n❌ Query interrupted\n")
        return False
    except Exception as e:
        error_str = str(e)
        is_debug = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
        log.error(f"❌ Query execution failed: {error_str}", exc_info=is_debug)
        if "credit" in error_str.lower() or "quota" in error_str.lower():
            print(f"\n⚠️  API Credits/Quota Exceeded\n")
            print("Using mock embeddings - search may be less accurate.")
        else:
            print(f"❌ Error: {e}\n")
        return True


def _run_interactive_loop(agent, log) -> None:
    """Run the main interactive query loop."""
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
                _handle_help_command()
                continue

            if query.lower() == "examples":
                log.debug("User requested examples")
                _handle_examples_command()
                continue

            _execute_query(query, agent, log)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def _cleanup(upload_dir: str, db_path: str, log) -> None:
    """Clean up temporary resources."""
    log.info("🧹 Cleaning up resources...")
    log.debug(f"Removing temporary directory: {upload_dir}")
    shutil.rmtree(upload_dir, ignore_errors=True)

    log.debug(f"Removing database: {db_path}")
    if os.path.exists(db_path):
        os.remove(db_path)

    log.info("=" * 80)
    log.info("✅ Agent session completed successfully")
    log.info("=" * 80)


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

    # Load documents
    log.info("📄 Starting document loading process...")
    upload_dir, uploaded_files, projects = load_documents()
    log.debug(f"Document loading complete: {len(uploaded_files)} files, {len(projects)} projects")

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    log.debug(f"Created temporary database: {db_path}")

    try:
        # Index documents
        vector_store, embedding_client = _index_documents(
            uploaded_files, db_path, log
        )[:2]

        # Initialize agent
        agent = _initialize_agent(projects, vector_store, embedding_client, log)

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

    # Run interactive loop
    _run_interactive_loop(agent, log)

    # Cleanup
    _cleanup(upload_dir, db_path, log)


if __name__ == "__main__":
    main()
