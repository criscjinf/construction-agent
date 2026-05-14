from pydantic import BaseModel, Field


class DataQualityReport(BaseModel):
    """Report of data quality issues found during parsing."""

    warnings: list[str] = Field(default_factory=list, description="Non-fatal issues")
    missing_fields: dict[str, int] = Field(default_factory=dict, description="Field: count of missing")
    inconsistencies: list[str] = Field(default_factory=list, description="Data type or value issues")

    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return bool(self.warnings or self.missing_fields or self.inconsistencies)
