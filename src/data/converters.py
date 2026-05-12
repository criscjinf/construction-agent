"""Type-safe value converters for data parsing."""

from typing import Any, Optional
from datetime import datetime
import pandas as pd


class ValueConverter:
    """Utilities for type-safe value conversion with sensible defaults."""

    @staticmethod
    def to_string(value: Any, default: str = "") -> Optional[str]:
        """Safely convert value to string, returning None if null."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else default
        return str(value).strip()

    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """Safely convert value to float with fallback default."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """Safely convert value to int with fallback default."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_date(value: Any) -> Optional[datetime]:
        """Try to parse date from various formats, returning None on failure."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        try:
            if isinstance(value, str):
                return pd.to_datetime(value).date()
            return pd.to_datetime(value).date()
        except Exception:
            return None
