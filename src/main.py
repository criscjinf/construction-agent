#!/usr/bin/env python
"""
Construction Estimating Agent — Command-line interface.

Interactive CLI for analyzing construction bid data and answering queries.

Usage:
    python src/main.py --file data/sample_bid_tabulation.csv
    python src/main.py --query "Top 5 expensive items?"
"""

import sys
import logging
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click")
    sys.exit(1)

from src.data.loaders import DataLoader
from src.data.validators import DataValidator
from src.vectorstore.storage import SQLiteVectorStore
from src.agent.core import AgentExecutor
from src.config import get_settings

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("construction_agent.log"),
            logging.StreamHandler()
        ]
    )


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, debug):
    """Construction Estimating Agent — Analyze bid data and answer queries."""
    setup_logging(debug)
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="Path to CSV or PDF file"
)
@click.option(
    "--query",
    type=str,
    help="Query to execute (optional; interactive if not provided)"
)
@click.option(
    "--vector-store",
    type=click.Path(),
    default="construction_agent.db",
    help="Path to vector store database"
)
@click.pass_context
def analyze(ctx, file: Optional[str], query: Optional[str], vector_store: str):
    """
    Analyze bid data and execute agent queries.

    Examples:
        # Interactive mode with CSV file
        python src/main.py analyze --file data/sample_bid_tabulation.csv

        # Single query mode
        python src/main.py analyze --file data/sample_bid_tabulation.csv \\
            --query "Top 5 most expensive items?"

        # Load multiple files
        python src/main.py analyze --file data/bid_tabulation.csv \\
            --query "Compare bidders on MOBILIZATION"
    """
    try:
        # Load settings
        settings = get_settings()

        # Validate input
        if not file:
            click.echo("Error: --file is required", err=True)
            sys.exit(1)

        file_path = Path(file)
        if not file_path.exists():
            click.echo(f"Error: File not found: {file_path}", err=True)
            sys.exit(1)

        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            click.echo(
                f"Error: File too large ({file_size_mb:.1f}MB > {settings.max_file_size_mb}MB)",
                err=True
            )
            sys.exit(1)

        # Load data
        click.echo(f"📂 Loading {file_path.name}...", err=True)
        try:
            projects = DataLoader.load(str(file_path))
        except Exception as e:
            click.echo(f"Error loading file: {e}", err=True)
            logger.exception("Failed to load file")
            sys.exit(1)

        if not projects:
            click.echo("Error: No valid projects found in file", err=True)
            sys.exit(1)

        click.echo(f"✓ Loaded {len(projects)} project(s)", err=True)

        # Validate data quality
        click.echo("🔍 Validating data...", err=True)
        for project in projects:
            report = DataValidator.validate_project(project)
            if report.error_count > 0:
                click.echo(
                    f"⚠️  {project.proj_id}: {report.error_count} errors, "
                    f"{report.warning_count} warnings",
                    err=True
                )

        # Initialize vector store (for semantic search)
        try:
            vs = SQLiteVectorStore(database_url=f"sqlite:///{vector_store}")
        except Exception as e:
            click.echo(f"⚠️  Vector store unavailable: {e}", err=True)
            vs = None

        # Initialize agent
        click.echo("🤖 Initializing agent...", err=True)
        agent = AgentExecutor(projects=projects, vector_store=vs)

        # Execute query or start interactive mode
        if query:
            # Single query mode
            click.echo("", err=True)
            _execute_query(agent, query)
        else:
            # Interactive mode
            _interactive_mode(agent)

    except Exception as e:
        click.echo(f"Fatal error: {e}", err=True)
        logger.exception("Fatal error in analyze")
        sys.exit(1)


def _execute_query(agent: AgentExecutor, query: str) -> None:
    """Execute a single query and display result."""
    click.echo(f"🔍 Query: {query}", err=True)
    click.echo("-" * 60, err=True)

    try:
        result = agent.query(query)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error executing query: {e}", err=True)
        logger.exception("Query execution failed")
        sys.exit(1)


def _interactive_mode(agent: AgentExecutor) -> None:
    """Start interactive query loop."""
    click.echo("\n📝 Interactive Mode (type 'help' for commands, 'quit' to exit)", err=True)
    click.echo("-" * 60, err=True)

    commands = {
        "help": "Show help message",
        "quit": "Exit interactive mode",
        "examples": "Show example queries",
    }

    while True:
        try:
            query = click.prompt("Query", type=str).strip()

            if not query:
                continue

            if query.lower() == "quit":
                click.echo("👋 Goodbye!", err=True)
                break

            if query.lower() == "help":
                click.echo("\nAvailable commands:", err=True)
                for cmd, desc in commands.items():
                    click.echo(f"  {cmd}: {desc}", err=True)
                click.echo("\nExample queries:", err=True)
                click.echo("  What are the top 5 most expensive items?", err=True)
                click.echo("  Are there any suspicious prices?", err=True)
                click.echo("  How do bidders compare on MOBILIZATION?", err=True)
                continue

            if query.lower() == "examples":
                _show_examples()
                continue

            # Execute query
            click.echo("-" * 60, err=True)
            _execute_query(agent, query)
            click.echo("-" * 60, err=True)

        except KeyboardInterrupt:
            click.echo("\n\n👋 Goodbye!", err=True)
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            logger.exception("Query execution failed")


def _show_examples() -> None:
    """Display example queries."""
    examples = [
        "What are the top 5 most expensive bid items?",
        "Are there any items with unit prices that deviate significantly?",
        "How do bidders compare on MOBILIZATION?",
        "Which items have the most bidder competition?",
        "Compare prices for ASPHALT SURFACE across all bidders",
        "What's the median price for items matching ASPHALT?",
        "Show me items with highest extended amounts",
    ]
    click.echo("\n💡 Example queries:", err=True)
    for i, example in enumerate(examples, 1):
        click.echo(f"  {i}. {example}", err=True)
    click.echo()


@cli.command()
def validate():
    """Validate project data from CSV file."""
    file = click.prompt("File path", type=click.Path(exists=True))

    try:
        click.echo(f"Loading {file}...")
        projects = DataLoader.load(file)

        if not projects:
            click.echo("No projects found")
            return

        click.echo(f"Found {len(projects)} project(s)\n")

        for project in projects:
            report = DataValidator.validate_project(project)
            click.echo(f"Project {project.proj_id}:")
            click.echo(f"  Items: {len(project.items)}")
            click.echo(f"  Bidders: {len(project.bidders)}")
            click.echo(f"  Errors: {report.error_count}")
            click.echo(f"  Warnings: {report.warning_count}")

            if report.issues:
                click.echo("  Issues:")
                for issue in report.issues[:5]:  # Show first 5
                    click.echo(f"    - {issue}")
                if len(report.issues) > 5:
                    click.echo(f"    ... and {len(report.issues) - 5} more")
            click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception("Validation failed")
        sys.exit(1)


def main():
    """Entry point."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
