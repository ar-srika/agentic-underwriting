"""
Integration Tests for Orchestrator & End-to-End Multi-Agent Pipeline
"""

from backend.agents.orchestrator import run_orchestrator
from backend.models.schemas import DecisionType, ComplianceStatus


def test_e2e_low_risk_auto_approved(low_risk_submission):
    decision = run_orchestrator(low_risk_submission)
    assert decision.decision == DecisionType.AUTO_APPROVED
    assert decision.risk_profile.composite_score <= 35.0
    assert decision.pricing.final_premium <= 10000.0
    assert decision.compliance.overall_status == ComplianceStatus.PASS
    assert not decision.requires_human_review
    assert len(decision.agents_executed) >= 5


def test_e2e_hazard_zone_manual_review(hazard_zone_submission):
    decision = run_orchestrator(hazard_zone_submission)
    assert decision.decision == DecisionType.MANUAL_REVIEW
    assert decision.requires_human_review is True
    assert decision.review_priority == "Critical"
    assert len(decision.human_review_reasons) > 0
    assert len(decision.agents_executed) >= 5


def test_e2e_prohibited_business_auto_declined(high_risk_submission):
    decision = run_orchestrator(high_risk_submission)
    assert decision.decision == DecisionType.AUTO_DECLINED
    assert len(decision.risk_profile.auto_decline_triggers) > 0
    assert decision.compliance.overall_status == ComplianceStatus.FAIL
    assert len(decision.agents_executed) >= 5
