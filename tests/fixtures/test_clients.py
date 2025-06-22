"""
Test client fixtures for the project.

This file contains fixtures for creating TestClient instances for testing the application.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def test_client(auth_headers):
    """
    Create a TestClient instance with authentication headers.

    This is the primary client fixture that should be used by all tests
    that need to make HTTP requests to the application.

    Args:
        auth_headers: Authentication headers from the auth_headers fixture.

    Returns:
        A TestClient instance with authentication headers.
    """
    with TestClient(app) as client:
        client.headers.update(auth_headers)
        yield client
