"""
Data quality validators for construction bid data.

Validates without failing: flags issues as warnings, doesn't throw errors.
"""

import logging
from typing import Optional

from src.data.models import Project, BidItem, DataQualityReport

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates construction data for quality issues."""

    @staticmethod
    def validate_project(project: Project) -> DataQualityReport:
        """
        Validate a Project object and return quality report.

        Checks:
        - Project ID is not empty
        - At least one bidder exists
        - At least one item exists
        - Items have reasonable values
        - Bidders have consistent data

        Returns:
            DataQualityReport with warnings and inconsistencies
        """
        report = DataQualityReport()

        # Check project basics
        if not project.proj_id or not project.proj_id.strip():
            report.warnings.append("Project ID is empty")

        if not project.bidders:
            report.warnings.append(f"Project {project.proj_id}: No bidders found")

        if not project.items:
            report.warnings.append(f"Project {project.proj_id}: No items found")

        # Validate items
        for item in project.items:
            item_report = DataValidator.validate_item(item)
            report.inconsistencies.extend(item_report.inconsistencies)
            report.warnings.extend(item_report.warnings)

        # Validate bidders
        for bidder_name, bidder in project.bidders.items():
            bidder_report = DataValidator.validate_bidder(bidder)
            report.inconsistencies.extend(bidder_report.inconsistencies)
            report.warnings.extend(bidder_report.warnings)

        # Check bidder-item consistency
        for bidder_name, items in project.bidder_items.items():
            if bidder_name not in project.bidders:
                report.inconsistencies.append(
                    f"Bidder '{bidder_name}' has items but not in bidders dict"
                )

        if report.has_issues():
            logger.warning(
                f"Project {project.proj_id} has quality issues: "
                f"{len(report.warnings)} warnings, {len(report.inconsistencies)} inconsistencies"
            )

        return report

    @staticmethod
    def validate_item(item: BidItem) -> DataQualityReport:
        """Validate a single BidItem."""
        report = DataQualityReport()

        # Check required fields
        if not item.item_no or not item.item_no.strip():
            report.warnings.append("Item number is empty")

        if not item.item_desc or not item.item_desc.strip():
            report.warnings.append("Item description is empty")

        if not item.unit or not item.unit.strip():
            report.warnings.append(f"Item {item.item_no}: Unit is empty")

        # Check numeric constraints
        if item.qty < 0:
            report.inconsistencies.append(f"Item {item.item_no}: Quantity is negative ({item.qty})")

        if item.unit_price < 0:
            report.inconsistencies.append(
                f"Item {item.item_no}: Unit price is negative ({item.unit_price})"
            )

        if item.ext_amt < 0:
            report.inconsistencies.append(
                f"Item {item.item_no}: Extended amount is negative ({item.ext_amt})"
            )

        # Check calculation consistency
        if item.qty > 0 and item.unit_price > 0:
            expected = item.qty * item.unit_price
            if abs(item.ext_amt - expected) > 0.01:  # Allow small rounding errors
                report.inconsistencies.append(
                    f"Item {item.item_no}: ext_amt ({item.ext_amt}) != qty ({item.qty}) × unit_price ({item.unit_price}) = {expected}"
                )

        # Check if item is reasonable
        if not item.is_reasonable():
            report.warnings.append(f"Item {item.item_no}: Values seem unreasonable")

        return report

    @staticmethod
    def validate_bidder(bidder) -> DataQualityReport:
        """Validate a single Bidder."""
        report = DataQualityReport()

        if not bidder.name or not bidder.name.strip():
            report.warnings.append("Bidder name is empty")

        if bidder.bid_rank < 1:
            report.inconsistencies.append(f"Bidder {bidder.name}: Bid rank < 1 ({bidder.bid_rank})")

        if bidder.bid_total < 0:
            report.inconsistencies.append(
                f"Bidder {bidder.name}: Bid total is negative ({bidder.bid_total})"
            )

        return report

    @staticmethod
    def validate_projects(projects: list[Project]) -> dict[str, DataQualityReport]:
        """
        Validate a list of projects.

        Returns:
            Dict mapping project_id to DataQualityReport
        """
        reports = {}
        for project in projects:
            reports[project.proj_id] = DataValidator.validate_project(project)

        total_issues = sum(1 for r in reports.values() if r.has_issues())
        logger.info(f"Validated {len(projects)} projects: {total_issues} with issues")

        return reports


def check_data_quality(projects: list[Project]) -> bool:
    """
    Quick check: Do all projects pass basic validation?

    Returns:
        True if no critical inconsistencies found, False otherwise
    """
    reports = DataValidator.validate_projects(projects)
    for project_id, report in reports.items():
        if report.inconsistencies:
            logger.error(f"Project {project_id} has critical inconsistencies")
            return False
    return True
