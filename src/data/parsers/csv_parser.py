"""CSV parser with adaptive schema inference."""

import logging
from typing import Optional

import pandas as pd

from src.data.models import Project, BidItem, Bidder, DataQualityReport, UnmappedField
from src.data.converters import ValueConverter

logger = logging.getLogger(__name__)


class CSVValidationError(Exception):
    """Raised when CSV is missing required columns."""
    pass


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
        self.unmapped_cols: dict[str, str] = {}  # col_name -> inferred_type
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


class CSVParser:
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
            missing = self._get_missing_fields()
            error_msg = (
                f"CSV is missing required columns: {', '.join(missing)}. "
                f"Please ensure your CSV has the following columns: "
                f"PROJECT_ID, ITEM_NO, ITEM_DESC, UNIT, QUANTITY, BIDDER, UNIT_PRICE"
            )
            logger.error(error_msg)
            raise CSVValidationError(error_msg)

        # Parse rows
        projects = self._parse_rows(df)

        if self.verbose:
            logger.info(f"Parsed {len(projects)} projects from {file_path}")

        return projects

    def _get_missing_fields(self) -> list[str]:
        """Return list of missing required fields."""
        if not self.schema:
            return ["PROJECT_ID", "ITEM_NO", "ITEM_DESC", "UNIT", "QUANTITY", "BIDDER", "UNIT_PRICE"]

        required = {
            "PROJECT_ID": self.schema.proj_id_col,
            "ITEM_NO": self.schema.item_no_col,
            "ITEM_DESC": self.schema.item_desc_col,
            "UNIT": self.schema.unit_col,
            "QUANTITY": self.schema.qty_col,
            "BIDDER": self.schema.bidder_col,
            "UNIT_PRICE": self.schema.unit_pr_col,
        }
        return [field for field, col in required.items() if col is None]

    def _infer_schema(self, df: pd.DataFrame) -> SchemaMapping:
        """Infer column mappings from CSV headers."""
        schema = SchemaMapping()
        columns = df.columns.tolist()

        # Define search patterns for each field (in priority order, all uppercase)
        # Supports: underscores (UNIT_PR), spaces (UNIT PR)
        # Case conversion happens automatically via .upper()
        patterns = {
            "proj_id": ["PROJ_ID", "PROJ ID", "PROJECT_ID", "PROJECT ID", "PROJ"],
            "let_dt": ["LET_DT", "LET DT", "LETTING_DATE", "LETTING DATE", "LET_DATE", "LET DATE", "DATE"],
            "county": ["CNTY", "COUNTY", "COUNTY_NAME", "COUNTY NAME", "CO"],
            "item_no": ["ITEM_NO", "ITEM NO", "ITEM_NUM", "ITEM NUM", "ITEM_ID", "ITEM ID"],
            "item_desc": ["ITEM_DESC", "ITEM DESC", "DESCRIPTION", "DESC"],
            "unit": ["UNIT", "UNITS", "UOM"],
            "qty": ["QTY", "QUANTITY", "QNTY"],
            "eng_est": ["ENG_EST_UNIT_PR", "ENG EST UNIT PR", "EST_UNIT_PRICE", "EST UNIT PRICE"],
            "bidder": ["BIDDER", "CONTRACTOR", "COMPANY", "COMPANY_NAME", "COMPANY NAME", "COMP", "SUPPLIER", "SUPPLIER_NAME", "SUPPLIER NAME", "SUP"],
            "bid_rank": ["BID_RANK", "BID RANK", "RANK", "BID_NO", "BID NO"],
            "unit_pr": ["UNIT_PR", "UNIT PR", "UNIT_PRICE", "UNIT PRICE", "PRICE"],
            "ext_amt": ["EXT_AMT", "EXT AMT", "EXTENDED_AMT", "EXTENDED AMT", "EXT_AMOUNT", "EXT AMOUNT", "EXT"],
            "bid_total": ["BID_TOTAL", "BID TOTAL", "TOTAL", "BID_AMOUNT", "BID AMOUNT"],
        }

        # Match columns (case-insensitive, keys are uppercase)
        columns_upper = {col.upper(): col for col in columns}

        for field, search_patterns in patterns.items():
            for pattern in search_patterns:
                pattern_upper = pattern.upper()
                if pattern_upper in columns_upper:
                    matched_col = columns_upper[pattern_upper]
                    setattr(schema, f"{field}_col", matched_col)
                    break

        # Log unmapped columns and detect their types
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
            # Detect type for each unmapped column
            for col in unmapped:
                # Sample first non-null value to infer type
                sample = None
                for val in df[col]:
                    if pd.notna(val):
                        sample = val
                        break

                if sample is not None:
                    inferred_type = ValueConverter.detect_type(sample)
                    schema.unmapped_cols[col] = inferred_type
                else:
                    schema.unmapped_cols[col] = "string"

            warning = f"Unmapped columns: {', '.join(unmapped)} (types: {schema.unmapped_cols})"
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
                        let_dt=ValueConverter.to_date(row.get(self.schema.let_dt_col)),
                        county=ValueConverter.to_string(row.get(self.schema.county_col)),
                    )

                project = projects_dict[proj_id]

                # Parse bid item
                item = BidItem(
                    item_no=str(row[self.schema.item_no_col]).strip(),
                    item_desc=str(row[self.schema.item_desc_col]).strip(),
                    unit=str(row[self.schema.unit_col]).strip(),
                    qty=ValueConverter.to_float(row.get(self.schema.qty_col), default=0.0),
                    eng_est_unit_pr=ValueConverter.to_float(row.get(self.schema.eng_est_col), default=0.0),
                    unit_price=ValueConverter.to_float(row.get(self.schema.unit_pr_col), default=0.0),
                    ext_amt=ValueConverter.to_float(row.get(self.schema.ext_amt_col), default=0.0),
                )

                # Add unmapped fields
                for col_name, inferred_type in self.schema.unmapped_cols.items():
                    raw_value = str(row.get(col_name, "")).strip()

                    # Parse numeric value if applicable
                    parsed_value = None
                    if inferred_type == "numeric":
                        parsed_value = ValueConverter.to_float(row.get(col_name))
                        if parsed_value == 0.0 and raw_value:
                            # Check if it really is 0 or conversion failed
                            try:
                                parsed_value = float(raw_value)
                            except ValueError:
                                parsed_value = None

                    item.unmapped_fields[col_name] = UnmappedField(
                        raw=raw_value,
                        inferred_type=inferred_type,
                        parsed_value=parsed_value,
                    )

                # Parse bidder (only store once, reuse for subsequent items)
                bidder_name = str(row[self.schema.bidder_col]).strip()

                if bidder_name not in project.bidders:
                    bid_rank = ValueConverter.to_int(row.get(self.schema.bid_rank_col), default=999)
                    bid_total = ValueConverter.to_float(row.get(self.schema.bid_total_col), default=0.0)
                    bidder = Bidder(name=bidder_name, bid_rank=bid_rank, bid_total=bid_total)
                    project.bidders[bidder_name] = bidder
                    project.bidder_items[bidder_name] = []

                # Store item for this bidder
                project.items.append(item)
                project.bidder_items[bidder_name].append(item)

            except Exception as e:
                logger.warning(f"Failed to parse row {idx}: {e}")
                self.quality_report.inconsistencies.append(f"Row {idx}: {str(e)}")

        return list(projects_dict.values())
