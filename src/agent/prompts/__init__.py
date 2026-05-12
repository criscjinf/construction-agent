"""Agent prompts - centralized prompt management."""

from src.agent.prompts.system import get_system_prompt, SYSTEM_PROMPT
from src.agent.prompts.examples import get_example_queries, EXAMPLE_QUERIES

__all__ = [
    "get_system_prompt",
    "SYSTEM_PROMPT",
    "get_example_queries",
    "EXAMPLE_QUERIES",
]
