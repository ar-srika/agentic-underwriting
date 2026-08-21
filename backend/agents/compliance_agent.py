"""
Compliance Agent

Validates the underwriting decision against regulatory rules
using the compliance_checker tool.
"""

from __future__ import annotations

import logging

from backend.models.schemas import (
    ComplianceReport,
    PricingRecommendation,
    RiskProfile,
    SubmissionData,
)
from backend.tools.compliance_checker import run_compliance_checks

logger = logging.getLogger(__name__)


def run_compliance_agent(
    data: SubmissionData,
    risk_profile: RiskProfile,
    pricing: PricingRecommendation,
) -> ComplianceReport:
    """
    Execute the Compliance Agent.

    Steps:
    1. Run compliance_checker tool (10 regulatory checks)
    2. Flag mandatory review triggers
    3. Add compliance notes

    Args:
        data: Structured submission data.
        risk_profile: Risk assessment results.
        pricing: Premium calculation results.

    Returns:
        ComplianceReport with per-rule results.
    """
    logger.info(f"Compliance Agent processing submission {data.submission_id}")

    # Step 1: Tool call — run all compliance checks
    report = run_compliance_checks(data, risk_profile, pricing)

    # Step 2: Additional compliance logging
    if report.requires_manual_review:
        logger.info(
            f"Compliance Agent flagged manual review for {data.submission_id}: "
            f"{report.review_reasons}"
        )

    if report.failed_count > 0:
        logger.warning(
            f"Compliance FAILURES for {data.submission_id}: "
            f"{[c.rule_name for c in report.checks if c.status.value == 'Fail']}"
        )

    logger.info(
        f"Compliance Agent completed — score: {report.compliance_score}%, "
        f"status: {report.overall_status.value}"
    )
    return report
