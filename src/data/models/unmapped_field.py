"""Model for storing unmapped/unknown CSV fields."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class UnmappedField(BaseModel):
    """Represents an unmapped column from CSV with inferred type information."""

    raw: str = Field(..., description="Original string value from CSV")
    inferred_type: Literal["numeric", "date", "string"] = Field(
        ..., description="Auto-detected type"
    )
    parsed_value: Optional[float] = Field(
        default=None, description="Parsed numeric value (if inferred_type == 'numeric')"
    )

    def get_numeric_value(self) -> Optional[float]:
        """Get numeric value if available, None otherwise."""
        return self.parsed_value

    def get_string_value(self) -> str:
        """Always return the raw string value."""
        return self.raw
