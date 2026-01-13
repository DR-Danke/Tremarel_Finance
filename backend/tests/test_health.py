"""
Health Endpoint Tests

Validates the API health check endpoint functionality.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check_returns_healthy_status() -> None:
    """Test that health endpoint returns healthy status."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "finance-tracker-api"
    print("INFO [test_health]: Health check test passed")
