"""
Parsers for construction data with adaptive schema inference.

Key strategy: No hardcoded column names. Instead, infer schema from data.
This handles columns that are renamed, missing, or in different order.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np

from src.data.models import (
    Project,
    BidItem,
    Bidder,
    DataQualityReport,
)

logger = logging.getLogger(__name__)


class SchemaMapping:
    """Inferred column mappings with aliases and types."""

    def __init__(self):
        self.proj_id_col: Optional[str] = None
        self.let_dt_col: Optional[str] = None
        self.county_col: Optional[str] = None
        self.item_no_col: Optional[str] = None
        self.item_desc_col: Optional[str] = None
        self.unit_col: Optional[str] = None
        self.qty_col: Optional[str] = None
        self.eng_est_col: Optional[str] = None
        self.bidder_col: Optional[str] = None
        self.bid_rank_col: Optional[str] = None
        self.unit_pr_col: Optional[str] = None
        self.ext_amt_col: Optional[str] = None
        self.bid_total_col: Optional[str] = None
        self.warnings: list[str] = []

    def is_complete(self) -> bool:
        """Check if all critical fields are mapped."""
        return all([
            self.proj_id_col,
            self.item_no_col,
            self.item_desc_col,
            self.unit_col,
            self.qty_col,
            self.bidder_col,
            self.unit_pr_col,
        ])


class BaseParser(ABC):
    """Abstract base for all parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> list[Project]:
        """Parse file and return list of Project objects."""
        pass


class CSVParser(BaseParser):
    """CSV parser with adaptive schema inference."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.schema: Optional[SchemaMapping] = None
        self.quality_report = DataQualityReport()

    def parse(self, file_path: str) -> list[Project]:
        """Parse CSV file with inferred schema."""
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV {file_path}: {e}")
            raise

        if df.empty:
            logger.warning(f"CSV file is empty: {file_path}")
            return []

        # Infer schema from data
        self.schema = self._infer_schema(df)

        if not self.schema.is_complete():
            logger.warning(f"Could not map all required columns. Found: {self.schema.warnings}")

        # Parse rows
        projects = self._parse_rows(df)

        if self.verbose:
            logger.info(f"Parsed {len(projects)} projects from {file_path}")

        return projects

    def _infer_schema(self, df: pd.DataFrame) -> SchemaMapping:
        """Infer column mappings from CSV headers."""
        schema = SchemaMapping()
        columns = df.columns.tolist()

        # Define search patterns for each field (in priority order)
        patterns = {
            "proj_id": ["PROJ_ID", "proj_id", "PROJECT_ID", "project_id", "PROJ", "proj"],
            "let_dt": ["LET_DT", "let_dt", "letting_date", "LET_DATE", "DATE", "date"],
            "county": ["CNTY", "cnty", "COUNTY", "county", "CO", "COUNTY_NAME"],
            "item_no": ["ITEM_NO", "item_no", "ITEM_NUM", "item_num", "ITEM_ID"],
            "item_desc": ["ITEM_DESC", "item_desc", "DESCRIPTION", "description", "DESC"],
            "unit": ["UNIT", "unit", "UNITS", "units", "UOM", "uom"],
            "qty": ["QTY", "qty", "QUANTITY", "quantity", "QNTY"],
            "eng_est": ["ENG_EST_UNIT_PR", "eng_est_unit_pr", "EST_UNIT_PRICE", "est_unit_price"],
            "bidder": ["BIDDER", "bidder", "CONTRACTOR", "contractor", "COMPANY", "company"],
            "bid_rank": ["BID_RANK", "bid_rank", "RANK", "rank", "BID_NO"],
            "unit_pr": ["UNIT_PR", "unit_pr", "UNIT_PRICE", "unit_price", "PRICE"],
            "ext_amt": ["EXT_AMT", "ext_amt", "EXTENDED_AMT", "extended_amt", "EXT_AMOUNT", "EXT", "ext"],
            "bid_total": ["BID_TOTAL", "bid_total", "TOTAL", "total", "BID_AMOUNT"],
        }

        # Match columns (case-insensitive)
        columns_lower = {col.upper(): col for col in columns}

        for field, search_patterns in patterns.items():
            for pattern in search_patterns:
                pattern_upper = pattern.upper()
                if pattern_upper in columns_lower:
                    matched_col = columns_lower[pattern_upper]
                    if field == "proj_id":
                        schema.proj_id_col = matched_col
                    elif field == "let_dt":
                        schema.let_dt_col = matched_col
                    elif field == "county":
                        schema.county_col = matched_col
                    elif field == "item_no":
                        schema.item_no_col = matched_col
                    elif field == "item_desc":
                        schema.item_desc_col = matched_col
                    elif field == "unit":
                        schema.unit_col = matched_col
                    elif field == "qty":
                        schema.qty_col = matched_col
                    elif field == "eng_est":
                        schema.eng_est_col = matched_col
                    elif field == "bidder":
                        schema.bidder_col = matched_col
                    elif field == "bid_rank":
                        schema.bid_rank_col = matched_col
                    elif field == "unit_pr":
                        schema.unit_pr_col = matched_col
                    elif field == "ext_amt":
                        schema.ext_amt_col = matched_col
                    elif field == "bid_total":
                        schema.bid_total_col = matched_col
                    break

        # Log unmapped columns
        mapped = {
            schema.proj_id_col,
            schema.let_dt_col,
            schema.county_col,
            schema.item_no_col,
            schema.item_desc_col,
            schema.unit_col,
            schema.qty_col,
            schema.eng_est_col,
            schema.bidder_col,
            schema.bid_rank_col,
            schema.unit_pr_col,
            schema.ext_amt_col,
            schema.bid_total_col,
        }
        mapped.discard(None)

        unmapped = set(columns) - mapped
        if unmapped:
            warning = f"Unmapped columns: {', '.join(unmapped)}"
            schema.warnings.append(warning)
            logger.warning(warning)

        return schema

    def _parse_rows(self, df: pd.DataFrame) -> list[Project]:
        """Parse DataFrame rows into Project objects."""
        if not self.schema or not self.schema.is_complete():
            logger.error("Schema not fully mapped. Cannot parse rows.")
            return []

        projects_dict: dict[str, Project] = {}

        for idx, row in df.iterrows():
            try:
                # Keep proj_id as string to preserve leading zeros
                proj_id_val = row[self.schema.proj_id_col]
                if isinstance(proj_id_val, str):
                    proj_id = proj_id_val.strip()
                elif isinstance(proj_id_val, (int, float)):
                    proj_id = str(int(proj_id_val)).zfill(7)  # Preserve as 7-digit string
                else:
                    proj_id = str(proj_id_val).strip()

                # Initialize project if new
                if proj_id not in projects_dict:
                    projects_dict[proj_id] = Project(
                        proj_id=proj_id,
                        let_dt=self._parse_date(row.get(self.schema.let_dt_col)),
                        county=self._safe_string(row.get(self.schema.county_col)),
                    )

                project = projects_dict[proj_id]

                # Parse bid item
                item = BidItem(
                    item_no=str(row[self.schema.item_no_col]).strip(),
                    item_desc=str(row[self.schema.item_desc_col]).strip(),
                    unit=str(row[self.schema.unit_col]).strip(),
                    qty=self._safe_float(row.get(self.schema.qty_col), default=0.0),
                    eng_est_unit_pr=self._safe_float(row.get(self.schema.eng_est_col), default=0.0),
                    unit_price=self._safe_float(row.get(self.schema.unit_pr_col), default=0.0),
                    ext_amt=self._safe_float(row.get(self.schema.ext_amt_col), default=0.0),
                )

                # Parse bidder
                bidder_name = str(row[self.schema.bidder_col]).strip()
                bid_rank = self._safe_int(row.get(self.schema.bid_rank_col), default=999)
                bid_total = self._safe_float(row.get(self.schema.bid_total_col), default=0.0)

                bidder = Bidder(name=bidder_name, bid_rank=bid_rank, bid_total=bid_total)

                # Store in project
                if bidder_name not in project.bidders:
                    project.bidders[bidder_name] = bidder

                if bidder_name not in project.bidder_items:
                    project.bidder_items[bidder_name] = []

                project.items.append(item)
                project.bidder_items[bidder_name].append(item)

            except Exception as e:
                logger.warning(f"Failed to parse row {idx}: {e}")
                self.quality_report.inconsistencies.append(f"Row {idx}: {str(e)}")

        return list(projects_dict.values())

    @staticmethod
    def _safe_string(val: Any, default: str = "") -> Optional[str]:
        """Safely convert value to string."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        if isinstance(val, str):
            return val.strip() if val.strip() else default
        return str(val).strip()

    @staticmethod
    def _safe_float(val: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_int(val: Any, default: int = 0) -> int:
        """Safely convert value to int."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _parse_date(val: Any) -> Optional[datetime]:
        """Try to parse date from various formats."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        try:
            if isinstance(val, str):
                return pd.to_datetime(val).date()
            return pd.to_datetime(val).date()
        except Exception:
            return None
