"""
Risk Profiling Agent

Analyzes parsed submission data against external MCP feeds (FEMA Flood,
USGS Seismic, Open-Meteo Weather) and the risk calculator tool.
Optionally uses Gemini for AI risk narrative generation.
Implements auto-approve / manual-review / auto-decline logic.
"""

from __future__ import annotations

import logging

from backend.config import settings
from backend.connectors.location_intelligence import gather_location_intelligence
from backend.models.schemas import RiskProfile, SubmissionData
from backend.tools.risk_calculator import calculate_risk

logger = logging.getLogger(__name__)


def _generate_risk_narrative(data: SubmissionData, profile: RiskProfile) -> str:
    """Use Gemini to generate a human-readable risk narrative including MCP feeds."""
    if not settings.is_api_key_configured():
        return profile.risk_summary

    try:
        risk_factors_text = "\n".join(f"- {f}" for f in profile.risk_factors) if profile.risk_factors else "None identified"
        mitigating_text = "\n".join(f"- {f}" for f in profile.mitigating_factors) if profile.mitigating_factors else "None identified"

        mcp_summary_lines = []
        if profile.location_intelligence:
            loc = profile.location_intelligence
            if loc.fema_flood:
                mcp_summary_lines.append(f"FEMA Flood: {loc.fema_flood.flood_zone} (Risk: {loc.fema_flood.flood_risk_score}/100, SFHA: {loc.fema_flood.is_sfha})")
            if loc.usgs_seismic:
                mcp_summary_lines.append(f"USGS Seismic: {loc.usgs_seismic.seismic_zone} (PGA: {loc.usgs_seismic.peak_ground_acceleration_g}g, Risk: {loc.usgs_seismic.seismic_risk_score}/100)")
            if loc.open_meteo_weather:
                mcp_summary_lines.append(f"Open-Meteo Wind: {loc.open_meteo_weather.hurricane_exposure_tier} (Max Gusts: {loc.open_meteo_weather.max_wind_gust_mph} mph, Risk: {loc.open_meteo_weather.weather_risk_score}/100)")

        mcp_context = "\n".join(mcp_summary_lines) if mcp_summary_lines else "Standard location profile"

        prompt = f"""You are a senior commercial insurance underwriter. Write a concise 3-4 sentence risk assessment narrative for this submission incorporating both physical and external MCP hazard feeds.

Business: {data.business_info.business_name} ({data.business_info.business_type})
Location: {data.property_details.city}, {data.property_details.state} (Coords: {data.property_details.latitude:.3f}, {data.property_details.longitude:.3f})
Property Value: ${data.property_details.property_value:,.0f}
Composite Risk Score: {profile.composite_score}/100 ({profile.risk_tier.value})
Hazard Zones: {', '.join(profile.hazard_zones_detected) if profile.hazard_zones_detected else 'None'}

External MCP Environmental Feeds:
{mcp_context}

Key Risk Factors:
{risk_factors_text}

Mitigating Factors:
{mitigating_text}

Write a professional underwriting risk narrative referencing key location exposures and structural characteristics. Keep it under 110 words."""

        result = settings.call_gemini(prompt).strip()
        return result or profile.risk_summary

    except Exception as e:
        logger.warning(f"Risk narrative generation failed: {e}")
        return profile.risk_summary


def run_risk_agent(data: SubmissionData) -> RiskProfile:
    """
    Execute the Risk Profiling Agent.

    Steps:
    1. Invoke Location Intelligence MCP sub-agent to fetch FEMA flood, USGS seismic, and Open-Meteo weather
    2. Run risk_calculator tool for quantitative scoring enriched with MCP data
    3. Validate results against thresholds and hazard triggers
    4. Generate AI-enhanced risk narrative with Gemini

    Args:
        data: Structured submission data from Intake Agent.

    Returns:
        RiskProfile with composite score, tier, dimensions, and decision signals.
    """
    logger.info(f"Risk Agent processing submission {data.submission_id}")

    # Step 1: Sub-agent MCP call — Location Intelligence Research
    loc_intel = None
    try:
        loc_intel = gather_location_intelligence(
            submission_id=data.submission_id,
            address=data.property_details.address,
            city=data.property_details.city,
            state=data.property_details.state,
            zip_code=data.property_details.zip_code,
            existing_geocoding=data.property_details.geocoding,
        )
        logger.info(
            f"Location Intelligence MCP completed in {loc_intel.mcp_latency_ms}ms "
            f"— Composite Location Hazard: {loc_intel.composite_location_score}/100"
        )
    except Exception as e:
        logger.warning(f"Failed to gather Location Intelligence MCP: {e}")

    # Step 2: Tool call — quantitative risk scoring with MCP feeds
    profile = calculate_risk(data, location_intelligence=loc_intel)

    # Step 3: Validate and flag
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

    # Step 4: AI-enhanced narrative
    profile.risk_summary = _generate_risk_narrative(data, profile)

    logger.info(
        f"Risk Agent completed — score: {profile.composite_score}, "
        f"tier: {profile.risk_tier.value}"
    )
    return profile

