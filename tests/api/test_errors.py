"""Tests for API error handlers (API-07)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cadenza.api.errors import CadenzaAPIError
from cadenza.cn.errors import ParseError


def test_cadenza_api_error_handler(client: TestClient) -> None:
    """CadenzaAPIError produces 422 JSON with error code, message, and input."""

    @client.app.get("/test-error-cadenza")  # type: ignore[union-attr]
    def _raise_cadenza_error() -> None:
        raise CadenzaAPIError("INVALID_PITCH", "test msg", "xb4")

    response = client.get("/test-error-cadenza")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "INVALID_PITCH"
    assert data["message"] == "test msg"
    assert data["input"] == "xb4"


def test_parse_error_handler(client: TestClient) -> None:
    """ParseError produces 422 JSON with INVALID_CN error code."""

    @client.app.get("/test-error-parse")  # type: ignore[union-attr]
    def _raise_parse_error() -> None:
        raise ParseError(message="bad input", position=0)

    response = client.get("/test-error-parse")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "INVALID_CN"
    assert "bad input" in data["message"]


def test_value_error_handler(client: TestClient) -> None:
    """ValueError produces 422 JSON with INVALID_INPUT error code."""

    @client.app.get("/test-error-value")  # type: ignore[union-attr]
    def _raise_value_error() -> None:
        raise ValueError("bad value")

    response = client.get("/test-error-value")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "INVALID_INPUT"
    assert data["message"] == "bad value"
