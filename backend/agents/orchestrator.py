"""
Orchestrator Agent

The root agent that coordinates the entire underwriting pipeline.
Chains all sub-agents sequentially, makes the final underwriting
decision (auto-approve / manual-review / auto-decline), and
triggers human-in-loop notifications when required.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime

from backend.agents.compliance_agent import run_compliance_agent
from backend.agents.feedback_agent import run_feedback_agent
from backend.agents.intake_agent import run_intake_agent
from backend.agents.pricing_agent import run_pricing_agent
from backend.agents.risk_agent import run_risk_agent
from backend.config import settings
from backend.models.schemas import (
    AgentStatus,
    ComplianceStatus,
    DecisionType,
    NotificationMessage,
    PipelineStatus,
    SubmissionInput,
    UnderwritingDecision,
)
from backend.services.agent_registry import AgentRegistry
from backend.services.memory_bank import MemoryBank
from backend.services.model_armor import ModelArmor
from backend.services.observability import ObservabilityService

logger = logging.getLogger(__name__)


def _determine_decision(
    risk_score: float,
    has_decline_triggers: bool,
    is_hazard_zone: bool,
    compliance_failed: bool,
    compliance_review_needed: bool,
) -> DecisionType:
    """
    Apply the underwriting decision rules.

    Decision Matrix:
    ┌────────────────────────────────────────┬────────────────────┐
    │ Condition                              │ Decision           │
    ├────────────────────────────────────────┼────────────────────┤
    │ Auto-decline triggers present          │ Auto-Declined      │
    │ Risk score > 80 (AUTO_DECLINE)         │ Auto-Declined      │
    │ Compliance checks FAILED               │ Auto-Declined      │
    │ Property in hazard zone                │ Manual Review      │
    │ Risk score 36-65 (MANUAL_REVIEW)       │ Manual Review      │
    │ Compliance has warnings                │ Manual Review      │
    │ Risk score ≤ 35 (AUTO_APPROVE)         │ Auto-Approved      │
    │ All checks pass                        │ Auto-Approved      │
    └────────────────────────────────────────┴────────────────────┘
    """
    # Auto-decline checks (highest priority)
    if has_decline_triggers:
        return DecisionType.AUTO_DECLINED
    if risk_score > settings.AUTO_DECLINE_THRESHOLD:
        return DecisionType.AUTO_DECLINED
    if compliance_failed:
        return DecisionType.AUTO_DECLINED

    # Manual review checks
    if is_hazard_zone:
        return DecisionType.MANUAL_REVIEW
    if risk_score > settings.AUTO_APPROVE_THRESHOLD:
        return DecisionType.MANUAL_REVIEW
    if compliance_review_needed:
        return DecisionType.MANUAL_REVIEW

    # Auto-approve
    return DecisionType.AUTO_APPROVED


def _create_notifications(
    decision: UnderwritingDecision,
) -> list[NotificationMessage]:
    """Generate human-in-loop notifications based on decision."""
    notifications = []

    if decision.decision == DecisionType.MANUAL_REVIEW:
        # Priority notification for hazard zone
        if decision.risk_profile and decision.risk_profile.is_hazard_zone:
            notifications.append(NotificationMessage(
                submission_id=decision.submission_id,
                severity="CRITICAL",
                title="🔴 Hazard Zone — Senior Underwriter Review Required",
                message=(
                    f"Submission {decision.submission_id} from "
                    f"{decision.submission_data.business_info.business_name} "
                    f"is located in hazard zone(s): "
                    f"{', '.join(decision.risk_profile.hazard_zones_detected)}. "
                    f"Risk score: {decision.risk_profile.composite_score}/100. "
                    f"Mandatory human review before binding."
                ),
                action_required=True,
            ))
            decision.review_priority = "Critical"
        else:
            notifications.append(NotificationMessage(
                submission_id=decision.submission_id,
                severity="WARNING",
                title="⚠ Manual Review Required",
                message=(
                    f"Submission {decision.submission_id} requires underwriter review. "
                    f"Risk score: {decision.risk_profile.composite_score if decision.risk_profile else 'N/A'}/100. "
                    f"Reasons: {'; '.join(decision.human_review_reasons[:3])}"
                ),
                action_required=True,
            ))
            decision.review_priority = "High"

    elif decision.decision == DecisionType.AUTO_DECLINED:
        notifications.append(NotificationMessage(
            submission_id=decision.submission_id,
            severity="INFO",
            title="📋 Submission Auto-Declined",
            message=(
                f"Submission {decision.submission_id} has been automatically declined. "
                f"Triggers: {'; '.join(decision.human_review_reasons[:3])}"
            ),
            action_required=False,
        ))

    elif decision.decision == DecisionType.AUTO_APPROVED:
        notifications.append(NotificationMessage(
            submission_id=decision.submission_id,
            severity="INFO",
            title="✅ Submission Auto-Approved",
            message=(
                f"Submission {decision.submission_id} from "
                f"{decision.submission_data.business_info.business_name if decision.submission_data else 'Unknown'} "
                f"has been auto-approved. Premium: "
                f"${decision.pricing.final_premium:,.2f}" if decision.pricing else "N/A"
            ),
            action_required=False,
        ))

    return notifications


def run_orchestrator(
    submission: SubmissionInput,
    pipeline_callback=None,
) -> UnderwritingDecision:
    """
    Execute the full underwriting pipeline.

    Orchestrates all 6 agents in sequence:
    1. Model Armor — input validation
    2. Intake Agent — document parsing
    3. Risk Profiling Agent — risk scoring
    4. Pricing Agent — premium calculation
    5. Compliance Agent — regulatory checks
    6. Feedback Agent — summary generation

    After all agents complete, applies the decision logic and
    generates human-in-loop notifications as needed.

    Args:
        submission: Raw submission input.
        pipeline_callback: Optional callback(agent_name, status) for UI updates.

    Returns:
        UnderwritingDecision with complete results.
    """
    start_time = time.time()
    registry = AgentRegistry()
    memory = MemoryBank()
    armor = ModelArmor()
    observability = ObservabilityService()

    trace_id = submission.submission_id
    observability.start_trace(trace_id)

    agents_executed = []

    def _update(agent_id: str, status: AgentStatus):
        registry.update_status(agent_id, status)
        if pipeline_callback:
            pipeline_callback(agent_id, status)

    # ── Step 0: Model Armor — Input Validation ────────────────────
    _update("orchestrator-agent", AgentStatus.RUNNING)
    armor_result = armor.scan_input(submission.raw_text, "submission")
    if armor_result.blocked:
        return UnderwritingDecision(
            submission_id=submission.submission_id,
            decision=DecisionType.AUTO_DECLINED,
            confidence_score=100.0,
            decision_rationale="Input blocked by Model Armor: " + "; ".join(armor_result.warnings),
            executive_summary="Submission rejected: security policy violation detected.",
            processing_time_seconds=round(time.time() - start_time, 2),
            agents_executed=["Model Armor"],
        )
    if armor_result.sanitized_text:
        submission.raw_text = armor_result.sanitized_text

    # ── Step 1: Intake Agent ──────────────────────────────────────
    _update("intake-agent", AgentStatus.RUNNING)
    try:
        with observability.trace_agent(trace_id, "Intake Agent") as span:
            parsed_data = run_intake_agent(submission)
            span.output_summary = f"Confidence: {parsed_data.extraction_confidence}%"
        _update("intake-agent", AgentStatus.COMPLETED)
        registry.record_execution("intake-agent", span.duration_ms, True)
        agents_executed.append("Intake Agent")
    except Exception as e:
        _update("intake-agent", AgentStatus.ERROR)
        registry.record_execution("intake-agent", 0, False)
        logger.error(f"Intake Agent failed: {e}")
        raise

    # ── Step 2: Risk Profiling Agent ──────────────────────────────
    _update("risk-agent", AgentStatus.RUNNING)
    try:
        with observability.trace_agent(trace_id, "Risk Profiling Agent") as span:
            risk_profile = run_risk_agent(parsed_data)
            span.output_summary = f"Score: {risk_profile.composite_score}, Tier: {risk_profile.risk_tier.value}"
        _update("risk-agent", AgentStatus.COMPLETED)
        registry.record_execution("risk-agent", span.duration_ms, True)
        agents_executed.append("Risk Profiling Agent")
    except Exception as e:
        _update("risk-agent", AgentStatus.ERROR)
        registry.record_execution("risk-agent", 0, False)
        logger.error(f"Risk Agent failed: {e}")
        raise

    # ── Step 3: Pricing Agent ─────────────────────────────────────
    _update("pricing-agent", AgentStatus.RUNNING)
    try:
        with observability.trace_agent(trace_id, "Pricing Agent") as span:
            pricing = run_pricing_agent(parsed_data, risk_profile)
            span.output_summary = f"Premium: ${pricing.final_premium:,.2f}"
        _update("pricing-agent", AgentStatus.COMPLETED)
        registry.record_execution("pricing-agent", span.duration_ms, True)
        agents_executed.append("Pricing Agent")
    except Exception as e:
        _update("pricing-agent", AgentStatus.ERROR)
        registry.record_execution("pricing-agent", 0, False)
        logger.error(f"Pricing Agent failed: {e}")
        raise

    # ── Step 4: Compliance Agent ──────────────────────────────────
    _update("compliance-agent", AgentStatus.RUNNING)
    try:
        with observability.trace_agent(trace_id, "Compliance Agent") as span:
            compliance = run_compliance_agent(parsed_data, risk_profile, pricing)
            span.output_summary = f"Status: {compliance.overall_status.value}, Score: {compliance.compliance_score}%"
        _update("compliance-agent", AgentStatus.COMPLETED)
        registry.record_execution("compliance-agent", span.duration_ms, True)
        agents_executed.append("Compliance Agent")
    except Exception as e:
        _update("compliance-agent", AgentStatus.ERROR)
        registry.record_execution("compliance-agent", 0, False)
        logger.error(f"Compliance Agent failed: {e}")
        raise

    # ── Step 5: Decision Logic ────────────────────────────────────
    decision_type = _determine_decision(
        risk_score=risk_profile.composite_score,
        has_decline_triggers=len(risk_profile.auto_decline_triggers) > 0,
        is_hazard_zone=risk_profile.is_hazard_zone,
        compliance_failed=compliance.overall_status == ComplianceStatus.FAIL,
        compliance_review_needed=compliance.requires_manual_review,
    )

    # Collect review reasons
    review_reasons = []
    if risk_profile.is_hazard_zone:
        review_reasons.append(f"Property in hazard zone: {', '.join(risk_profile.hazard_zones_detected)}")
    if risk_profile.auto_decline_triggers:
        review_reasons.extend(risk_profile.auto_decline_triggers)
    if compliance.review_reasons:
        review_reasons.extend(compliance.review_reasons)
    if risk_profile.composite_score > settings.AUTO_APPROVE_THRESHOLD:
        review_reasons.append(f"Risk score {risk_profile.composite_score} exceeds auto-approve threshold ({settings.AUTO_APPROVE_THRESHOLD})")

    # Confidence score
    if decision_type == DecisionType.AUTO_APPROVED:
        confidence = min(95.0, 100 - risk_profile.composite_score)
    elif decision_type == DecisionType.AUTO_DECLINED:
        confidence = min(95.0, risk_profile.composite_score)
    else:
        confidence = 50.0 + (risk_profile.composite_score / 4)

    # ── Step 6: Feedback Agent ────────────────────────────────────
    _update("feedback-agent", AgentStatus.RUNNING)
    try:
        with observability.trace_agent(trace_id, "Feedback Agent") as span:
            executive_summary, portfolio_insights = run_feedback_agent(
                parsed_data, risk_profile, pricing, compliance, decision_type.value
            )
            span.output_summary = f"Summary generated, {len(portfolio_insights)} insights"
        _update("feedback-agent", AgentStatus.COMPLETED)
        registry.record_execution("feedback-agent", span.duration_ms, True)
        agents_executed.append("Feedback Agent")
    except Exception as e:
        _update("feedback-agent", AgentStatus.ERROR)
        executive_summary = "Executive summary unavailable due to error."
        portfolio_insights = []
        agents_executed.append("Feedback Agent (Error)")

    _update("orchestrator-agent", AgentStatus.COMPLETED)

    # ── Build Final Decision ──────────────────────────────────────
    processing_time = round(time.time() - start_time, 2)

    decision = UnderwritingDecision(
        submission_id=submission.submission_id,
        decision=decision_type,
        confidence_score=round(confidence, 1),
        decision_rationale=f"{decision_type.value}: {'; '.join(review_reasons[:3])}" if review_reasons else f"{decision_type.value}: All criteria met",
        executive_summary=executive_summary,
        submission_data=parsed_data,
        risk_profile=risk_profile,
        pricing=pricing,
        compliance=compliance,
        requires_human_review=decision_type == DecisionType.MANUAL_REVIEW,
        review_priority="Critical" if risk_profile.is_hazard_zone else ("High" if decision_type == DecisionType.MANUAL_REVIEW else "Normal"),
        human_review_reasons=review_reasons,
        processing_time_seconds=processing_time,
        agents_executed=agents_executed,
        portfolio_insights=portfolio_insights,
    )

    # ── Notifications ─────────────────────────────────────────────
    notifications = _create_notifications(decision)
    decision.reviewer_notifications = [n.title for n in notifications]
    for n in notifications:
        memory.add_notification(n)

    # ── Persist to Memory Bank ────────────────────────────────────
    memory.store_decision(decision)

    # ── Model Armor — Output Validation ───────────────────────────
    armor.validate_output(
        {"final_premium": pricing.final_premium, "composite_score": risk_profile.composite_score},
        "orchestrator",
    )

    logger.info(
        f"Pipeline completed for {submission.submission_id}: "
        f"{decision_type.value} in {processing_time}s"
    )

    return decision
