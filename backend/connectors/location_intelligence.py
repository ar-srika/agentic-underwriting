"""
Location Intelligence Sub-Agent & MCP Aggregator

Coordinates external research across all 4 MCP connectors:
1. Open-Meteo Geocoding (Address normalization & lat/long coordinates)
2. FEMA Flood Zone (Flood risk score & SFHA determination)
3. USGS Seismic (Earthquake hazard score & fault proximity)
4. Open-Meteo Weather (Hurricane / windstorm exposure score)

Feeds structured location intelligence directly back to Intake and Risk Profiling Agents.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from backend.connectors.fema_flood_connector import fetch_fema_flood_data
from backend.connectors.geocoding_connector import geocode_address
from backend.connectors.open_meteo_weather_connector import fetch_weather_exposure
from backend.connectors.usgs_seismic_connector import fetch_usgs_seismic_data
from backend.models.schemas import (
    FEMAFloodData,
    GeocodingData,
    LocationIntelligenceReport,
    OpenMeteoWeatherData,
    USGSSeismicData,
)

logger = logging.getLogger(__name__)


class LocationIntelligenceAggregator:
    """
    Sub-agent data fetcher orchestrator for location-based risk intelligence.
    """

    def __init__(self):
        pass

    def gather(
        self,
        submission_id: str = "",
        address: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        existing_geocoding: Optional[GeocodingData] = None,
    ) -> LocationIntelligenceReport:
        """
        Execute full location research workflow across all MCP connectors.
        """
        start_time = time.perf_counter()
        logger.info(f"Initiating Location Intelligence MCP workflow for {submission_id or city}")

        # Step 1: Geocoding (Address Normalization)
        if existing_geocoding and existing_geocoding.latitude != 0.0:
            geocoding = existing_geocoding
            geo_lat_ms = 0.0
        else:
            geo_resp = geocode_address(address=address, city=city, state=state, zip_code=zip_code)
            geocoding = geo_resp.data or GeocodingData(city=city, state=state, zip_code=zip_code)
            geo_lat_ms = geo_resp.latency_ms

        lat = geocoding.latitude
        lon = geocoding.longitude
        resolved_state = geocoding.state_code or state or "TX"
        resolved_zip = geocoding.zip_code or zip_code or "73301"

        # Step 2: Query FEMA Flood MCP
        fema_resp = fetch_fema_flood_data(
            latitude=lat,
            longitude=lon,
            state=resolved_state,
            zip_code=resolved_zip,
        )
        fema_data: FEMAFloodData = fema_resp.data or FEMAFloodData()

        # Step 3: Query USGS Seismic MCP
        usgs_resp = fetch_usgs_seismic_data(
            latitude=lat,
            longitude=lon,
            state=resolved_state,
            zip_code=resolved_zip,
        )
        usgs_data: USGSSeismicData = usgs_resp.data or USGSSeismicData()

        # Step 4: Query Open-Meteo Weather MCP
        weather_resp = fetch_weather_exposure(
            latitude=lat,
            longitude=lon,
            state=resolved_state,
            zip_code=resolved_zip,
        )
        weather_data: OpenMeteoWeatherData = weather_resp.data or OpenMeteoWeatherData()

        # Step 5: Synthesize Composite Environmental Hazard Score (0-100)
        # Weights: Flood 40%, Seismic 30%, Wind/Weather 30%
        composite_hazard = (
            (fema_data.flood_risk_score * 0.40)
            + (usgs_data.seismic_risk_score * 0.30)
            + (weather_data.weather_risk_score * 0.30)
        )
        composite_hazard = round(min(100.0, max(0.0, composite_hazard)), 1)

        # Generate Hazard Alerts
        hazard_alerts = []
        if fema_data.is_sfha:
            hazard_alerts.append(f"🌊 Special Flood Hazard Area ({fema_data.flood_zone}) — Flood Risk: {fema_data.flood_risk_score}/100")
        if usgs_data.seismic_risk_score >= 65.0:
            hazard_alerts.append(f"🌋 High Seismic Exposure ({usgs_data.seismic_zone}) — PGA: {usgs_data.peak_ground_acceleration_g}g, Fault: {usgs_data.nearest_fault_name}")
        if weather_data.weather_risk_score >= 65.0 or "Tier" in weather_data.hurricane_exposure_tier and not weather_data.hurricane_exposure_tier.startswith("None"):
            hazard_alerts.append(f"🌪️ Severe Windstorm/Hurricane Exposure ({weather_data.hurricane_exposure_tier}) — Gusts: {weather_data.max_wind_gust_mph} mph")

        total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return LocationIntelligenceReport(
            submission_id=submission_id,
            geocoding=geocoding,
            fema_flood=fema_data,
            usgs_seismic=usgs_data,
            open_meteo_weather=weather_data,
            composite_location_score=composite_hazard,
            hazard_alerts=hazard_alerts,
            fetched_at=datetime.utcnow(),
            mcp_latency_ms=total_latency_ms,
        )


def gather_location_intelligence(
    submission_id: str = "",
    address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    existing_geocoding: Optional[GeocodingData] = None,
) -> LocationIntelligenceReport:
    """Convenience top-level entry point to run location intelligence research."""
    aggregator = LocationIntelligenceAggregator()
    return aggregator.gather(
        submission_id=submission_id,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        existing_geocoding=existing_geocoding,
    )
