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
    assert data["agents_registered"] >= 6


def test_agent_registry_endpoint():
    response = client.get("/api/v1/registry")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) >= 6
    assert any(a["agent_id"] == "intake-agent" for a in agents)
    assert any(a["agent_id"] == "mcp-open-meteo-geocoding" for a in agents)


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


def test_notifications_endpoint():
    response = client.get("/api/v1/notifications")
    assert response.status_code == 200
    notifs = response.json()
    assert isinstance(notifs, list)


def test_override_and_clear_cache_endpoints(low_risk_submission):
    # First submit an application
    sub_res = client.post(
        "/api/v1/underwrite",
        json={"raw_text": low_risk_submission.raw_text, "submission_type": "text"}
    )
    assert sub_res.status_code == 200
    sub_id = sub_res.json()["submission_id"]

    # Test override
    override_res = client.post(
        "/api/v1/override",
        json={
            "submission_id": sub_id,
            "decision_type": "APPROVED",
            "comments": "Test override approval by senior UW",
            "underwriter_id": "Senior Underwriter",
        }
    )
    assert override_res.status_code == 200
    assert override_res.json()["underwriter_override"] == "APPROVED"
    assert override_res.json()["decision"] == "Underwriter Approved"

    # Test clear cache
    clear_res = client.post("/api/v1/clear-cache")
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "success"

