"""
Pricing & Product Agent

Calculates insurance premium using the pricing_engine tool and
optionally uses Gemini for product recommendation rationale.
"""

from __future__ import annotations

import logging

from backend.config import settings
from backend.models.schemas import PricingRecommendation, RiskProfile, SubmissionData
from backend.tools.pricing_engine import calculate_premium

logger = logging.getLogger(__name__)


def _generate_pricing_rationale(
    data: SubmissionData,
    risk_profile: RiskProfile,
    pricing: PricingRecommendation,
) -> PricingRecommendation:
    """Use Gemini to generate a pricing rationale narrative."""
    if not settings.is_api_key_configured():
        return pricing

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        modifiers_text = "\n".join(
            f"- {m.name}: {m.factor} ({m.reason})" for m in pricing.modifiers
        )

        prompt = f"""You are an insurance pricing actuary. Write a brief 2-3 sentence rationale for this premium calculation.

Business: {data.business_info.business_name} ({data.business_info.business_type})
Risk Score: {risk_profile.composite_score}/100 ({risk_profile.risk_tier.value})
Base Premium: ${pricing.base_premium:,.2f}
Final Premium: ${pricing.final_premium:,.2f}
{'Premium was CAPPED at $10,000' if pricing.premium_capped else ''}
Product: {pricing.product_recommendation}

Key Modifiers:
{modifiers_text}

Write a professional pricing rationale. Be concise and specific. Under 60 words."""

        response = model.generate_content(prompt)
        pricing.pricing_notes.append(f"AI Rationale: {response.text.strip()}")

    except Exception as e:
        logger.warning(f"Pricing rationale generation failed: {e}")
        pricing.pricing_notes.append(f"⚠ AI rationale unavailable: {str(e)[:100]}")

    return pricing


def run_pricing_agent(
    data: SubmissionData,
    risk_profile: RiskProfile,
) -> PricingRecommendation:
    """
    Execute the Pricing & Product Agent.

    Steps:
    1. Run pricing_engine tool for premium calculation
    2. Validate premium against $10K cap
    3. Generate AI-enhanced pricing rationale with Gemini

    Args:
        data: Structured submission data from Intake Agent.
        risk_profile: Risk assessment from Risk Agent.

    Returns:
        PricingRecommendation with full premium breakdown.
    """
    logger.info(f"Pricing Agent processing submission {data.submission_id}")

    # Step 1: Tool call — premium calculation
    pricing = calculate_premium(data, risk_profile)

    # Step 2: Double-check cap enforcement
    if pricing.final_premium > settings.MAX_PREMIUM:
        pricing.final_premium = settings.MAX_PREMIUM
        pricing.premium_capped = True
        pricing.pricing_notes.append(
            f"⚠ Premium re-capped to ${settings.MAX_PREMIUM:,.2f} by agent validation"
        )

    # Step 3: AI-enhanced rationale
    pricing = _generate_pricing_rationale(data, risk_profile, pricing)

    logger.info(
        f"Pricing Agent completed — premium: ${pricing.final_premium:,.2f}, "
        f"product: {pricing.product_recommendation}"
    )
    return pricing
