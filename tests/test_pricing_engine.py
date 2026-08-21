"""
Unit Tests for Actuarial Pricing Engine & $10,000 Hard Policy Cap
"""

from backend.tools.document_parser import parse_submission_text
from backend.tools.risk_calculator import calculate_risk
from backend.tools.pricing_engine import calculate_premium
from backend.models.schemas import SubmissionType


def test_pricing_cap_enforcement(hazard_zone_submission):
    data = parse_submission_text(hazard_zone_submission.raw_text, "TEST-002")
    risk = calculate_risk(data)
    pricing = calculate_premium(data, risk)
    
    # Premium must never exceed the $10,000 hard ceiling
    assert pricing.final_premium <= 10000.0
    assert pricing.final_premium >= 500.0
    assert pricing.product_recommendation != ""


def test_low_risk_pricing(low_risk_submission):
    data = parse_submission_text(low_risk_submission.raw_text, "TEST-001")
    risk = calculate_risk(data)
    pricing = calculate_premium(data, risk)
    
    assert pricing.final_premium <= 10000.0
    assert pricing.final_premium >= 500.0
    assert not pricing.premium_capped
    assert len(pricing.modifiers) == 8
