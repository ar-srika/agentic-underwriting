"""
Unit Tests for Document Parser & ACORD Extraction
"""

from backend.tools.document_parser import parse_submission_text
from backend.models.schemas import SubmissionType


def test_parse_low_risk_submission(low_risk_submission):
    data = parse_submission_text(low_risk_submission.raw_text, "TEST-001")
    assert "Apex Technology" in data.business_info.business_name
    assert "Technology" in data.business_info.business_type
    assert data.business_info.annual_revenue == 1500000.0
    assert data.business_info.employee_count == 10
    assert data.business_info.has_valid_license is True
    assert data.property_details.city == "Austin"
    assert data.property_details.state == "TX"
    assert data.property_details.zip_code == "78701"
    assert data.property_details.has_sprinkler_system is True
    assert data.claims_history.total_claims_3yr == 0


def test_parse_hazard_zone_submission(hazard_zone_submission):
    data = parse_submission_text(hazard_zone_submission.raw_text, "TEST-002")
    assert "Ocean Breeze" in data.business_info.business_name
    assert "Restaurant" in data.business_info.business_type
    assert data.property_details.city == "Miami"
    assert data.property_details.state == "FL"
    assert data.property_details.zip_code == "33139"
    assert data.claims_history.total_claims_3yr == 2


def test_parse_prohibited_business_submission(high_risk_submission):
    data = parse_submission_text(high_risk_submission.raw_text, "TEST-003")
    assert "Demolition" in data.business_info.business_name
    assert "Hazardous" in data.business_info.business_type
    assert data.business_info.has_valid_license is False
    assert data.claims_history.total_claims_3yr == 6
