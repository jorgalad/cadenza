"""Integration tests for analysis endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_detect_key(client: TestClient) -> None:
    r = client.post("/v1/analysis/detect-key", json={"phrase": "q c4 e4 g4 c5"})
    assert r.status_code == 200
    data = r.json()
    assert "root" in data
    assert "mode" in data
    assert "confidence" in data


def test_identify_chord(client: TestClient) -> None:
    r = client.post("/v1/analysis/identify-chord", json={"pitches": "c4 e4 g4"})
    assert r.status_code == 200
    data = r.json()
    assert "root" in data
    assert "symbol" in data


def test_ambitus(client: TestClient) -> None:
    r = client.post("/v1/analysis/ambitus", json={"phrase": "q c4 g5 e4"})
    assert r.status_code == 200
    data = r.json()
    assert "low" in data
    assert "high" in data


def test_melodic_contour(client: TestClient) -> None:
    r = client.post("/v1/analysis/melodic-contour", json={"phrase": "q c4 d4 e4"})
    assert r.status_code == 200
    data = r.json()
    assert "contour" in data
    assert isinstance(data["contour"], list)


def test_complexity_score(client: TestClient) -> None:
    r = client.post("/v1/analysis/complexity-score", json={"phrase": "q c4 d4 e4"})
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert isinstance(data["score"], float)


def test_check_voice_leading(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/check-voice-leading",
        json={"voices": ["w c4 d4 e4 f4", "w e4 f4 g4 a4"]},
    )
    assert r.status_code == 200
    data = r.json()
    assert "violations" in data


def test_smooth_voice_leading(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/smooth-voice-leading",
        json={"chord1": "c4 e4 g4", "chord2": "d4 f4 a4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "phrase" in data


def test_phrase_similarity(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/phrase-similarity",
        json={"phrase": "q c4 d4 e4", "phrase2": "q c4 d4 f4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "similarity" in data
    assert isinstance(data["similarity"], float)


def test_find_motifs(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/find-motifs",
        json={"phrase": "q c4 d4 e4 c4 d4 e4", "min_length": 2},
    )
    assert r.status_code == 200
    data = r.json()
    assert "motifs" in data


def test_pitch_class_histogram(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/pitch-class-histogram",
        json={"phrase": "q c4 d4 e4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "histogram" in data


def test_interval_sequence(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/interval-sequence",
        json={"phrase": "q c4 d4 e4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "intervals" in data
    assert isinstance(data["intervals"], list)


def test_rhythmic_density(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/rhythmic-density",
        json={"phrase": "q c4 e d4 e4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "density" in data


def test_roman_numeral(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/roman-numeral",
        json={"pitches": "c4 e4 g4", "key_root": "c4", "key_mode": "major"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "numeral" in data
    assert "function" in data


def test_detect_modulations(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/detect-modulations",
        json={"phrase": "q c4 d4 e4 f4 g4 a4 b4 c5", "window": 4},
    )
    assert r.status_code == 200
    data = r.json()
    assert "modulations" in data
    assert isinstance(data["modulations"], list)


def test_detect_sequence(client: TestClient) -> None:
    r = client.post(
        "/v1/analysis/detect-sequence",
        json={"phrase": "q c4 d4 e4", "phrase2": "q d4 e4 f4"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "matches" in data
