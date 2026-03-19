"""Shared fixtures for API tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cadenza.api import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient for the Cadenza API."""
    app = create_app()
    return TestClient(app)
