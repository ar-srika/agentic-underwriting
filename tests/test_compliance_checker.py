"""
Unit Tests for 10-Point Regulatory Compliance & Fair Lending Engine
"""

from backend.tools.document_parser import parse_submission_text
from backend.tools.risk_calculator import calculate_risk
from backend.tools.pricing_engine import calculate_premium
from backend.tools.compliance_checker import run_compliance_checks
from backend.models.schemas import ComplianceStatus, SubmissionType


def test_compliance_pass_low_risk(low_risk_submission):
    data = parse_submission_text(low_risk_submission.raw_text, "TEST-001")
    risk = calculate_risk(data)
    pricing = calculate_premium(data, risk)
    report = run_compliance_checks(data, risk, pricing)

    assert report.overall_status == ComplianceStatus.PASS
    assert report.failed_count == 0
    assert report.passed_count == 10
    assert not report.requires_manual_review


def test_compliance_warning_hazard_zone(hazard_zone_submission):
    data = parse_submission_text(hazard_zone_submission.raw_text, "TEST-002")
    risk = calculate_risk(data)
    pricing = calculate_premium(data, risk)
    report = run_compliance_checks(data, risk, pricing)

    # Hazard disclosure warning
    assert report.warning_count >= 1
    assert report.overall_status in [ComplianceStatus.WARNING, ComplianceStatus.PASS]


def test_compliance_fail_prohibited_business(high_risk_submission):
    data = parse_submission_text(high_risk_submission.raw_text, "TEST-003")
    risk = calculate_risk(data)
    pricing = calculate_premium(data, risk)
    report = run_compliance_checks(data, risk, pricing)

    assert report.overall_status == ComplianceStatus.FAIL
    assert report.failed_count >= 1
    assert any("prohibited" in c.details.lower() or "prohibited" in c.rule_name.lower() for c in report.checks if c.status == ComplianceStatus.FAIL)
