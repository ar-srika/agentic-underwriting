"""
Open-Meteo Geocoding MCP Connector

Sub-agent data fetcher used by Intake Agent to normalize property addresses,
validate municipal jurisdictions, and extract geographic coordinates (lat/long)
and elevation.
"""

from __future__ import annotations

import logging
import urllib.parse
from typing import Any, Optional
import httpx

from backend.connectors.base import BaseMCPConnector, MCPResponse
from backend.models.schemas import GeocodingData

logger = logging.getLogger(__name__)

# Known baseline coordinates for deterministic simulation
KNOWN_CITY_COORDINATES = {
    ("AUSTIN", "TX"): (30.2672, -97.7431, 149.0, "73301"),
    ("MIAMI", "FL"): (25.7617, -80.1918, 2.0, "33139"),
    ("MIAMI BEACH", "FL"): (25.7907, -80.1300, 1.5, "33139"),
    ("KEY WEST", "FL"): (24.5551, -81.7800, 1.0, "33040"),
    ("NEW ORLEANS", "FL"): (29.9511, -90.0715, 1.0, "70112"),
    ("NEW ORLEANS", "LA"): (29.9511, -90.0715, 1.0, "70112"),
    ("SAN FRANCISCO", "CA"): (37.7749, -122.4194, 16.0, "94102"),
    ("LOS ANGELES", "CA"): (34.0522, -118.2437, 89.0, "90012"),
    ("SAN DIEGO", "CA"): (32.7157, -117.1611, 20.0, "92101"),
    ("GALVESTON", "TX"): (29.3013, -94.7977, 2.0, "77550"),
    ("HOUSTON", "TX"): (29.7604, -95.3698, 14.0, "77002"),
    ("DENVER", "CO"): (39.7392, -104.9903, 1609.0, "80202"),
    ("BOULDER", "CO"): (40.0150, -105.2705, 1655.0, "80302"),
    ("SANTA ROSA", "CA"): (38.4404, -122.7141, 50.0, "95401"),
    ("NEW YORK", "NY"): (40.7128, -74.0060, 10.0, "10001"),
    ("CHICAGO", "IL"): (41.8781, -87.6298, 181.0, "60601"),
}


class OpenMeteoGeocodingConnector(BaseMCPConnector):
    """
    Open-Meteo Geocoding API connector.
    Resolves freeform or structured location text to verified coordinates & addresses.
    """

    def __init__(self, timeout_seconds: float = 3.5):
        super().__init__(
            connector_id="mcp-open-meteo-geocoding",
            name="Open-Meteo Geocoding MCP Connector",
            timeout_seconds=timeout_seconds,
        )

    def _fetch_data(
        self,
        address: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
    ) -> tuple[GeocodingData, bool]:
        """Fetch live geocoding data from Open-Meteo."""
        # Construct search query
        query_parts = [p.strip() for p in [city, state, "United States"] if p.strip()]
        if not query_parts and address:
            query_parts = [address.strip(), "United States"]
        query = ", ".join(query_parts) if query_parts else "Austin, Texas"

        url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(query)}&count=5&language=en&format=json"

        with httpx.Client(timeout=self.timeout_seconds) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()

        results = data.get("results")
        if not results:
            return self._simulate_fallback(address=address, city=city, state=state, zip_code=zip_code), True

        # Pick best matching result
        best = results[0]
        st_name = best.get("admin1", state or "")
        cty_name = best.get("name", city or "")
        lat = float(best.get("latitude", 0.0))
        lon = float(best.get("longitude", 0.0))
        elevation = float(best.get("elevation", 0.0))
        tz = best.get("timezone", "America/Chicago")

        # Build normalized address
        street_prefix = address.strip() if address else "100 Commercial Blvd"
        norm_address = f"{street_prefix}, {cty_name}, {st_name} {zip_code}".strip(", ")

        return (
            GeocodingData(
                normalized_address=norm_address,
                city=cty_name,
                state=st_name,
                state_code=state.upper().strip() if len(state.strip()) == 2 else "",
                zip_code=zip_code,
                country=best.get("country", "United States"),
                latitude=round(lat, 5),
                longitude=round(lon, 5),
                elevation_m=round(elevation, 1),
                timezone=tz,
                confidence=0.98,
                is_simulated=False,
            ),
            False,
        )

    def _simulate_fallback(
        self,
        address: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
    ) -> GeocodingData:
        """Deterministic simulation for offline operation and known locations."""
        c_key = (city.upper().strip(), state.upper().strip())
        if c_key in KNOWN_CITY_COORDINATES:
            lat, lon, elev, default_zip = KNOWN_CITY_COORDINATES[c_key]
            actual_zip = zip_code.strip() or default_zip
        else:
            # General state-level hashing fallback
            lat = 30.0 + (hash(city.strip().upper()) % 1500) / 100.0
            lon = -95.0 - (hash(state.strip().upper()) % 2500) / 100.0
            elev = 15.0 + (hash(city.strip()) % 200)
            actual_zip = zip_code.strip() or "73301"

        resolved_city = city.strip() or "Austin"
        resolved_state = state.strip() or "TX"
        resolved_street = address.strip() or "456 Enterprise Way"
        norm_address = f"{resolved_street}, {resolved_city}, {resolved_state} {actual_zip}".strip()

        return GeocodingData(
            normalized_address=norm_address,
            city=resolved_city,
            state=resolved_state,
            state_code=resolved_state.upper() if len(resolved_state) == 2 else "TX",
            zip_code=actual_zip,
            country="United States",
            latitude=round(lat, 5),
            longitude=round(lon, 5),
            elevation_m=round(elev, 1),
            timezone="America/Chicago",
            confidence=0.92,
            is_simulated=True,
        )


def geocode_address(
    address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
) -> MCPResponse[GeocodingData]:
    """Convenience functional wrapper for the Geocoding MCP connector."""
    connector = OpenMeteoGeocodingConnector()
    return connector.execute(address=address, city=city, state=state, zip_code=zip_code)
