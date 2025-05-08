"""Configuration for pytest."""

import pytest
from fastapi.testclient import TestClient

from parkings_ch_api import create_app


@pytest.fixture
def app() -> object:
    """Create a test instance of the application."""
    return create_app()


@pytest.fixture
def client(app: object) -> TestClient:
    """Create a test client for the application."""
    return TestClient(app)
