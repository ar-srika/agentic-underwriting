"""
Risk Profiling Agent

Analyzes parsed submission data against the risk calculator tool
and optionally uses Gemini for risk narrative generation.
Implements auto-approve / manual-review / auto-decline logic.
"""

from __future__ import annotations

import logging

from backend.config import settings
from backend.models.schemas import RiskProfile, SubmissionData
from backend.tools.risk_calculator import calculate_risk

logger = logging.getLogger(__name__)


def _generate_risk_narrative(data: SubmissionData, profile: RiskProfile) -> str:
    """Use Gemini to generate a human-readable risk narrative."""
    if not settings.is_api_key_configured():
        return profile.risk_summary

    try:
        risk_factors_text = "\n".join(f"- {f}" for f in profile.risk_factors) if profile.risk_factors else "None identified"
        mitigating_text = "\n".join(f"- {f}" for f in profile.mitigating_factors) if profile.mitigating_factors else "None identified"

        prompt = f"""You are a senior insurance underwriter. Write a concise 3-4 sentence risk assessment narrative for this submission.

Business: {data.business_info.business_name} ({data.business_info.business_type})
Location: {data.property_details.city}, {data.property_details.state}
Property Value: ${data.property_details.property_value:,.0f}
Composite Risk Score: {profile.composite_score}/100 ({profile.risk_tier.value})
Hazard Zones: {', '.join(profile.hazard_zones_detected) if profile.hazard_zones_detected else 'None'}

Key Risk Factors:
{risk_factors_text}

Mitigating Factors:
{mitigating_text}

Write a professional underwriting risk narrative. Be specific about the key concerns and positives. Keep it under 100 words."""

        result = settings.call_gemini(prompt).strip()
        return result or profile.risk_summary

    except Exception as e:
        logger.warning(f"Risk narrative generation failed: {e}")
        return profile.risk_summary


def run_risk_agent(data: SubmissionData) -> RiskProfile:
    """
    Execute the Risk Profiling Agent.

    Steps:
    1. Run risk_calculator tool for quantitative scoring
    2. Validate results against thresholds
    3. Generate AI-enhanced risk narrative with Gemini
    4. Flag hazard zones and auto-decline triggers

    Args:
        data: Structured submission data from Intake Agent.

    Returns:
        RiskProfile with composite score, tier, and decision signals.
    """
    logger.info(f"Risk Agent processing submission {data.submission_id}")

    # Step 1: Tool call — quantitative risk scoring
    profile = calculate_risk(data)

    # Step 2: Validate and flag
    if profile.auto_decline_triggers:
        logger.warning(
            f"Auto-decline triggers for {data.submission_id}: "
            f"{profile.auto_decline_triggers}"
        )

    if profile.is_hazard_zone:
        logger.info(
            f"Hazard zone detected for {data.submission_id}: "
            f"{profile.hazard_zones_detected}"
        )

    # Step 3: AI-enhanced narrative
    profile.risk_summary = _generate_risk_narrative(data, profile)

    logger.info(
        f"Risk Agent completed — score: {profile.composite_score}, "
        f"tier: {profile.risk_tier.value}"
    )
    return profile
