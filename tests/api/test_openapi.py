"""OpenAPI schema verification tests (API-05)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_openapi_schema_accessible(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()


def test_openapi_has_transform_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/transform/chromatic-transpose" in schema["paths"]
    assert "/v1/transform/pitch-retrograde" in schema["paths"]
    assert "/v1/transform/augment" in schema["paths"]
    assert "/v1/transform/fragment" in schema["paths"]


def test_openapi_has_theory_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/theory/scale" in schema["paths"]
    assert "/v1/theory/chord" in schema["paths"]
    assert "/v1/theory/diatonic-chords" in schema["paths"]


def test_openapi_has_health_path(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/health" in schema["paths"]


def test_all_endpoints_have_summary(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    for path, methods in schema["paths"].items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                assert "summary" in details, f"Missing summary on {method.upper()} {path}"


def test_openapi_title(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Cadenza API"
