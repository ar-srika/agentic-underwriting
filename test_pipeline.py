"""
Test Script for Underwriting Pipeline

Verifies end-to-end execution of:
1. Low-risk submission -> Auto-Approved ($10K cap respected)
2. Hazard zone submission -> Manual Review Required + Human-in-the-loop Notification
3. High-risk submission -> Auto-Declined with violation triggers
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.agents.orchestrator import run_orchestrator
from backend.models.schemas import SubmissionInput, SubmissionType, DecisionType
from backend.services.memory_bank import MemoryBank

def test_pipeline():
    print("==================================================")
    print("RUNNING MULTI-AGENT UNDERWRITING PIPELINE TESTS")
    print("==================================================")
    
    memory = MemoryBank()

    # Test 1: Low Risk (Auto-Approve)
    print("\n--- TEST 1: Low Risk Small Business Submission ---")
    sub1 = SubmissionInput(
        raw_text="""Business Name: Apex Technology Solutions LLC
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
Deductible: $1,000""",
        submission_type=SubmissionType.TEXT
    )
    res1 = run_orchestrator(sub1)
    print(f"Decision: {res1.decision.value}")
    print(f"Risk Score: {res1.risk_profile.composite_score}/100 ({res1.risk_profile.risk_tier.value})")
    print(f"Final Premium: ${res1.pricing.final_premium:,.2f} (Capped: {res1.pricing.premium_capped})")
    print(f"Compliance: {res1.compliance.overall_status.value} ({res1.compliance.compliance_score}%)")
    assert res1.decision == DecisionType.AUTO_APPROVED, f"Expected Auto-Approved, got {res1.decision.value}"
    assert res1.pricing.final_premium <= 10000.0, f"Premium exceeds $10k cap: {res1.pricing.final_premium}"
    print("[PASS] TEST 1 PASSED: Successfully Auto-Approved")

    # Test 2: Hazard Zone (Manual Review Required)
    print("\n--- TEST 2: Hazard Zone (Miami Flood/Hurricane) ---")
    sub2 = SubmissionInput(
        raw_text="""Business Name: Ocean Breeze Coastal Cafe
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
Deductible: $2,500""",
        submission_type=SubmissionType.TEXT
    )
    res2 = run_orchestrator(sub2)
    print(f"Decision: {res2.decision.value}")
    print(f"Hazard Zones Detected: {res2.risk_profile.hazard_zones_detected}")
    print(f"Human Review Required: {res2.requires_human_review}")
    print(f"Review Priority: {res2.review_priority}")
    print(f"Final Premium: ${res2.pricing.final_premium:,.2f} (Capped: {res2.pricing.premium_capped})")
    assert res2.decision == DecisionType.MANUAL_REVIEW, f"Expected Manual Review, got {res2.decision.value}"
    assert res2.requires_human_review is True
    assert len(res2.risk_profile.hazard_zones_detected) > 0
    print("[PASS] TEST 2 PASSED: Successfully Routed to Manual Review with Hazard Notifications")

    # Test 3: High Risk (Auto-Decline)
    print("\n--- TEST 3: Prohibited / Extreme Risk Business ---")
    sub3 = SubmissionInput(
        raw_text="""Business Name: Heavy Demolition & Waste Corp
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
Deductible: $5,000""",
        submission_type=SubmissionType.TEXT
    )
    res3 = run_orchestrator(sub3)
    print(f"Decision: {res3.decision.value}")
    print(f"Auto-Decline Triggers: {res3.risk_profile.auto_decline_triggers}")
    print(f"Compliance Status: {res3.compliance.overall_status.value}")
    assert res3.decision == DecisionType.AUTO_DECLINED, f"Expected Auto-Declined, got {res3.decision.value}"
    print("[PASS] TEST 3 PASSED: Successfully Auto-Declined with policy triggers")

    # Test 4: Verify Memory Bank Notifications
    print("\n--- TEST 4: Human-in-the-Loop Notification Center ---")
    notifications = memory.get_notifications()
    print(f"Total Notifications queued: {len(notifications)}")
    for n in notifications:
        print(f"  - [{n.severity}] {n.title.encode('ascii', 'replace').decode('ascii')}")
    assert len(notifications) >= 3, "Expected notifications for all runs"
    print("[PASS] TEST 4 PASSED: Notification center correctly queued alerts")

    print("\n==================================================")
    print("ALL TESTS PASSED! Enterprise Underwriting System is 100% Operational.")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
