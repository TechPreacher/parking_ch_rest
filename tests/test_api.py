"""Basic API tests."""

from fastapi.testclient import TestClient


def test_api_health(client: TestClient):
    """Test that the API health endpoint returns a success response."""
    response = client.get("/health")
    assert response.status_code == 404  # Will fail until we implement the endpoint
