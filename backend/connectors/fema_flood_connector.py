"""
FEMA Flood Zone MCP Connector

Sub-agent data fetcher used by Risk Profiling Agent to determine flood hazard
classification, Special Flood Hazard Area (SFHA) status, and actuarial flood risk scores.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import httpx

from backend.connectors.base import BaseMCPConnector, MCPResponse
from backend.models.schemas import FEMAFloodData

logger = logging.getLogger(__name__)

# Known flood profiles by state / zip prefix
FLOOD_ZONE_PROFILES = {
    "330": {  # FL Keys
        "zone": "Zone VE",
        "is_sfha": True,
        "bfe": 14.0,
        "depth": 5.2,
        "prob": 0.04,
        "score": 92.0,
        "summary": "FEMA Zone VE (Coastal High Hazard Wave Action Zone). Critical storm surge flood hazard.",
    },
    "331": {  # Miami-Dade
        "zone": "Zone AE",
        "is_sfha": True,
        "bfe": 9.0,
        "depth": 3.0,
        "prob": 0.025,
        "score": 82.0,
        "summary": "FEMA Zone AE (100-Year Base Floodplain with determined elevation). Mandatory flood insurance zone.",
    },
    "700": {  # New Orleans Delta
        "zone": "Zone A",
        "is_sfha": True,
        "bfe": 6.0,
        "depth": 4.5,
        "prob": 0.03,
        "score": 88.0,
        "summary": "FEMA Zone A (Special Flood Hazard Area in Mississippi Delta Basin). High inundation risk.",
    },
    "701": {  # New Orleans Metro
        "zone": "Zone AE",
        "is_sfha": True,
        "bfe": 7.0,
        "depth": 3.8,
        "prob": 0.028,
        "score": 85.0,
        "summary": "FEMA Zone AE (Urban Basin Special Flood Hazard Area). Significant storm surge and drainage exposure.",
    },
    "775": {  # Galveston Coastal
        "zone": "Zone VE",
        "is_sfha": True,
        "bfe": 12.0,
        "depth": 4.8,
        "prob": 0.035,
        "score": 90.0,
        "summary": "FEMA Zone VE (Gulf Coast Velocity Zone). Severe wave action and coastal surge exposure.",
    },
    "770": {  # Houston / Harris County
        "zone": "Zone AE",
        "is_sfha": True,
        "bfe": 45.0,
        "depth": 2.5,
        "prob": 0.02,
        "score": 70.0,
        "summary": "FEMA Zone AE (Bayou Floodplain). High convective rainfall accumulation exposure.",
    },
}


class FEMAFloodConnector(BaseMCPConnector):
    """
    FEMA National Flood Hazard Layer (NFHL) & OpenFEMA MCP connector.
    """

    def __init__(self, timeout_seconds: float = 3.5):
        super().__init__(
            connector_id="mcp-fema-flood",
            name="FEMA Flood Zone MCP Connector",
            timeout_seconds=timeout_seconds,
        )

    def _fetch_data(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> tuple[FEMAFloodData, bool]:
        """
        Query FEMA NFHL REST API / OpenFEMA endpoint.
        Falls back smoothly to geospatial simulation rules.
        """
        # If coordinates provided, attempt query to public FEMA GIS layer or OpenFEMA
        if latitude != 0.0 and longitude != 0.0:
            try:
                # ESRI FEMA NFHL REST query endpoint
                url = (
                    "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"
                    f"?geometry={longitude}%2C{latitude}&geometryType=esriGeometryPoint"
                    "&spatialRel=esriSpatialRelIntersects&outFields=FLD_ZONE,ZONE_SUBTY,SFHA_TF"
                    "&returnGeometry=false&f=json"
                )
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        features = data.get("features", [])
                        if features:
                            attr = features[0].get("attributes", {})
                            zone = attr.get("FLD_ZONE", "Zone X")
                            sfha = attr.get("SFHA_TF", "F") == "T" or zone in ("VE", "AE", "A", "V", "AO", "AH")
                            score = 85.0 if zone.startswith("V") else (75.0 if sfha else 20.0)
                            return (
                                FEMAFloodData(
                                    flood_zone=f"Zone {zone}",
                                    is_sfha=sfha,
                                    base_flood_elevation_ft=10.0 if sfha else None,
                                    flood_depth_estimate_ft=3.0 if sfha else 0.0,
                                    annual_flood_probability=0.02 if sfha else 0.002,
                                    flood_risk_score=score,
                                    fema_community_name=state.upper(),
                                    summary=f"FEMA NFHL verified flood zone: Zone {zone} (SFHA: {sfha}).",
                                    is_simulated=False,
                                ),
                                False,
                            )
            except Exception as live_err:
                logger.debug(f"Live FEMA NFHL GIS query error: {live_err}, using geospatial simulation fallback.")

        return self._simulate_fallback(latitude=latitude, longitude=longitude, state=state, zip_code=zip_code), True

    def _simulate_fallback(
        self,
        latitude: float = 0.0,
        longitude: float = 0.0,
        state: str = "",
        zip_code: str = "",
    ) -> FEMAFloodData:
        """Geospatial actuarial simulation for FEMA flood risk."""
        zc = zip_code.strip()
        st = state.upper().strip()

        # Check explicit high-risk ZIP prefix
        for prefix, prof in FLOOD_ZONE_PROFILES.items():
            if zc.startswith(prefix):
                return FEMAFloodData(
                    flood_zone=prof["zone"],
                    is_sfha=prof["is_sfha"],
                    base_flood_elevation_ft=prof["bfe"],
                    flood_depth_estimate_ft=prof["depth"],
                    annual_flood_probability=prof["prob"],
                    flood_risk_score=prof["score"],
                    fema_community_name=f"{st} Special Flood Jurisdiction",
                    summary=prof["summary"],
                    is_simulated=True,
                )

        # State-level baseline for coastal Florida / Louisiana
        if st in ("FL", "LA"):
            return FEMAFloodData(
                flood_zone="Zone AE",
                is_sfha=True,
                base_flood_elevation_ft=8.0,
                flood_depth_estimate_ft=2.0,
                annual_flood_probability=0.018,
                flood_risk_score=65.0,
                fema_community_name=f"{st} Coastal Flood District",
                summary=f"FEMA Zone AE ({st} Coastal Plain). Moderate-to-high seasonal precipitation exposure.",
                is_simulated=True,
            )

        # Standard inland / minimal risk zone
        return FEMAFloodData(
            flood_zone="Zone X (Unshaded)",
            is_sfha=False,
            base_flood_elevation_ft=None,
            flood_depth_estimate_ft=0.0,
            annual_flood_probability=0.002,
            flood_risk_score=15.0,
            fema_community_name=f"{st or 'Inland'} Municipal Water District",
            summary="FEMA Zone X (Area of Minimal Flood Hazard). Outside the 100-year and 500-year floodplains.",
            is_simulated=True,
        )


def fetch_fema_flood_data(
    latitude: float = 0.0,
    longitude: float = 0.0,
    state: str = "",
    zip_code: str = "",
) -> MCPResponse[FEMAFloodData]:
    """Functional helper for FEMA Flood MCP Connector."""
    connector = FEMAFloodConnector()
    return connector.execute(
        latitude=latitude,
        longitude=longitude,
        state=state,
        zip_code=zip_code,
    )
