"""
Open-Meteo Weather & Extreme Windstorm MCP Connector

Sub-agent data fetcher used by Risk Profiling Agent to evaluate hurricane exposure,
extreme wind gusts, convective storm intensity, and severe weather vulnerability.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import httpx

from backend.connectors.base import BaseMCPConnector, MCPResponse
from backend.models.schemas import OpenMeteoWeatherData

logger = logging.getLogger(__name__)

# Known hurricane & convective storm risk profiles by ZIP prefix
WEATHER_PROFILES = {
    "330": {  # FL Keys
        "max_gust": 155.0,
        "tier": "Tier 5 (Category 5 Hurricane Exposure)",
        "precip": 44.0,
        "convective": "High",
        "score": 96.0,
        "summary": "Critical Hurricane Exposure (Cat 5 Wind-Borne Debris Region). Severe hurricane and storm surge exposure.",
    },
    "331": {  # Miami-Dade
        "max_gust": 135.0,
        "tier": "Tier 4 (Category 4 Hurricane Exposure)",
        "precip": 62.0,
        "convective": "High",
        "score": 85.0,
        "summary": "High Hurricane Exposure (South Florida High-Velocity Hurricane Zone). Severe tropical cyclone vulnerability.",
    },
    "339": {  # Southwest FL (Ft. Myers / Naples)
        "max_gust": 125.0,
        "tier": "Tier 3 (Category 3 Hurricane Exposure)",
        "precip": 54.0,
        "convective": "High",
        "score": 80.0,
        "summary": "Elevated Hurricane Exposure (Gulf Coast Hurricane Corridor). Significant wind-borne debris hazard.",
    },
    "775": {  # Galveston
        "max_gust": 120.0,
        "tier": "Tier 3 (Category 3 Hurricane Exposure)",
        "precip": 58.0,
        "convective": "High",
        "score": 82.0,
        "summary": "Gulf Coast Storm Surge & Hurricane Tier 3. Substantial coastal wind and rainfall exposure.",
    },
    "770": {  # Houston
        "max_gust": 95.0,
        "tier": "Tier 2 (Category 2 Hurricane Exposure)",
        "precip": 52.0,
        "convective": "Severe",
        "score": 68.0,
        "summary": "Sub-tropical Convective & Tropical Depression Zone. Extreme precipitation and straight-line wind hazard.",
    },
    "700": {  # New Orleans
        "max_gust": 115.0,
        "tier": "Tier 3 (Category 3 Hurricane Exposure)",
        "precip": 64.0,
        "convective": "High",
        "score": 78.0,
        "summary": "Mississippi Delta Cyclone Exposure. Tropical storm surge and severe moisture convergence.",
    },
    "701": {  # New Orleans Metro
        "max_gust": 110.0,
        "tier": "Tier 3 (Category 3 Hurricane Exposure)",
        "precip": 64.0,
        "convective": "High",
        "score": 75.0,
        "summary": "Urban Gulf Coast Hurricane Corridor. High windstorm and localized inundation risk.",
    },
}


class OpenMeteoWeatherConnector(BaseMCPConnector):
    """
    Open-Meteo Weather Forecast & Climate Extreme MCP Connector.
    """

    def __init__(self, timeout_seconds: float = 3.5):
        super().__init__(
            connector_id="mcp-open-meteo-weather",
            name="Open-Meteo Weather & Extreme Wind MCP Connector",
            timeout_seconds=timeout_seconds,
        )

    def _fetch_data(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> tuple[OpenMeteoWeatherData, bool]:
        """
        Query Open-Meteo Daily Weather API for wind gusts, speed, and precipitation.
        """
        if latitude != 0.0 and longitude != 0.0:
            try:
                url = (
                    "https://api.open-meteo.com/v1/forecast"
                    f"?latitude={latitude}&longitude={longitude}"
                    "&daily=wind_speed_10m_max,wind_gusts_10m_max,precipitation_sum"
                    "&wind_speed_unit=mph&precipitation_unit=inch&timezone=auto"
                )
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        daily = data.get("daily", {})
                        gusts = daily.get("wind_gusts_10m_max", [])
                        precip = daily.get("precipitation_sum", [])

                        max_gust = max(gusts, default=35.0)
                        tot_precip = sum(precip) if precip else 0.5

                        # Evaluate hurricane tier based on gust thresholds and state
                        st = state.upper().strip()
                        if max_gust >= 130 or (st == "FL" and zip_code.startswith("330")):
                            tier = "Tier 4 (Category 4 Hurricane Exposure)"
                            score = 85.0
                        elif max_gust >= 100 or st in ("FL", "LA"):
                            tier = "Tier 3 (Category 3 Hurricane Exposure)"
                            score = 70.0
                        elif max_gust >= 65:
                            tier = "Tier 2 (Gale / Convective Storm Exposure)"
                            score = 45.0
                        else:
                            tier = "None (Standard Wind Load)"
                            score = 18.0

                        return (
                            OpenMeteoWeatherData(
                                max_wind_gust_mph=round(max_gust, 1),
                                hurricane_exposure_tier=tier,
                                annual_precipitation_inches=round(tot_precip * 52, 1) or 38.0,
                                severe_convective_storm_risk="Moderate" if max_gust > 50 else "Low",
                                weather_risk_score=round(score, 1),
                                summary=f"Open-Meteo telemetry: Peak recorded wind gust {max_gust:.1f} mph ({tier}).",
                                is_simulated=False,
                            ),
                            False,
                        )
            except Exception as e:
                logger.debug(f"Open-Meteo live weather API error: {e}, falling back to simulation.")

        return self._simulate_fallback(latitude=latitude, longitude=longitude, state=state, zip_code=zip_code), True

    def _simulate_fallback(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> OpenMeteoWeatherData:
        """Geospatial actuarial simulation for hurricane and severe weather exposure."""
        zc = zip_code.strip()
        st = state.upper().strip()

        # Check explicit high-risk ZIP prefix
        for prefix, prof in WEATHER_PROFILES.items():
            if zc.startswith(prefix):
                return OpenMeteoWeatherData(
                    max_wind_gust_mph=prof["max_gust"],
                    hurricane_exposure_tier=prof["tier"],
                    annual_precipitation_inches=prof["precip"],
                    severe_convective_storm_risk=prof["convective"],
                    weather_risk_score=prof["score"],
                    summary=prof["summary"],
                    is_simulated=True,
                )

        # Coastal Florida baseline
        if st == "FL":
            return OpenMeteoWeatherData(
                max_wind_gust_mph=110.0,
                hurricane_exposure_tier="Tier 3 (Category 3 Hurricane Exposure)",
                annual_precipitation_inches=55.0,
                severe_convective_storm_risk="High",
                weather_risk_score=72.0,
                summary="Florida Hurricane Corridor. High exposure to severe tropical cyclonic systems and windstorm losses.",
                is_simulated=True,
            )

        # Coastal Louisiana / Texas Gulf baseline
        if st in ("LA", "TX") and (zc.startswith("70") or zc.startswith("77")):
            return OpenMeteoWeatherData(
                max_wind_gust_mph=90.0,
                hurricane_exposure_tier="Tier 2 (Category 2 Hurricane Exposure)",
                annual_precipitation_inches=50.0,
                severe_convective_storm_risk="High",
                weather_risk_score=60.0,
                summary="Gulf Coast Tropical Basin. Moderate-to-high storm surge and localized windstorm hazard.",
                is_simulated=True,
            )

        # Standard inland / minimal windstorm exposure (Austin, Denver, Chicago, etc.)
        return OpenMeteoWeatherData(
            max_wind_gust_mph=42.0,
            hurricane_exposure_tier="None (Inland Low Exposure)",
            annual_precipitation_inches=34.0,
            severe_convective_storm_risk="Low",
            weather_risk_score=15.0,
            summary="Inland Standard Zone. Low hurricane and extreme windstorm exposure; baseline structural loading.",
            is_simulated=True,
        )


def fetch_weather_exposure(
    latitude: float = 0.0,
    longitude: float = 0.0,
    state: str = "",
    zip_code: str = "",
) -> MCPResponse[OpenMeteoWeatherData]:
    """Functional helper for Open-Meteo Weather MCP Connector."""
    connector = OpenMeteoWeatherConnector()
    return connector.execute(
        latitude=latitude,
        longitude=longitude,
        state=state,
        zip_code=zip_code,
    )
