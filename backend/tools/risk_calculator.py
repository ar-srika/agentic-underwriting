"""
Risk Calculator Tool

Custom rule-based risk scoring engine for small business insurance.
Evaluates six risk dimensions, detects hazard zones, and determines
auto-approve / manual-review / auto-decline decisions.
"""

from __future__ import annotations

from backend.config import settings
from backend.models.schemas import (
    DecisionType,
    LocationIntelligenceReport,
    RiskDimension,
    RiskProfile,
    RiskTier,
    SubmissionData,
)


# ────────────────────────────────────────────────────────────────────
# Hazard zone / decline lookup tables
# ────────────────────────────────────────────────────────────────────

# High-risk coastal and disaster-prone zones
CRITICAL_HAZARD_STATES = {"FL", "LA"}

HAZARDOUS_ZIP_PREFIXES = {
    "330": "FEMA Flood Zone VE (Keys)",
    "331": "FEMA Flood Zone AE (Miami-Dade)",
    "339": "Hurricane Wind-Borne Debris Region",
    "700": "FEMA Flood Zone A (Delta Region)",
    "701": "FEMA Flood Zone A (New Orleans)",
    "770": "Hurricane Storm Surge Tier 1",
    "775": "Coastal Flood Zone VE (Galveston)",
    "900": "Seismic Alquist-Priolo Zone 4 (LA Basin)",
    "941": "Seismic Zone 4 (San Francisco Fault Line)",
    "921": "Wildfire Urban Interface - Very High (San Diego)",
    "803": "Wildfire Wildland Urban Interface (Front Range)",
    "954": "Wildfire High Severity Zone (Sonoma/Napa)",
}


def _get_hazard_zones(state: str, zip_code: str) -> list[str]:
    """Determine which hazard zones apply to a specific property location."""
    zones = []
    st = state.upper().strip()
    zc = zip_code.strip()

    # Specific high-risk ZIP prefix matching
    for prefix, zone in HAZARDOUS_ZIP_PREFIXES.items():
        if zc.startswith(prefix):
            if zone not in zones:
                zones.append(zone)

    # State-level baseline for extreme coastal flood exposure
    if st in CRITICAL_HAZARD_STATES and not zones:
        zones.append(f"FEMA Special Flood Hazard Area ({st} Coastal)")

    return zones


def _score_property_risk(data: SubmissionData) -> RiskDimension:
    """Score the physical property risk (0-100)."""
    prop = data.property_details
    score = 30.0  # baseline
    factors = []

    # Building age
    if prop.building_age_years > 50:
        score += 25
        factors.append(f"Building age {prop.building_age_years}yr — significant structural risk")
    elif prop.building_age_years > 30:
        score += 15
        factors.append(f"Building age {prop.building_age_years}yr — moderate aging")
    elif prop.building_age_years > 10:
        score += 5
        factors.append(f"Building age {prop.building_age_years}yr — acceptable")
    else:
        score -= 10
        factors.append("Modern construction — low structural risk")

    # Safety features (reduce risk)
    safety_count = sum([
        prop.has_sprinkler_system,
        prop.has_fire_alarm,
        prop.has_security_system,
    ])
    if safety_count == 3:
        score -= 20
        factors.append("Full safety systems installed (sprinkler, alarm, security)")
    elif safety_count == 2:
        score -= 10
        factors.append("Partial safety systems installed")
    elif safety_count == 1:
        score -= 5
        factors.append("Minimal safety systems")
    else:
        score += 15
        factors.append("No safety systems — elevated fire/theft risk")

    # Construction type
    ct = prop.construction_type.lower()
    if "fire" in ct or "concrete" in ct or "masonry" in ct:
        score -= 5
        factors.append(f"Fire-resistant construction ({prop.construction_type})")
    elif "wood" in ct or "frame" in ct:
        score += 10
        factors.append(f"Wood/frame construction — higher fire risk")

    # Roof condition
    if prop.roof_condition.lower() in ("poor", "deteriorated", "damaged"):
        score += 15
        factors.append("Poor roof condition")

    score = max(0, min(100, score))
    return RiskDimension(
        name="Property Risk",
        score=round(score, 1),
        weight=0.20,
        factors=factors,
        recommendation="Property inspection recommended" if score > 50 else "Acceptable property condition",
    )


def _score_location_risk(
    data: SubmissionData,
    location_intelligence: Optional[LocationIntelligenceReport] = None,
) -> tuple[RiskDimension, list[str]]:
    """
    Score geographic location risk using MCP external feeds (FEMA, USGS, Open-Meteo).
    Blends real-time flood zone, seismic hazard, and windstorm exposure.
    """
    prop = data.property_details
    factors = []
    hazard_zones = _get_hazard_zones(prop.state, prop.zip_code)

    if location_intelligence:
        # 1. FEMA Flood MCP feed
        fema = location_intelligence.fema_flood
        if fema:
            if fema.is_sfha or fema.flood_risk_score >= 60:
                zone_label = f"FEMA Special Flood Hazard Area ({fema.flood_zone})"
                if zone_label not in hazard_zones:
                    hazard_zones.append(zone_label)
                factors.append(f"🌊 FEMA Flood: {fema.summary} (Flood Risk: {fema.flood_risk_score}/100)")
            else:
                factors.append(f"🌊 FEMA Flood: {fema.flood_zone} — Minimal inundation exposure (Score: {fema.flood_risk_score}/100)")

        # 2. USGS Seismic MCP feed
        seismic = location_intelligence.usgs_seismic
        if seismic:
            if seismic.seismic_risk_score >= 65:
                seismic_label = f"USGS High Seismic Hazard ({seismic.seismic_zone})"
                if seismic_label not in hazard_zones:
                    hazard_zones.append(seismic_label)
                factors.append(f"🌋 USGS Seismic: {seismic.summary} (PGA: {seismic.peak_ground_acceleration_g}g, Score: {seismic.seismic_risk_score}/100)")
            else:
                factors.append(f"🌋 USGS Seismic: Stable intraplate region ({seismic.seismic_zone}) (Score: {seismic.seismic_risk_score}/100)")

        # 3. Open-Meteo Extreme Weather / Hurricane MCP feed
        weather = location_intelligence.open_meteo_weather
        if weather:
            if weather.weather_risk_score >= 65 or (weather.hurricane_exposure_tier and not weather.hurricane_exposure_tier.startswith("None")):
                weather_label = f"Severe Wind/Hurricane Exposure ({weather.hurricane_exposure_tier})"
                if weather_label not in hazard_zones:
                    hazard_zones.append(weather_label)
                factors.append(f"🌪️ Open-Meteo Wind: {weather.summary} (Max gusts: {weather.max_wind_gust_mph} mph, Score: {weather.weather_risk_score}/100)")
            else:
                factors.append(f"🌪️ Open-Meteo Wind: Standard wind load ({weather.max_wind_gust_mph} mph max gusts, Score: {weather.weather_risk_score}/100)")

        # Dynamic location score driven directly by composite MCP feeds
        score = location_intelligence.composite_location_score
        if hazard_zones:
            score = max(score, 45.0 + len(hazard_zones) * 10.0)
    else:
        # Fallback to static rule lookup
        score = 20.0
        if hazard_zones:
            zone_penalty = len(hazard_zones) * 15
            score += zone_penalty
            for z in hazard_zones:
                factors.append(f"🔴 Hazard zone detected: {z}")
        else:
            factors.append("No known hazard zones at property location")
            score -= 5

    # Deduplicate hazard zones while preserving order
    deduped_zones = list(dict.fromkeys(hazard_zones))

    score = max(0.0, min(100.0, score))
    return (
        RiskDimension(
            name="Location Risk",
            score=round(score, 1),
            weight=0.20,
            factors=factors,
            recommendation="Mandatory human review for hazard zone" if deduped_zones else "Location acceptable",
        ),
        deduped_zones,
    )


def _score_financial_risk(data: SubmissionData) -> RiskDimension:
    """Score the financial stability risk."""
    biz = data.business_info
    score = 25.0
    factors = []

    # Revenue analysis
    if biz.annual_revenue >= 2_000_000:
        score -= 10
        factors.append(f"Strong revenue (${biz.annual_revenue:,.0f}) — financially stable")
    elif biz.annual_revenue >= 500_000:
        score -= 5
        factors.append(f"Moderate revenue (${biz.annual_revenue:,.0f})")
    elif biz.annual_revenue > 0:
        score += 10
        factors.append(f"Low revenue (${biz.annual_revenue:,.0f}) — financial pressure risk")
    else:
        score += 15
        factors.append("Revenue not reported — unable to assess financial stability")

    # Years in business (longevity = stability)
    if biz.years_in_business >= 10:
        score -= 10
        factors.append(f"Established business ({biz.years_in_business} years)")
    elif biz.years_in_business >= 5:
        score -= 5
        factors.append(f"Maturing business ({biz.years_in_business} years)")
    elif biz.years_in_business >= 2:
        factors.append(f"Newer business ({biz.years_in_business} years)")
    else:
        score += 15
        factors.append(f"Startup (<2 years) — higher failure risk")

    score = max(0, min(100, score))
    return RiskDimension(
        name="Financial Risk",
        score=round(score, 1),
        weight=0.15,
        factors=factors,
        recommendation="Consider financial guarantees" if score > 50 else "Financial profile acceptable",
    )


def _score_claims_risk(data: SubmissionData) -> RiskDimension:
    """Score claims history risk."""
    claims = data.claims_history
    score = 15.0
    factors = []

    if claims.total_claims_3yr == 0:
        score -= 10
        factors.append("Clean claims history (0 claims in 3 years)")
    elif claims.total_claims_3yr <= 2:
        score += 10
        factors.append(f"{claims.total_claims_3yr} claim(s) in 3 years — moderate")
    elif claims.total_claims_3yr <= 4:
        score += 30
        factors.append(f"{claims.total_claims_3yr} claims in 3 years — elevated frequency")
    else:
        score += 50
        factors.append(f"🔴 {claims.total_claims_3yr} claims in 3 years — excessive claim frequency")

    if claims.largest_claim_amount > 100_000:
        score += 15
        factors.append(f"Large prior claim (${claims.largest_claim_amount:,.0f})")
    elif claims.largest_claim_amount > 50_000:
        score += 8
        factors.append(f"Moderate prior claim (${claims.largest_claim_amount:,.0f})")

    score = max(0, min(100, score))
    return RiskDimension(
        name="Claims Risk",
        score=round(score, 1),
        weight=0.20,
        factors=factors,
        recommendation="Require higher deductible" if score > 50 else "Claims history acceptable",
    )


def _score_operational_risk(data: SubmissionData) -> RiskDimension:
    """Score operational / business-type risk."""
    biz = data.business_info
    score = 25.0
    factors = []

    # Business type risk classification
    bt = biz.business_type.lower()
    high_risk_types = ["restaurant", "bar", "manufacturing", "construction", "auto repair"]
    medium_risk_types = ["retail", "warehouse", "food service", "healthcare"]
    low_risk_types = ["office", "technology", "consulting", "professional service", "accounting"]

    if any(t in bt for t in high_risk_types):
        score += 20
        factors.append(f"High-risk business category: {biz.business_type}")
    elif any(t in bt for t in medium_risk_types):
        score += 10
        factors.append(f"Medium-risk business category: {biz.business_type}")
    elif any(t in bt for t in low_risk_types):
        score -= 10
        factors.append(f"Low-risk business category: {biz.business_type}")
    else:
        factors.append(f"Business type: {biz.business_type} — standard risk")

    # Employee count
    if biz.employee_count > 50:
        score += 10
        factors.append(f"{biz.employee_count} employees — increased workers comp exposure")
    elif biz.employee_count > 20:
        score += 5
        factors.append(f"{biz.employee_count} employees — moderate workforce")

    score = max(0, min(100, score))
    return RiskDimension(
        name="Operational Risk",
        score=round(score, 1),
        weight=0.15,
        factors=factors,
        recommendation="Additional operational controls recommended" if score > 50 else "Operational profile acceptable",
    )


def _score_compliance_risk(data: SubmissionData) -> RiskDimension:
    """Score compliance / licensing risk."""
    biz = data.business_info
    score = 10.0
    factors = []

    if not biz.has_valid_license:
        score += 60
        factors.append("🔴 No valid business license — major compliance issue")

    if biz.previous_policy_cancelled:
        score += 30
        reason = biz.cancellation_reason or "Reason unknown"
        factors.append(f"🔴 Previous policy cancelled: {reason}")
        if "fraud" in reason.lower():
            score += 30
            factors.append("🔴 Prior cancellation for fraud — severe risk flag")

    if not factors:
        factors.append("Clean compliance record — no licensing or cancellation issues")

    score = max(0, min(100, score))
    return RiskDimension(
        name="Compliance Risk",
        score=round(score, 1),
        weight=0.10,
        factors=factors,
        recommendation="Verify licensing and regulatory standing" if score > 30 else "Compliance acceptable",
    )


# ────────────────────────────────────────────────────────────────────
# Main risk calculation entry point
# ────────────────────────────────────────────────────────────────────

def calculate_risk(
    data: SubmissionData,
    location_intelligence: Optional[LocationIntelligenceReport] = None,
) -> RiskProfile:
    """
    Compute comprehensive risk profile for a submission.

    Evaluates 6 risk dimensions, enriches location risk using external MCP feeds
    (FEMA, USGS, Open-Meteo), detects hazard zones, checks auto-decline criteria,
    and produces a composite risk score.

    Tool Call: This function is invoked by the Risk Profiling Agent.

    Args:
        data: Parsed submission data from the Intake Agent.
        location_intelligence: Optional aggregated MCP external research data.

    Returns:
        RiskProfile with composite score, tier, dimensions, and decision signals.
    """
    biz = data.business_info
    claims = data.claims_history

    # Score each dimension
    property_dim = _score_property_risk(data)
    location_dim, hazard_zones = _score_location_risk(data, location_intelligence=location_intelligence)
    financial_dim = _score_financial_risk(data)
    claims_dim = _score_claims_risk(data)
    operational_dim = _score_operational_risk(data)
    compliance_dim = _score_compliance_risk(data)

    dimensions = [
        property_dim, location_dim, financial_dim,
        claims_dim, operational_dim, compliance_dim,
    ]

    # Weighted composite score
    composite = sum(d.score * d.weight for d in dimensions)
    composite = round(min(100, max(0, composite)), 1)

    # Risk tier
    if composite <= settings.AUTO_APPROVE_THRESHOLD:
        tier = RiskTier.LOW
    elif composite <= settings.MANUAL_REVIEW_THRESHOLD:
        tier = RiskTier.MEDIUM
    elif composite <= settings.AUTO_DECLINE_THRESHOLD:
        tier = RiskTier.HIGH
    else:
        tier = RiskTier.CRITICAL

    # Auto-decline triggers
    decline_triggers = []
    bt_lower = biz.business_type.lower()
    for prohibited in settings.PROHIBITED_BUSINESS_TYPES:
        if prohibited in bt_lower:
            decline_triggers.append(f"Prohibited business type: {biz.business_type}")
    if claims.total_claims_3yr >= settings.MAX_CLAIMS_BEFORE_DECLINE:
        decline_triggers.append(f"Excessive claims: {claims.total_claims_3yr} in 3 years (max {settings.MAX_CLAIMS_BEFORE_DECLINE})")
    if biz.previous_policy_cancelled and biz.cancellation_reason and "fraud" in biz.cancellation_reason.lower():
        decline_triggers.append("Previous policy cancelled for fraud")
    if not biz.has_valid_license:
        decline_triggers.append("No valid business license")
    if composite > settings.AUTO_DECLINE_THRESHOLD:
        decline_triggers.append(f"Composite risk score {composite} exceeds decline threshold ({settings.AUTO_DECLINE_THRESHOLD})")

    # Risk factors and mitigating factors
    risk_factors = []
    mitigating = []
    for d in dimensions:
        for f in d.factors:
            if "🔴" in f or "🌊" in f or "🌋" in f or "🌪️" in f or d.score > 50:
                risk_factors.append(f)
            elif d.score < 25:
                mitigating.append(f)

    # Summary
    summary_parts = [
        f"Composite risk score: {composite}/100 ({tier.value} Risk).",
    ]
    if hazard_zones:
        summary_parts.append(f"Property is in {len(hazard_zones)} hazard zone(s): {', '.join(hazard_zones)}.")
        summary_parts.append("MANDATORY human underwriter review required for hazard zone properties.")
    if decline_triggers:
        summary_parts.append(f"AUTO-DECLINE TRIGGERED: {'; '.join(decline_triggers)}.")

    return RiskProfile(
        submission_id=data.submission_id,
        composite_score=composite,
        risk_tier=tier,
        dimensions=dimensions,
        hazard_zones_detected=hazard_zones,
        is_hazard_zone=len(hazard_zones) > 0,
        auto_decline_triggers=decline_triggers,
        risk_summary=" ".join(summary_parts),
        risk_factors=risk_factors,
        mitigating_factors=mitigating,
        location_intelligence=location_intelligence,
    )
