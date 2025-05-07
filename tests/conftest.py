"""Configuration for pytest."""

import pytest
from fastapi.testclient import TestClient

from parkings_ch_api import create_app


@pytest.fixture
def app():
    """Create a test instance of the application."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return TestClient(app)
