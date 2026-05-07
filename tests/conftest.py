"""
Pytest configuration and global fixtures.
"""

import pytest
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s — %(name)s — %(message)s'
)


@pytest.fixture
def sample_csv_normal():
    """Fixture: Normal, well-formed CSV."""
    from tests.fixtures.sample_data import create_sample_csv_normal
    return create_sample_csv_normal()


@pytest.fixture
def sample_csv_missing_columns():
    """Fixture: CSV with missing columns."""
    from tests.fixtures.sample_data import create_sample_csv_missing_columns
    return create_sample_csv_missing_columns()


@pytest.fixture
def sample_csv_renamed_columns():
    """Fixture: CSV with renamed columns."""
    from tests.fixtures.sample_data import create_sample_csv_renamed_columns
    return create_sample_csv_renamed_columns()


@pytest.fixture
def sample_csv_empty_cells():
    """Fixture: CSV with empty/null cells."""
    from tests.fixtures.sample_data import create_sample_csv_empty_cells
    return create_sample_csv_empty_cells()


@pytest.fixture
def sample_csv_multiple_projects():
    """Fixture: CSV with multiple projects."""
    from tests.fixtures.sample_data import create_sample_csv_multiple_projects
    return create_sample_csv_multiple_projects()


@pytest.fixture
def sample_csv_inconsistent_types():
    """Fixture: CSV with inconsistent data types."""
    from tests.fixtures.sample_data import create_sample_csv_inconsistent_types
    return create_sample_csv_inconsistent_types()


@pytest.fixture
def empty_csv():
    """Fixture: Empty CSV (header only)."""
    from tests.fixtures.sample_data import create_empty_csv
    return create_empty_csv()


@pytest.fixture
def single_row_csv():
    """Fixture: CSV with single data row."""
    from tests.fixtures.sample_data import create_single_row_csv
    return create_single_row_csv()
