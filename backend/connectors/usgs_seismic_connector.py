"""
USGS Seismic MCP Connector

Sub-agent data fetcher used by Risk Profiling Agent to evaluate earthquake hazard,
seismic fault line proximity, historical event frequency, and Peak Ground Acceleration (PGA).
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import httpx

from backend.connectors.base import BaseMCPConnector, MCPResponse
from backend.models.schemas import USGSSeismicData

logger = logging.getLogger(__name__)

# Known high-seismic ZIP prefixes & fault associations
SEISMIC_PROFILES = {
    "941": {  # San Francisco / Bay Area
        "zone": "Zone 4 (Critical)",
        "fault": "San Andreas Fault / Hayward Fault",
        "proximity_km": 8.5,
        "max_mag": 6.9,
        "count_10yr": 42,
        "pga": 0.55,
        "score": 90.0,
        "summary": "USGS Seismic Zone 4. High-risk proximity to San Andreas Fault with elevated 50-year liquefaction potential.",
    },
    "900": {  # Los Angeles Basin
        "zone": "Zone 4 (Critical)",
        "fault": "Puente Hills / Newport-Inglewood Fault",
        "proximity_km": 11.2,
        "max_mag": 6.7,
        "count_10yr": 35,
        "pga": 0.48,
        "score": 85.0,
        "summary": "USGS Seismic Zone 4. Active strike-slip fault basin with high peak ground acceleration hazard.",
    },
    "921": {  # San Diego
        "zone": "Zone 3 (High)",
        "fault": "Rose Canyon Fault",
        "proximity_km": 16.0,
        "max_mag": 5.8,
        "count_10yr": 18,
        "pga": 0.32,
        "score": 68.0,
        "summary": "USGS Seismic Zone 3. Moderate-to-high seismic ground motion hazard.",
    },
    "954": {  # Sonoma / Napa Faults
        "zone": "Zone 3 (High)",
        "fault": "Rodgers Creek / West Napa Fault",
        "proximity_km": 14.5,
        "max_mag": 6.0,
        "count_10yr": 22,
        "pga": 0.38,
        "score": 72.0,
        "summary": "USGS Seismic Zone 3. Substantial ground shaking vulnerability in wine country fault basin.",
    },
}


class USGSSeismicConnector(BaseMCPConnector):
    """
    USGS Earthquake Hazards REST API connector.
    """

    def __init__(self, timeout_seconds: float = 3.5):
        super().__init__(
            connector_id="mcp-usgs-seismic",
            name="USGS Seismic MCP Connector",
            timeout_seconds=timeout_seconds,
        )

    def _fetch_data(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> tuple[USGSSeismicData, bool]:
        """
        Query USGS Earthquake API for historical events within a 150km radius.
        """
        zc = zip_code.strip()
        st = state.upper().strip()

        # Regional tectonic fault baseline
        base_zone = None
        base_pga = 0.05
        base_score = 10.0
        nearest_fault = f"{st} Regional Fault System" if st == "CA" else "None identified"
        proximity = 120.0
        hist_count = 0
        hist_max_mag = 0.0

        for prefix, prof in SEISMIC_PROFILES.items():
            if zc.startswith(prefix):
                base_zone = prof["zone"]
                base_pga = prof["pga"]
                base_score = prof["score"]
                nearest_fault = prof["fault"]
                proximity = prof["proximity_km"]
                hist_count = prof["count_10yr"]
                hist_max_mag = prof["max_mag"]
                break

        if not base_zone and st == "CA":
            base_zone = "Zone 3 (High)"
            base_pga = 0.28
            base_score = 60.0
            nearest_fault = "California Fault Network"
            proximity = 25.0
            hist_count = 12
            hist_max_mag = 5.4

        if latitude != 0.0 and longitude != 0.0:
            try:
                url = (
                    "https://earthquake.usgs.gov/fdsnws/event/1/query"
                    f"?format=geojson&latitude={latitude}&longitude={longitude}"
                    "&maxradiuskm=150&minmagnitude=3.5&limit=10"
                )
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        features = data.get("features", [])
                        count = len(features)
                        max_mag = max([f["properties"]["mag"] for f in features if f.get("properties", {}).get("mag") is not None], default=hist_max_mag)

                        final_zone = base_zone or ("Zone 4 (Critical)" if count > 5 or max_mag >= 5.0 else ("Zone 2 (Moderate)" if count > 0 else "Zone 1 (Low)"))
                        final_pga = max(base_pga, round(0.05 + (max_mag * 0.05), 3))
                        final_score = max(base_score, 80.0 if count > 5 else (40.0 + count * 5.0 if count > 0 else 15.0))

                        return (
                            USGSSeismicData(
                                seismic_zone=final_zone,
                                fault_line_proximity_km=proximity if proximity < 120.0 else (25.0 if count > 0 else 120.0),
                                nearest_fault_name=nearest_fault,
                                max_magnitude_nearby=round(max_mag, 1),
                                earthquake_count_10yr=max(count, hist_count),
                                peak_ground_acceleration_g=final_pga,
                                seismic_risk_score=round(min(100.0, final_score), 1),
                                summary=f"USGS live catalog: {final_zone} near {nearest_fault} ({proximity:.1f}km) with {final_pga}g PGA.",
                                is_simulated=False,
                            ),
                            False,
                        )
            except Exception as e:
                logger.debug(f"USGS live API call error: {e}, falling back to simulation.")

        return self._simulate_fallback(latitude=latitude, longitude=longitude, state=state, zip_code=zip_code), True

    def _simulate_fallback(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> USGSSeismicData:
        """Geospatial actuarial simulation for seismic hazard."""
        zc = zip_code.strip()
        st = state.upper().strip()

        # Check explicit high-risk ZIP prefix
        for prefix, prof in SEISMIC_PROFILES.items():
            if zc.startswith(prefix):
                return USGSSeismicData(
                    seismic_zone=prof["zone"],
                    fault_line_proximity_km=prof["proximity_km"],
                    nearest_fault_name=prof["fault"],
                    max_magnitude_nearby=prof["max_mag"],
                    earthquake_count_10yr=prof["count_10yr"],
                    peak_ground_acceleration_g=prof["pga"],
                    seismic_risk_score=prof["score"],
                    summary=prof["summary"],
                    is_simulated=True,
                )

        # California general baseline
        if st == "CA":
            return USGSSeismicData(
                seismic_zone="Zone 3 (High)",
                fault_line_proximity_km=28.0,
                nearest_fault_name="California Fault Network",
                max_magnitude_nearby=5.4,
                earthquake_count_10yr=12,
                peak_ground_acceleration_g=0.25,
                seismic_risk_score=60.0,
                summary="USGS Seismic Zone 3. Active tectonic region with moderate PGA exposure.",
                is_simulated=True,
            )

        # Standard low seismic zone (Texas, New York, Florida, Illinois, etc.)
        return USGSSeismicData(
            seismic_zone="Zone 1 (Low)",
            fault_line_proximity_km=180.0,
            nearest_fault_name="Stable Craton / Intraplate",
            max_magnitude_nearby=2.1,
            earthquake_count_10yr=0,
            peak_ground_acceleration_g=0.03,
            seismic_risk_score=10.0,
            summary="USGS Seismic Zone 1 (Stable Continental Region). Negligible earthquake hazard.",
            is_simulated=True,
        )


def fetch_usgs_seismic_data(
    latitude: float = 0.0,
    longitude: float = 0.0,
    state: str = "",
    zip_code: str = "",
) -> MCPResponse[USGSSeismicData]:
    """Functional helper for USGS Seismic MCP Connector."""
    connector = USGSSeismicConnector()
    return connector.execute(
        latitude=latitude,
        longitude=longitude,
        state=state,
        zip_code=zip_code,
    )
