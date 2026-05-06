"""
Test fixtures and sample data for construction bid data tests.

Creates sample CSVs with various edge cases and variations to test robustness.
"""

import tempfile
from pathlib import Path
import pandas as pd


def create_sample_csv_normal() -> Path:
    """Create a normal, well-formed sample CSV."""
    data = {
        "PROJ_ID": ["0676350", "0676350", "0676350"],
        "LET_DT": ["2026-03-10", "2026-03-10", "2026-03-10"],
        "CNTY": ["Barnwell", "Barnwell", "Barnwell"],
        "ITEM_NO": ["1031000", "1032010", "2033000"],
        "ITEM_DESC": ["MOBILIZATION", "BONDS AND INSURANCE", "BORROW EXCAVATION"],
        "UNIT": ["LS", "LS", "CY"],
        "QTY": [1.0, 1.0, 248.0],
        "ENG_EST_UNIT_PR": [0.0, 0.0, 0.0],
        "BIDDER": ["ABC CONSTRUCTION", "ABC CONSTRUCTION", "ABC CONSTRUCTION"],
        "BID_RANK": [1, 1, 1],
        "UNIT_PR": [16500.0, 800.0, 107.15],
        "EXT_AMT": [16500.0, 800.0, 26573.2],
        "BID_TOTAL": [337288.86, 337288.86, 337288.86],
    }
    return _write_csv(pd.DataFrame(data))


def create_sample_csv_missing_columns() -> Path:
    """Create CSV with missing columns (e.g., no ENG_EST_UNIT_PR)."""
    data = {
        "PROJ_ID": ["0676350", "0676350"],
        "LET_DT": ["2026-03-10", "2026-03-10"],
        "CNTY": ["Barnwell", "Barnwell"],
        "ITEM_NO": ["1031000", "1032010"],
        "ITEM_DESC": ["MOBILIZATION", "BONDS AND INSURANCE"],
        "UNIT": ["LS", "LS"],
        "QTY": [1.0, 1.0],
        # Missing: ENG_EST_UNIT_PR
        "BIDDER": ["ABC CONSTRUCTION", "ABC CONSTRUCTION"],
        "BID_RANK": [1, 1],
        "UNIT_PR": [16500.0, 800.0],
        "EXT_AMT": [16500.0, 800.0],
        "BID_TOTAL": [337288.86, 337288.86],
    }
    return _write_csv(pd.DataFrame(data))


def create_sample_csv_renamed_columns() -> Path:
    """Create CSV with renamed columns (different naming convention)."""
    data = {
        "proj_id": ["0676350", "0676350"],  # lowercase instead of PROJ_ID
        "let_dt": ["2026-03-10", "2026-03-10"],
        "cnty": ["Barnwell", "Barnwell"],
        "item_no": ["1031000", "1032010"],
        "description": ["MOBILIZATION", "BONDS AND INSURANCE"],  # ITEM_DESC → description
        "unit": ["LS", "LS"],
        "qty": [1.0, 1.0],
        "eng_est_unit_pr": [0.0, 0.0],
        "contractor": ["ABC CONSTRUCTION", "ABC CONSTRUCTION"],  # BIDDER → contractor
        "rank": [1, 1],  # BID_RANK → rank
        "price": [16500.0, 800.0],  # UNIT_PR → price
        "ext": [16500.0, 800.0],  # EXT_AMT → ext
        "total": [337288.86, 337288.86],  # BID_TOTAL → total
    }
    return _write_csv(pd.DataFrame(data))


def create_sample_csv_empty_cells() -> Path:
    """Create CSV with empty/null values."""
    data = {
        "PROJ_ID": ["0676350", "0676350", None],
        "LET_DT": ["2026-03-10", None, "2026-03-10"],
        "CNTY": ["Barnwell", "Barnwell", "Barnwell"],
        "ITEM_NO": ["1031000", "1032010", "2033000"],
        "ITEM_DESC": ["MOBILIZATION", "", "BORROW EXCAVATION"],
        "UNIT": ["LS", "LS", None],
        "QTY": [1.0, 1.0, 248.0],
        "ENG_EST_UNIT_PR": [0.0, None, 0.0],
        "BIDDER": ["ABC CONSTRUCTION", "ABC CONSTRUCTION", "ABC CONSTRUCTION"],
        "BID_RANK": [1, 1, None],
        "UNIT_PR": [16500.0, 800.0, 107.15],
        "EXT_AMT": [16500.0, 800.0, 26573.2],
        "BID_TOTAL": [337288.86, 337288.86, 337288.86],
    }
    return _write_csv(pd.DataFrame(data))


def create_sample_csv_multiple_projects() -> Path:
    """Create CSV with multiple projects."""
    data = {
        "PROJ_ID": ["0676350", "0676350", "5275280", "5275280"],
        "LET_DT": ["2026-03-10", "2026-03-10", "2026-01-13", "2026-01-13"],
        "CNTY": ["Barnwell", "Barnwell", "District 2", "District 2"],
        "ITEM_NO": ["1031000", "1032010", "1031000", "1032010"],
        "ITEM_DESC": ["MOBILIZATION", "BONDS AND INSURANCE", "MOBILIZATION", "BONDS AND INSURANCE"],
        "UNIT": ["LS", "LS", "LS", "LS"],
        "QTY": [1.0, 1.0, 1.0, 1.0],
        "ENG_EST_UNIT_PR": [0.0, 0.0, 0.0, 0.0],
        "BIDDER": ["ABC CONSTRUCTION", "ABC CONSTRUCTION", "XYZ CORP", "XYZ CORP"],
        "BID_RANK": [1, 1, 1, 1],
        "UNIT_PR": [16500.0, 800.0, 6500.0, 7500.0],
        "EXT_AMT": [16500.0, 800.0, 6500.0, 7500.0],
        "BID_TOTAL": [337288.86, 337288.86, 2558797.8, 2558797.8],
    }
    return _write_csv(pd.DataFrame(data))


def create_sample_csv_inconsistent_types() -> Path:
    """Create CSV with inconsistent data types (quantities as strings, etc)."""
    data = {
        "PROJ_ID": ["0676350", "0676350"],
        "LET_DT": ["2026-03-10", "2026-03-10"],
        "CNTY": ["Barnwell", "Barnwell"],
        "ITEM_NO": ["1031000", "1032010"],
        "ITEM_DESC": ["MOBILIZATION", "BONDS AND INSURANCE"],
        "UNIT": ["LS", "LS"],
        "QTY": ["1.0", "248 units"],  # String instead of numeric
        "ENG_EST_UNIT_PR": [0.0, 0.0],
        "BIDDER": ["ABC CONSTRUCTION", "ABC CONSTRUCTION"],
        "BID_RANK": [1, "2"],  # String instead of int
        "UNIT_PR": [16500.0, "800"],  # String instead of float
        "EXT_AMT": [16500.0, 800.0],
        "BID_TOTAL": [337288.86, 337288.86],
    }
    return _write_csv(pd.DataFrame(data))


def create_empty_csv() -> Path:
    """Create an empty CSV (header only)."""
    df = pd.DataFrame(columns=[
        "PROJ_ID", "LET_DT", "CNTY", "ITEM_NO", "ITEM_DESC",
        "UNIT", "QTY", "ENG_EST_UNIT_PR", "BIDDER", "BID_RANK",
        "UNIT_PR", "EXT_AMT", "BID_TOTAL"
    ])
    return _write_csv(df)


def create_single_row_csv() -> Path:
    """Create CSV with just one row of data."""
    data = {
        "PROJ_ID": ["0676350"],
        "LET_DT": ["2026-03-10"],
        "CNTY": ["Barnwell"],
        "ITEM_NO": ["1031000"],
        "ITEM_DESC": ["MOBILIZATION"],
        "UNIT": ["LS"],
        "QTY": [1.0],
        "ENG_EST_UNIT_PR": [0.0],
        "BIDDER": ["ABC CONSTRUCTION"],
        "BID_RANK": [1],
        "UNIT_PR": [16500.0],
        "EXT_AMT": [16500.0],
        "BID_TOTAL": [337288.86],
    }
    return _write_csv(pd.DataFrame(data))


def _write_csv(df: pd.DataFrame) -> Path:
    """Helper: Write DataFrame to temporary CSV file."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_path = Path(temp_file.name)
    df.to_csv(temp_path, index=False)
    temp_file.close()
    return temp_path
