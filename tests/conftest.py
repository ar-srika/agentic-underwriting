"""
Pytest Test Fixtures and Configurations
"""

import pytest
from backend.models.schemas import SubmissionInput, SubmissionType

SAMPLE_LOW_RISK_TEXT = """
Business Name: Apex Technology Solutions LLC
Business Type: Technology Consulting
Annual Revenue: $1,500,000
Employees: 10
Years in Business: 7
Property Address: 100 Innovation Way, Austin, TX 78701
Property Value: $400,000
Building Age: 4 years
Construction Type: Fire-resistant concrete
Sprinkler System: Yes
Fire Alarm: Yes
Security System: Yes
Claims in past 3 years: 0
Coverage Types: General Liability, Property, Professional Liability
Coverage Limit: $1,000,000
Deductible: $1,000
"""

SAMPLE_HAZARD_ZONE_TEXT = """
Business Name: Ocean Breeze Coastal Cafe
Business Type: Restaurant
Annual Revenue: $900,000
Employees: 22
Years in Business: 3
Property Address: 200 Ocean Drive, Miami, FL 33139
Property Value: $750,000
Building Age: 30 years
Construction Type: Wood frame
Sprinkler System: Yes
Fire Alarm: Yes
Security System: No
Roof Condition: Fair
Claims in past 3 years: 2
Largest Claim: $35,000
Coverage Types: General Liability, Property, Business Interruption
Coverage Limit: $1,000,000
Deductible: $2,500
"""

SAMPLE_HIGH_RISK_TEXT = """
Business Name: Heavy Demolition & Waste Corp
Business Type: Hazardous waste disposal
Annual Revenue: $4,000,000
Employees: 80
Years in Business: 1
Property Address: 500 Scrap Yard Rd, Los Angeles, CA 90001
Property Value: $1,200,000
Building Age: 60 years
Construction Type: Wood frame
Sprinkler System: No
Fire Alarm: No
Security System: No
Roof Condition: Poor
Claims in past 3 years: 6
Largest Claim: $350,000
Previous Policy Cancelled: Yes
Cancellation Reason: Fraud and non-payment
No valid license: True
Coverage Types: General Liability, Property, Workers Compensation
Coverage Limit: $2,000,000
Deductible: $5,000
"""


@pytest.fixture
def low_risk_submission():
    return SubmissionInput(
        raw_text=SAMPLE_LOW_RISK_TEXT,
        submission_type=SubmissionType.TEXT,
    )


@pytest.fixture
def hazard_zone_submission():
    return SubmissionInput(
        raw_text=SAMPLE_HAZARD_ZONE_TEXT,
        submission_type=SubmissionType.TEXT,
    )


@pytest.fixture
def high_risk_submission():
    return SubmissionInput(
        raw_text=SAMPLE_HIGH_RISK_TEXT,
        submission_type=SubmissionType.TEXT,
    )
