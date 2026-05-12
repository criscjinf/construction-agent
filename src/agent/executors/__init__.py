"""Agent executors - extensible agent implementations."""

from src.agent.executors.base import BaseAgentExecutor
from src.agent.executors.anthropic import AnthropicAgentExecutor
from src.agent.executors.mock import MockAgentExecutor
from src.agent.executors.factory import AgentFactory

# For backward compatibility, also export as AgentExecutor
AgentExecutor = AnthropicAgentExecutor

__all__ = [
    "BaseAgentExecutor",
    "AnthropicAgentExecutor",
    "MockAgentExecutor",
    "AgentFactory",
    "AgentExecutor",  # backward compatible
]
