"""
Tests for MCP Connectors and Location Intelligence Sub-Agents
"""

import pytest
from backend.connectors.geocoding_connector import OpenMeteoGeocodingConnector, geocode_address
from backend.connectors.fema_flood_connector import FEMAFloodConnector, fetch_fema_flood_data
from backend.connectors.usgs_seismic_connector import USGSSeismicConnector, fetch_usgs_seismic_data
from backend.connectors.open_meteo_weather_connector import OpenMeteoWeatherConnector, fetch_weather_exposure
from backend.connectors.location_intelligence import (
    LocationIntelligenceAggregator,
    gather_location_intelligence,
)
from backend.agents.intake_agent import run_intake_agent
from backend.agents.risk_agent import run_risk_agent
from backend.models.schemas import SubmissionInput, SubmissionType
from backend.tools.risk_calculator import calculate_risk


class TestOpenMeteoGeocodingConnector:
    """Test geocoding address normalization and coordinate resolution."""

    def test_geocode_known_city_austin(self):
        resp = geocode_address(address="456 Corporate Plaza", city="Austin", state="TX", zip_code="73301")
        assert resp.success is True
        assert resp.data is not None
        geo = resp.data
        assert geo.city == "Austin"
        assert geo.state_code == "TX"
        assert geo.latitude > 0.0
        assert geo.longitude < 0.0
        assert geo.elevation_m > 0.0
        assert "Austin" in geo.normalized_address

    def test_geocode_miami_beach(self):
        resp = geocode_address(address="1200 Ocean Drive", city="Miami Beach", state="FL", zip_code="33139")
        assert resp.success is True
        assert resp.data is not None
        geo = resp.data
        assert geo.latitude > 24.0
        assert geo.longitude < -79.0


class TestFEMAFloodConnector:
    """Test FEMA flood zone classification and SFHA scoring."""

    def test_fema_high_risk_keys(self):
        resp = fetch_fema_flood_data(latitude=24.555, longitude=-81.780, state="FL", zip_code="33040")
        assert resp.success is True
        assert resp.data is not None
        fema = resp.data
        assert "VE" in fema.flood_zone or fema.is_sfha is True
        assert fema.flood_risk_score >= 80.0
        assert fema.is_sfha is True

    def test_fema_low_risk_inland(self):
        resp = fetch_fema_flood_data(latitude=30.267, longitude=-97.743, state="TX", zip_code="73301")
        assert resp.success is True
        assert resp.data is not None
        fema = resp.data
        assert fema.is_sfha is False
        assert fema.flood_risk_score <= 35.0


class TestUSGSSeismicConnector:
    """Test USGS earthquake hazard and fault line proximity."""

    def test_usgs_high_seismic_san_francisco(self):
        resp = fetch_usgs_seismic_data(latitude=37.774, longitude=-122.419, state="CA", zip_code="94102")
        assert resp.success is True
        assert resp.data is not None
        seismic = resp.data
        assert "Zone 4" in seismic.seismic_zone or seismic.seismic_risk_score >= 70.0
        assert seismic.peak_ground_acceleration_g > 0.3

    def test_usgs_low_seismic_texas(self):
        resp = fetch_usgs_seismic_data(latitude=30.267, longitude=-97.743, state="TX", zip_code="73301")
        assert resp.success is True
        assert resp.data is not None
        seismic = resp.data
        assert seismic.seismic_risk_score <= 30.0


class TestOpenMeteoWeatherConnector:
    """Test Open-Meteo hurricane exposure and extreme wind gusts."""

    def test_hurricane_tier_miami(self):
        resp = fetch_weather_exposure(latitude=25.761, longitude=-80.191, state="FL", zip_code="33139")
        assert resp.success is True
        assert resp.data is not None
        weather = resp.data
        assert weather.weather_risk_score >= 65.0
        assert "Tier" in weather.hurricane_exposure_tier
        assert weather.max_wind_gust_mph > 0.0

    def test_inland_wind_austin(self):
        resp = fetch_weather_exposure(latitude=30.267, longitude=-97.743, state="TX", zip_code="73301")
        assert resp.success is True
        assert resp.data is not None
        weather = resp.data
        assert weather.weather_risk_score <= 35.0


class TestLocationIntelligenceAggregator:
    """Test full multi-connector sub-agent workflow."""

    def test_location_intelligence_aggregation(self):
        report = gather_location_intelligence(
            submission_id="TEST-001",
            address="1200 Ocean Drive",
            city="Miami Beach",
            state="FL",
            zip_code="33139",
        )
        assert report.geocoding is not None
        assert report.fema_flood is not None
        assert report.usgs_seismic is not None
        assert report.open_meteo_weather is not None
        assert report.composite_location_score > 0.0
        assert len(report.hazard_alerts) >= 1
        assert report.mcp_latency_ms >= 0.0

    def test_risk_calculator_with_mcp_feeds(self):
        sub = SubmissionInput(
            submission_id="TEST-002",
            raw_text="""Business Name: Coral Reef Bar
Business Type: Restaurant / Bar
Annual Revenue: $800,000
Employees: 10
Years in Business: 4
Property Address: 100 Duval St
City: Key West
State: FL
Zip Code: 33040
Property Value: $750,000
Building Age: 15 years
Construction Type: Masonry
Claims in past 3 years: 0
""",
        )
        parsed = run_intake_agent(sub)
        assert parsed.property_details.latitude != 0.0
        assert parsed.property_details.geocoding is not None

        risk_profile = run_risk_agent(parsed)
        assert risk_profile.location_intelligence is not None
        assert risk_profile.is_hazard_zone is True
        assert any("Flood" in z or "Hurricane" in z for z in risk_profile.hazard_zones_detected)
