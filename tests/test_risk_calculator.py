"""
Unit Tests for 6-Dimensional Risk Calculator & Hazard Zone Lookup
"""

from backend.tools.document_parser import parse_submission_text
from backend.tools.risk_calculator import calculate_risk
from backend.models.schemas import RiskTier, SubmissionType


def test_low_risk_calculation(low_risk_submission):
    data = parse_submission_text(low_risk_submission.raw_text, "TEST-001")
    risk = calculate_risk(data)
    assert risk.composite_score <= 35.0
    assert risk.risk_tier == RiskTier.LOW
    assert not risk.is_hazard_zone
    assert len(risk.auto_decline_triggers) == 0


def test_hazard_zone_detection(hazard_zone_submission):
    data = parse_submission_text(hazard_zone_submission.raw_text, "TEST-002")
    risk = calculate_risk(data)
    assert risk.is_hazard_zone is True
    assert any("Miami" in hz or "Flood" in hz for hz in risk.hazard_zones_detected)


def test_high_risk_decline_triggers(high_risk_submission):
    data = parse_submission_text(high_risk_submission.raw_text, "TEST-003")
    risk = calculate_risk(data)
    assert len(risk.auto_decline_triggers) > 0
    assert any("Prohibited business" in t for t in risk.auto_decline_triggers)
