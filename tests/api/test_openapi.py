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


def test_openapi_has_analysis_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/analysis/detect-key" in schema["paths"]
    assert "/v1/analysis/identify-chord" in schema["paths"]
    assert "/v1/analysis/ambitus" in schema["paths"]


def test_openapi_has_batch_ops_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/batch-ops/crescendo" in schema["paths"]
    assert "/v1/batch-ops/set-articulation-nth" in schema["paths"]


def test_openapi_has_counterpoint_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/counterpoint/generate-first-species" in schema["paths"]
    assert "/v1/counterpoint/generate-first-species/async" in schema["paths"]
    assert "/v1/counterpoint/check-counterpoint" in schema["paths"]


def test_openapi_has_settheory_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/settheory/prime-form" in schema["paths"]
    assert "/v1/settheory/forte-number" in schema["paths"]


def test_openapi_has_patterns_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/patterns/euclidean-rhythm" in schema["paths"]
    assert "/v1/patterns/ostinato" in schema["paths"]


def test_openapi_has_composition_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/composition/markov-generate" in schema["paths"]
    assert "/v1/composition/random-walk" in schema["paths"]


def test_openapi_has_io_paths(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/io/import-musicxml" in schema["paths"]
    assert "/v1/io/export-musicxml" in schema["paths"]


def test_openapi_has_jobs_path(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/jobs/{job_id}" in schema["paths"]


def test_openapi_has_batch_path(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/batch" in schema["paths"]


def test_openapi_title(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Cadenza API"
