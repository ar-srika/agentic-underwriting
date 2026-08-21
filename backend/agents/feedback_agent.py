"""
Feedback & Learning Agent

Generates executive summaries, portfolio insights, and
improvement recommendations using Gemini 3.5.
"""

from __future__ import annotations

import logging
from typing import List

from backend.config import settings
from backend.models.schemas import (
    ComplianceReport,
    PricingRecommendation,
    RiskProfile,
    SubmissionData,
)

logger = logging.getLogger(__name__)


def _generate_executive_summary(
    data: SubmissionData,
    risk: RiskProfile,
    pricing: PricingRecommendation,
    compliance: ComplianceReport,
    decision: str,
) -> str:
    """Generate an executive summary using Gemini."""
    if not settings.is_api_key_configured():
        return _build_default_summary(data, risk, pricing, compliance, decision)

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        prompt = f"""You are a Chief Underwriting Officer. Write a concise executive summary for this underwriting decision.

SUBMISSION:
- Business: {data.business_info.business_name} ({data.business_info.business_type})
- Location: {data.property_details.city}, {data.property_details.state}
- Property Value: ${data.property_details.property_value:,.0f}
- Annual Revenue: ${data.business_info.annual_revenue:,.0f}
- Employees: {data.business_info.employee_count}
- Years in Business: {data.business_info.years_in_business}

RISK ASSESSMENT:
- Composite Score: {risk.composite_score}/100 ({risk.risk_tier.value})
- Hazard Zones: {', '.join(risk.hazard_zones_detected) if risk.hazard_zones_detected else 'None'}
- Auto-Decline Triggers: {risk.auto_decline_triggers if risk.auto_decline_triggers else 'None'}

PRICING:
- Final Premium: ${pricing.final_premium:,.2f}
- Product: {pricing.product_recommendation}
- Premium Capped: {'Yes' if pricing.premium_capped else 'No'}

COMPLIANCE:
- Status: {compliance.overall_status.value}
- Score: {compliance.compliance_score}%
- Manual Review Required: {'Yes' if compliance.requires_manual_review else 'No'}

DECISION: {decision}

Write a 4-5 sentence executive summary suitable for a board report. Include the decision, key risk factors, pricing rationale, and any required actions. Be professional and decisive."""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.warning(f"Executive summary generation failed: {e}")
        return _build_default_summary(data, risk, pricing, compliance, decision)


def _build_default_summary(
    data: SubmissionData,
    risk: RiskProfile,
    pricing: PricingRecommendation,
    compliance: ComplianceReport,
    decision: str,
) -> str:
    """Build a structured executive summary without AI."""
    biz = data.business_info
    parts = [
        f"Submission from {biz.business_name or 'Unknown Business'} ({biz.business_type}) "
        f"has been assessed with a composite risk score of {risk.composite_score}/100 "
        f"({risk.risk_tier.value} Risk).",

        f"The recommended annual premium is ${pricing.final_premium:,.2f} under a "
        f"{pricing.product_recommendation}.",

        f"Compliance assessment scored {compliance.compliance_score}% with "
        f"{compliance.passed_count} checks passed, {compliance.warning_count} warnings, "
        f"and {compliance.failed_count} failures.",
    ]

    if decision == "Auto-Approved":
        parts.append(
            "The submission meets all underwriting standards and has been AUTO-APPROVED. "
            "No further action required."
        )
    elif decision == "Auto-Declined":
        parts.append(
            f"The submission has been AUTO-DECLINED due to: "
            f"{'; '.join(risk.auto_decline_triggers[:3])}."
        )
    else:
        reasons = compliance.review_reasons[:2] if compliance.review_reasons else ["Risk factors require review"]
        parts.append(
            f"MANUAL REVIEW REQUIRED: {'; '.join(reasons)}. "
            "A senior underwriter must review before binding."
        )

    return " ".join(parts)


def _generate_portfolio_insights(
    data: SubmissionData,
    risk: RiskProfile,
    pricing: PricingRecommendation,
) -> List[str]:
    """Generate portfolio-level insights."""
    insights = []

    # Pricing insight
    if pricing.premium_capped:
        insights.append(
            f"Premium for this submission was capped at $10,000. The uncapped premium "
            f"would be ${pricing.calculated_premium:,.2f}. Consider adjusting coverage limits "
            f"or deductibles to better reflect the risk."
        )

    # Risk concentration insight
    if risk.is_hazard_zone:
        insights.append(
            f"This submission adds exposure to hazard zone(s): "
            f"{', '.join(risk.hazard_zones_detected)}. Review portfolio concentration "
            f"in these zones to ensure adequate diversification."
        )

    # Business type insight
    bt = data.business_info.business_type.lower()
    if any(t in bt for t in ["restaurant", "construction", "manufacturing"]):
        insights.append(
            f"High-risk business type ({data.business_info.business_type}). "
            f"Monitor loss ratio for this segment closely."
        )

    # Claims trend
    if data.claims_history.total_claims_3yr > 2:
        insights.append(
            f"Elevated claims frequency ({data.claims_history.total_claims_3yr} in 3 years). "
            f"Consider loss-control consultation for similar accounts."
        )

    if not insights:
        insights.append(
            "This submission falls within standard risk parameters. No portfolio-level concerns."
        )

    return insights


def run_feedback_agent(
    data: SubmissionData,
    risk: RiskProfile,
    pricing: PricingRecommendation,
    compliance: ComplianceReport,
    decision: str,
) -> tuple[str, List[str]]:
    """
    Execute the Feedback & Learning Agent.

    Steps:
    1. Generate executive summary (AI-enhanced or fallback)
    2. Produce portfolio-level insights
    3. Create improvement recommendations

    Args:
        data: Submission data.
        risk: Risk profile.
        pricing: Pricing recommendation.
        compliance: Compliance report.
        decision: Final decision string.

    Returns:
        Tuple of (executive_summary, portfolio_insights).
    """
    logger.info(f"Feedback Agent processing submission {data.submission_id}")

    summary = _generate_executive_summary(data, risk, pricing, compliance, decision)
    insights = _generate_portfolio_insights(data, risk, pricing)

    logger.info("Feedback Agent completed")
    return summary, insights
