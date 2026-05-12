"""Base tool definition model."""

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Definition of a tool for Claude to call."""

    name: str
    description: str
    input_schema: dict
