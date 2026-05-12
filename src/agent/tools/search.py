"""Semantic search tool definitions."""

from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    """Input for semantic + keyword search."""

    query: str = Field(
        ...,
        description="Natural language search query",
        examples=["drainage requirements", "asphalt paving costs", "mobilization"]
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return"
    )
    threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )


class SearchOutput(BaseModel):
    """Output from search."""

    query: str = Field(..., description="Original search query")
    result_count: int = Field(..., description="Number of results found")
    results: list[dict] = Field(
        ...,
        description="List of results with content, source, similarity score"
    )
    interpretation: str = Field(
        ...,
        description="Summary of search results"
    )
