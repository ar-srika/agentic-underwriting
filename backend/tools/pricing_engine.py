"""
Pricing Engine Tool

Custom premium calculation engine for Small Business Insurance.
Implements actuarial-style base-rate × modifier pricing with a
hard cap at $10,000.  All pricing rules are deterministic and
auditable.
"""

from __future__ import annotations

from backend.config import settings
from backend.models.schemas import (
    PricingModifier,
    PricingRecommendation,
    RiskProfile,
    SubmissionData,
)


# ────────────────────────────────────────────────────────────────────
# Base premium lookup tables
# ────────────────────────────────────────────────────────────────────

BUSINESS_TYPE_RATES: dict[str, float] = {
    "restaurant": 1.50,
    "bar": 1.60,
    "food service": 1.40,
    "retail": 1.00,
    "warehouse": 1.10,
    "office": 0.80,
    "technology": 0.70,
    "consulting": 0.75,
    "professional service": 0.75,
    "accounting": 0.70,
    "healthcare": 1.20,
    "manufacturing": 1.80,
    "construction": 2.00,
    "auto repair": 1.70,
    "beauty salon": 1.10,
    "fitness": 1.15,
    "education": 0.85,
}


def _get_base_premium(property_value: float) -> float:
    """Determine base premium from property value tier."""
    if property_value <= 0:
        return 1200.0  # default when unknown
    elif property_value <= 100_000:
        return 800.0
    elif property_value <= 250_000:
        return 1200.0
    elif property_value <= 500_000:
        return 1800.0
    elif property_value <= 1_000_000:
        return 2800.0
    else:
        return 4200.0


def _get_business_type_factor(business_type: str) -> tuple[float, str]:
    """Look up the business-type rating factor."""
    bt_lower = business_type.lower().strip()
    for key, rate in BUSINESS_TYPE_RATES.items():
        if key in bt_lower:
            return rate, f"Business type '{business_type}' → class factor {rate}"
    return 1.0, f"Business type '{business_type}' → standard class factor 1.0"


def _get_revenue_factor(annual_revenue: float) -> tuple[float, str]:
    """Rating factor based on annual revenue."""
    if annual_revenue <= 0:
        return 1.0, "Revenue undisclosed → standard factor"
    elif annual_revenue < 250_000:
        return 0.85, f"Micro-business revenue (${annual_revenue:,.0f}) → 0.85"
    elif annual_revenue < 500_000:
        return 0.90, f"Small revenue (${annual_revenue:,.0f}) → 0.90"
    elif annual_revenue < 2_000_000:
        return 1.00, f"Moderate revenue (${annual_revenue:,.0f}) → 1.00"
    elif annual_revenue < 5_000_000:
        return 1.15, f"Solid revenue (${annual_revenue:,.0f}) → 1.15"
    else:
        return 1.30, f"High revenue (${annual_revenue:,.0f}) → 1.30 (larger exposure)"


def _get_employee_factor(employee_count: int) -> tuple[float, str]:
    """Rating factor based on employee count."""
    if employee_count <= 5:
        return 0.90, f"{employee_count} employees → micro-business factor 0.90"
    elif employee_count <= 20:
        return 1.00, f"{employee_count} employees → standard factor 1.00"
    elif employee_count <= 50:
        return 1.10, f"{employee_count} employees → mid-size factor 1.10"
    else:
        return 1.25, f"{employee_count} employees → large workforce factor 1.25"


def _get_location_factor(risk_profile: RiskProfile) -> tuple[float, str]:
    """Rating factor based on location risk and hazard zones."""
    if not risk_profile.hazard_zones_detected:
        return 0.95, "No hazard zones → favorable location factor 0.95"
    elif len(risk_profile.hazard_zones_detected) == 1:
        return 1.25, f"1 hazard zone ({risk_profile.hazard_zones_detected[0]}) → factor 1.25"
    elif len(risk_profile.hazard_zones_detected) == 2:
        return 1.45, f"2 hazard zones → elevated factor 1.45"
    else:
        return 1.60, f"{len(risk_profile.hazard_zones_detected)} hazard zones → critical factor 1.60"


def _get_claims_factor(total_claims_3yr: int) -> tuple[float, str]:
    """Rating factor based on claims history."""
    if total_claims_3yr == 0:
        return 0.85, "0 claims in 3 years → claims-free discount 0.85"
    elif total_claims_3yr == 1:
        return 1.00, "1 claim in 3 years → standard factor 1.00"
    elif total_claims_3yr == 2:
        return 1.15, "2 claims in 3 years → surcharge factor 1.15"
    elif total_claims_3yr <= 4:
        return 1.40, f"{total_claims_3yr} claims in 3 years → heavy surcharge 1.40"
    else:
        return 1.60, f"{total_claims_3yr} claims in 3 years → severe surcharge 1.60"


def _get_safety_factor(data: SubmissionData) -> tuple[float, str]:
    """Rating factor based on safety features."""
    prop = data.property_details
    safety_count = sum([
        prop.has_sprinkler_system,
        prop.has_fire_alarm,
        prop.has_security_system,
    ])
    if safety_count == 3:
        return 0.82, "Full safety systems (sprinkler + alarm + security) → discount 0.82"
    elif safety_count == 2:
        return 0.90, "Partial safety systems → discount 0.90"
    elif safety_count == 1:
        return 0.95, "Minimal safety systems → slight discount 0.95"
    else:
        return 1.15, "No safety systems → surcharge 1.15"


def _get_experience_factor(years_in_business: int) -> tuple[float, str]:
    """Rating factor based on years in business."""
    if years_in_business >= 10:
        return 0.85, f"{years_in_business} years in business → veteran discount 0.85"
    elif years_in_business >= 5:
        return 0.92, f"{years_in_business} years in business → discount 0.92"
    elif years_in_business >= 2:
        return 1.00, f"{years_in_business} years in business → standard factor 1.00"
    else:
        return 1.20, f"New business (<2 years) → new venture surcharge 1.20"


def _get_building_age_factor(building_age: int) -> tuple[float, str]:
    """Rating factor based on building age."""
    if building_age <= 0:
        return 1.00, "Building age unknown → standard factor"
    elif building_age < 10:
        return 0.90, f"Modern building ({building_age}yr) → discount 0.90"
    elif building_age < 30:
        return 1.00, f"Standard age building ({building_age}yr) → factor 1.00"
    elif building_age < 50:
        return 1.10, f"Aging building ({building_age}yr) → surcharge 1.10"
    else:
        return 1.25, f"Old building ({building_age}yr) → significant surcharge 1.25"


# ────────────────────────────────────────────────────────────────────
# Main pricing calculation
# ────────────────────────────────────────────────────────────────────

def calculate_premium(
    data: SubmissionData,
    risk_profile: RiskProfile,
) -> PricingRecommendation:
    """
    Calculate the insurance premium for a small business submission.

    Uses base-rate × modifier approach with the following factors:
    1. Property value → base premium tier
    2. Business type → class factor
    3. Annual revenue → exposure factor
    4. Employee count → workforce factor
    5. Location/hazard zones → geographic factor
    6. Claims history → experience rating
    7. Safety features → protective systems credit
    8. Years in business → experience discount
    9. Building age → structural factor

    The final premium is capped at $10,000 (MAX_PREMIUM).

    Tool Call: This function is invoked by the Pricing Agent.

    Args:
        data: Parsed submission data from the Intake Agent.
        risk_profile: Risk assessment from the Risk Agent.

    Returns:
        PricingRecommendation with full premium breakdown.
    """
    biz = data.business_info
    prop = data.property_details
    claims = data.claims_history

    # Base premium
    base_premium = _get_base_premium(prop.property_value)

    # Calculate each modifier
    modifiers: list[PricingModifier] = []

    bt_factor, bt_reason = _get_business_type_factor(biz.business_type)
    modifiers.append(PricingModifier(name="Business Type", factor=bt_factor, reason=bt_reason))

    rev_factor, rev_reason = _get_revenue_factor(biz.annual_revenue)
    modifiers.append(PricingModifier(name="Revenue", factor=rev_factor, reason=rev_reason))

    emp_factor, emp_reason = _get_employee_factor(biz.employee_count)
    modifiers.append(PricingModifier(name="Employees", factor=emp_factor, reason=emp_reason))

    loc_factor, loc_reason = _get_location_factor(risk_profile)
    modifiers.append(PricingModifier(name="Location", factor=loc_factor, reason=loc_reason))

    clm_factor, clm_reason = _get_claims_factor(claims.total_claims_3yr)
    modifiers.append(PricingModifier(name="Claims History", factor=clm_factor, reason=clm_reason))

    saf_factor, saf_reason = _get_safety_factor(data)
    modifiers.append(PricingModifier(name="Safety Features", factor=saf_factor, reason=saf_reason))

    exp_factor, exp_reason = _get_experience_factor(biz.years_in_business)
    modifiers.append(PricingModifier(name="Business Experience", factor=exp_factor, reason=exp_reason))

    bld_factor, bld_reason = _get_building_age_factor(prop.building_age_years)
    modifiers.append(PricingModifier(name="Building Age", factor=bld_factor, reason=bld_reason))

    # Compute modifier product
    modifier_product = 1.0
    for m in modifiers:
        modifier_product *= m.factor
    modifier_product = round(modifier_product, 4)

    # Calculated premium
    calculated_premium = round(base_premium * modifier_product, 2)

    # Enforce hard cap
    premium_capped = calculated_premium > settings.MAX_PREMIUM
    final_premium = min(calculated_premium, settings.MAX_PREMIUM)
    final_premium = max(final_premium, settings.MIN_PREMIUM)

    # Product recommendation
    coverages = data.coverage_request.coverage_types
    if "General Liability" in coverages and "Property" in coverages:
        product = "Business Owners Policy (BOP)"
    elif len(coverages) >= 3:
        product = "Commercial Package Policy (CPP)"
    elif "Professional Liability" in coverages:
        product = "Professional Liability / E&O Policy"
    else:
        product = "Business Owners Policy (BOP)"

    # Coverage limit
    coverage_limit = data.coverage_request.desired_limit
    if coverage_limit <= 0:
        coverage_limit = max(prop.property_value, 500_000)

    # Pricing breakdown for visualization
    breakdown = {
        "Base Premium": base_premium,
        "After Business Type": round(base_premium * bt_factor, 2),
        "After Revenue": round(base_premium * bt_factor * rev_factor, 2),
        "After Location": round(base_premium * bt_factor * rev_factor * loc_factor, 2),
        "After Claims": round(base_premium * bt_factor * rev_factor * loc_factor * clm_factor, 2),
        "Final Calculated": calculated_premium,
        "Final (Capped)": final_premium,
    }

    notes = []
    if premium_capped:
        notes.append(f"⚠ Premium capped from ${calculated_premium:,.2f} to ${settings.MAX_PREMIUM:,.2f} (policy limit)")
    notes.append(f"Rating basis: {len(modifiers)} pricing factors applied")
    notes.append(f"Combined modifier product: {modifier_product}")

    return PricingRecommendation(
        submission_id=data.submission_id,
        base_premium=base_premium,
        modifiers=modifiers,
        modifier_product=modifier_product,
        calculated_premium=calculated_premium,
        final_premium=final_premium,
        premium_capped=premium_capped,
        product_recommendation=product,
        coverage_limit=coverage_limit,
        deductible=data.coverage_request.deductible_preference,
        pricing_notes=notes,
        pricing_breakdown=breakdown,
    )
