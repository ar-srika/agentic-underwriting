"""
Unit Tests for FastAPI REST Endpoints
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agents_registered"] == 6


def test_agent_registry_endpoint():
    response = client.get("/api/v1/registry")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 6
    assert any(a["agent_id"] == "intake-agent" for a in agents)


def test_underwrite_api_endpoint(low_risk_submission):
    response = client.post(
        "/api/v1/underwrite",
        json={"raw_text": low_risk_submission.raw_text, "submission_type": "text"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] in ["Auto-Approved", "Manual Review Required", "Auto-Declined"]
    assert "submission_id" in data
    assert data["pricing"]["final_premium"] <= 10000.0


def test_portfolio_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "total_submissions" in metrics
