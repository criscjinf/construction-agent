#!/usr/bin/env python3
"""
Construction Estimating Agent - Main Entry Point
Orchestrates document loading, indexing, agent initialization, and interactive analysis.
"""

import tempfile
import os
import shutil
import sys
import traceback

from dotenv import load_dotenv
load_dotenv(".env")

from src.config import Config
from src.logging_config import initialize_logging, get_logger
from src.ui import FileLoader
from src.data.indexers import IndexOrchestrator
from src.agent.executors import AgentFactory
from src.cli import InteractiveShell


def _print_header(title: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)


def _initialize_agent(projects: list, vector_store, embedding_client, logger):
    """Initialize and return the agent executor."""
    _print_header("🤖 INITIALIZING AGENT")

    logger.info("🤖 Initializing Claude agent...")
    if projects:
        logger.debug(f"Creating agent with {len(projects)} projects from CSV data")
    else:
        logger.debug("No CSV projects loaded. Agent will analyze documents only.")

    agent = AgentFactory.create_agent(
        projects=projects,
        vector_store=vector_store,
        embedding_client=embedding_client,
        allow_fallback=True
    )
    executor_type = type(agent).__name__
    logger.info(f"✅ Agent ready: {executor_type} with {len(agent.tools)} tools")

    print(f"✅ Agent ready with {len(agent.tools)} tools")
    print("   • Search (CSV + PDF)")
    print("   • Top Items")
    print("   • Outlier Detection")
    print("   • Bidder Comparison")

    return agent


def _cleanup(upload_dir: str, db_path: str, logger) -> None:
    """Clean up temporary resources."""
    logger.info("🧹 Cleaning up resources...")
    logger.debug(f"Removing temporary directory: {upload_dir}")
    shutil.rmtree(upload_dir, ignore_errors=True)

    logger.debug(f"Removing database: {db_path}")
    if os.path.exists(db_path):
        os.remove(db_path)

    logger.info("=" * 80)
    logger.info("✅ Agent session completed successfully")
    logger.info("=" * 80)


def main():
    """Main entry point: orchestrate document loading, indexing, and analysis."""
    # Initialize logging at runtime (not at import time)
    initialize_logging()
    logger = get_logger("construction_agent")

    _print_header("🤖 CONSTRUCTION ESTIMATING AGENT")

    logger.info("=" * 80)
    logger.info(f"Starting Construction Agent | Log Level: {Config.LOG_LEVEL}")
    logger.info(f"Config: {Config}")
    logger.info("=" * 80)

    # Load documents using specialized FileLoader
    logger.info("📄 Starting document loading process...")
    file_loader = FileLoader()
    uploaded_files, projects = file_loader.load_documents()
    upload_dir = file_loader.upload_dir
    logger.debug(f"Document loading complete: {len(uploaded_files)} files, {len(projects)} projects")

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    logger.debug(f"Created temporary database: {db_path}")

    try:
        # Index documents using orchestrator
        orchestrator = IndexOrchestrator(logger)
        vector_store, embedding_client, _ = orchestrator.index_files(uploaded_files, db_path)

        # Initialize agent
        agent = _initialize_agent(projects, vector_store, embedding_client, logger)

    except KeyboardInterrupt:
        print("\n❌ Initialization interrupted")
        sys.exit(1)
    except ValueError as e:
        print(f"\n{str(e)}\n")
        sys.exit(1)
    except Exception as e:
        error_str = str(e)
        if "credit" in error_str.lower() or "quota" in error_str.lower():
            print(f"\n⚠️  API INITIALIZATION ERROR\n")
            print(f"❌ {error_str}\n")
            print("💡 Using mock embeddings instead.\n")
        else:
            print(f"❌ Error: {e}")
            traceback.print_exc()
        sys.exit(1)

    # Run interactive shell
    shell = InteractiveShell(agent, logger)
    shell.run()

    # Cleanup
    _cleanup(upload_dir, db_path, logger)


if __name__ == "__main__":
    main()
