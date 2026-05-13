"""Interactive shell for CLI user interactions."""

import logging

from src.config import Config


class InteractiveShell:
    """Manages interactive shell commands and query loop."""

    def __init__(self, agent, logger: logging.Logger):
        """
        Initialize interactive shell.

        Args:
            agent: Agent executor instance
            logger: Logger instance
        """
        self.agent = agent
        self.log = logger

    def run(self) -> None:
        """Start the interactive shell."""
        self._print_welcome()
        self._loop()

    def _print_welcome(self) -> None:
        """Print welcome message and instructions."""
        print("\n" + "=" * 90)
        print("💬 ANALYSIS MODE")
        print("=" * 90)
        print("\n💡 Ask questions about your documents!")
        print("\nExamples:")
        print('  • "What are the top 5 most expensive items?"')
        print('  • "What does the plan say about drainage?"')
        print('  • "Are there pricing anomalies?"')
        print('  • "Find information about..."')
        print("\nCommands: 'help', 'examples', 'quit'")
        print("=" * 90 + "\n")

        self.log.info("=" * 80)
        self.log.info("Ready for user queries")
        self.log.info("=" * 80)

    def _loop(self) -> None:
        """Run the main interaction loop."""
        while True:
            try:
                query = input("📍 You: ").strip()

                if not query:
                    self.log.debug("Empty query received, skipping...")
                    continue

                self.log.info(f"📍 User query: {query[:100]}{'...' if len(query) > 100 else ''}")

                if query.lower() == "quit":
                    self._handle_quit()
                    break

                if query.lower() == "help":
                    self.log.debug("User requested help")
                    self._handle_help()
                    continue

                if query.lower() == "examples":
                    self.log.debug("User requested examples")
                    self._handle_examples()
                    continue

                self._execute_query(query)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                self.log.error(f"Unexpected error: {e}", exc_info=True)
                print(f"\n❌ Error: {e}\n")

    def _execute_query(self, query: str) -> None:
        """
        Execute a user query through the agent.

        Args:
            query: User's natural language query
        """
        self.log.debug(f"🔄 Executing agent.query() for: {query[:80]}")
        print("\n🤖 Claude is analyzing...\n")
        print("-" * 90)

        try:
            self.log.info("🔧 Agent processing query...")
            result = self.agent.query(query)
            self.log.info("✅ Agent returned response")
            self.log.debug(f"Response length: {len(result)} characters")
            print(result)
            print("-" * 90 + "\n")
        except KeyboardInterrupt:
            self.log.warning("Query interrupted by user")
            print("\n❌ Query interrupted\n")
        except Exception as e:
            error_str = str(e)
            is_debug = Config.is_debug()
            self.log.error(f"❌ Query execution failed: {error_str}", exc_info=is_debug)
            if "credit" in error_str.lower() or "quota" in error_str.lower():
                print(f"\n⚠️  API Credits/Quota Exceeded\n")
                print("Using mock embeddings - search may be less accurate.")
            else:
                print(f"❌ Error: {e}\n")

    def _handle_help(self) -> None:
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

    def _handle_examples(self) -> None:
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

    def _handle_quit(self) -> None:
        """Handle quit command."""
        self.log.info("User requested quit")
        print("\n👋 Goodbye!\n")
