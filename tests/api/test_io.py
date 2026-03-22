"""Integration tests for file I/O endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_export_musicxml_content_type(client: TestClient) -> None:
    r = client.post("/v1/io/export-musicxml", json={"phrase": "q c4 d4 e4"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")


def test_export_import_musicxml_roundtrip(client: TestClient) -> None:
    # Export a phrase
    r = client.post("/v1/io/export-musicxml", json={"phrase": "q c4 d4 e4"})
    assert r.status_code == 200
    xml_bytes = r.content

    # Import it back
    r2 = client.post(
        "/v1/io/import-musicxml",
        files={"file": ("test.xml", xml_bytes, "application/xml")},
    )
    assert r2.status_code == 200
    data = r2.json()
    # Either phrase (single) or voices (score) should be present
    assert "phrase" in data or "voices" in data


def test_import_musicxml_invalid(client: TestClient) -> None:
    # Invalid XML triggers xml.etree ParseError -- route propagates as 500
    import pytest
    from xml.etree.ElementTree import ParseError
    with pytest.raises(ParseError):
        client.post(
            "/v1/io/import-musicxml",
            files={"file": ("bad.xml", b"not xml data", "application/xml")},
        )


def test_export_midi_if_available(client: TestClient) -> None:
    """Test MIDI export -- only runs if mido is installed."""
    try:
        import mido  # noqa: F401
    except ImportError:
        return  # skip if mido not available

    r = client.post("/v1/io/export-midi", json={"phrase": "q c4 d4 e4", "tempo": 120})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/octet-stream"
