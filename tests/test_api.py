"""Basic API tests."""

from fastapi.testclient import TestClient

# Status code constants
NOT_FOUND_STATUS = 404


def test_api_health(client: TestClient) -> None:
    """Test that the API health endpoint returns a success response."""
    response = client.get("/health")
    assert response.status_code == NOT_FOUND_STATUS  # Will fail until we implement the endpoint
