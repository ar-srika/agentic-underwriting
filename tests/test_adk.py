"""
Unit & Integration Tests for Google ADK (Agent Development Kit) Framework
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.adk.tools import (
    ADKTool,
    ADKToolRegistry,
    adk_tool,
    adk_geocode_tool,
    adk_fema_flood_tool,
    adk_usgs_seismic_tool,
    adk_weather_exposure_tool,
    adk_location_intelligence_mcp_tool,
)
from backend.adk.agents import (
    ADKAgent,
    adk_intake_agent,
    adk_risk_agent,
    adk_pricing_agent,
    adk_compliance_agent,
    adk_feedback_agent,
)
from backend.adk.runner import ADKRunner, ADKSupervisor
from backend.adk.session_store import ADKSessionStore
from backend.models.schemas import SubmissionInput, UnderwritingDecision, DecisionType


@pytest.fixture
def client():
    return TestClient(app)


def test_adk_tool_registry_and_mcp_binding():
    """Verify ADK Tool Registry and MCP Location Intelligence tool declarations."""
    tools = ADKToolRegistry.list_tools()
    assert len(tools) >= 5

    # Verify geocoding tool schema
    geo_tool = ADKToolRegistry.get_tool("adk_geocode_tool")
    assert geo_tool is not None
    schema = geo_tool.to_schema()
    assert schema["name"] == "adk_geocode_tool"
    assert "address" in schema["parameters"]["properties"]
    assert schema["category"] == "mcp_location"

    # Verify FEMA flood tool schema
    fema_tool = ADKToolRegistry.get_tool("adk_fema_flood_tool")
    assert fema_tool is not None
    fema_schema = fema_tool.to_schema()
    assert "latitude" in fema_schema["parameters"]["properties"]


def test_adk_custom_tool_decorator():
    """Verify @adk_tool decorator creates a functional ADKTool."""
    @adk_tool(name="sample_actuarial_tool", description="Calculates sample loading factor", category="actuarial")
    def sample_tool(base: float, multiplier: float) -> float:
        return base * multiplier

    tool = ADKToolRegistry.get_tool("sample_actuarial_tool")
    assert tool is not None
    assert tool(100.0, 1.25) == 125.0
    assert tool.total_invocations >= 1


def test_adk_agent_declarations():
    """Verify the 5 core Google ADK fleet agents are declared with Gemini models."""
    assert adk_intake_agent.agent_id == "adk-intake-agent"
    assert "gemini" in adk_intake_agent.model
    assert len(adk_intake_agent.tools) >= 1

    assert adk_risk_agent.agent_id == "adk-risk-agent"
    assert len(adk_risk_agent.tools) >= 2  # MCP tool + Risk calculator

    assert adk_pricing_agent.agent_id == "adk-pricing-agent"
    assert adk_compliance_agent.agent_id == "adk-compliance-agent"
    assert adk_feedback_agent.agent_id == "adk-feedback-agent"


def test_adk_runner_event_recording():
    """Verify ADKRunner manages isolated agent execution and emits audit events."""
    dummy_agent = ADKAgent(
        agent_id="dummy-test-agent",
        name="Dummy Test Agent",
        role="Tester",
        system_instruction="Test instruction",
        model="gemini-3.7-flash",
        runner_fn=lambda x: {"status": "processed", "input": x},
    )

    runner = ADKRunner(agent=dummy_agent, session_id="adk-session-123")
    result = runner.execute("test-payload")

    assert result["status"] == "processed"
    assert len(runner.events) == 2
    assert runner.events[0]["event"] == "agent_started"
    assert runner.events[1]["event"] == "agent_completed"
    assert runner.events[1]["data"]["status"] == "success"


def test_adk_supervisor_fleet_status():
    """Verify ADKSupervisor reports fleet status and tool schemas."""
    supervisor = ADKSupervisor()
    status = supervisor.get_fleet_status()

    assert status["adk_framework"] == "Google ADK (Agent Development Kit)"
    assert status["supervised_agents_count"] == 5
    assert status["registered_tools_count"] >= 5
    assert len(status["tool_declarations"]) >= 5


def test_adk_session_store_cold_storage():
    """Verify ADKSessionStore cold storage snapshot save and hydration."""
    store = ADKSessionStore()
    sessions = store.list_sessions()
    assert len(sessions) >= 1  # Pre-seeded snapshot

    target_id = sessions[0].session_id
    hydrated = store.hydrate_session(target_id)
    assert hydrated is not None
    assert hydrated.session_id == target_id
    assert hydrated.status == "HYDRATED"
    assert hydrated.decision is not None


def test_adk_api_endpoints(client):
    """Verify /api/v1/adk/status and /health ADK responses via FastAPI."""
    # Test ADK status endpoint
    resp = client.get("/api/v1/adk/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["adk_framework"] == "Google ADK (Agent Development Kit)"
    assert data["supervised_agents_count"] == 5

    # Test health check reports ADK status
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert "adk_status" in health_data
    assert health_data["adk_status"]["adk_supervisor"] == "Active"
