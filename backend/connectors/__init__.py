"""
Backend Connectors Package — Model Context Protocol (MCP) External Feeds

Provides standardized, resilient data-fetching connectors for external APIs
(Geocoding, FEMA Flood, USGS Seismic, Open-Meteo Extreme Weather) to enrich
underwriting agents with live location intelligence.
"""

from backend.connectors.base import BaseMCPConnector, MCPResponse
from backend.connectors.geocoding_connector import OpenMeteoGeocodingConnector, geocode_address
from backend.connectors.fema_flood_connector import FEMAFloodConnector, fetch_fema_flood_data
from backend.connectors.usgs_seismic_connector import USGSSeismicConnector, fetch_usgs_seismic_data
from backend.connectors.open_meteo_weather_connector import OpenMeteoWeatherConnector, fetch_weather_exposure
from backend.connectors.location_intelligence import (
    LocationIntelligenceAggregator,
    gather_location_intelligence,
)

__all__ = [
    "BaseMCPConnector",
    "MCPResponse",
    "OpenMeteoGeocodingConnector",
    "geocode_address",
    "FEMAFloodConnector",
    "fetch_fema_flood_data",
    "USGSSeismicConnector",
    "fetch_usgs_seismic_data",
    "OpenMeteoWeatherConnector",
    "fetch_weather_exposure",
    "LocationIntelligenceAggregator",
    "gather_location_intelligence",
]
