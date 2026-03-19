---
phase: 4
slug: rest-api-v1
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x + httpx 0.27+ |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/api/ -x -q` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/api/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| API-08 | 04-01 | 1 | API-08 | integration | `pytest tests/api/test_health.py -x` | ❌ W0 | ⬜ pending |
| API-04 | 04-01 | 1 | API-04 | integration | `pytest tests/api/ -k "v1" -x` | ❌ W0 | ⬜ pending |
| API-07 | 04-01 | 1 | API-07 | integration | `pytest tests/api/test_errors.py -x` | ❌ W0 | ⬜ pending |
| API-01 | 04-02 | 2 | API-01 | integration | `pytest tests/api/test_transforms.py tests/api/test_theory.py -x` | ❌ W0 | ⬜ pending |
| API-02 | 04-02 | 2 | API-02 | integration | `pytest tests/api/test_transforms.py -k "cn_input" -x` | ❌ W0 | ⬜ pending |
| API-03 | 04-02 | 2 | API-03 | integration | `pytest tests/api/test_transforms.py -k "response_format" -x` | ❌ W0 | ⬜ pending |
| API-05 | 04-02 | 2 | API-05 | integration | `pytest tests/api/test_openapi.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All API test files must be created before implementation tasks run:

- [ ] `tests/api/__init__.py` — test package init
- [ ] `tests/api/conftest.py` — TestClient fixture (`client` fixture using `create_app()`)
- [ ] `tests/api/test_health.py` — stubs for API-08
- [ ] `tests/api/test_transforms.py` — stubs for API-01, API-02, API-03, API-04
- [ ] `tests/api/test_theory.py` — stubs for API-01, API-02, API-03, API-04
- [ ] `tests/api/test_errors.py` — stubs for API-07
- [ ] `tests/api/test_openapi.py` — stubs for API-05
- [ ] `pyproject.toml` updated — `httpx>=0.27` in dev deps, `fastapi>=0.115,<1.0` and `uvicorn[standard]>=0.30` in runtime deps

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OpenAPI docs are human-readable and accurate | API-05 | Content quality is subjective | Open `http://localhost:8000/docs` after starting server; verify all endpoints listed with meaningful descriptions and example values |
| Server starts and responds to Dorico-style calls | API-01 | E2E DAW integration | Run `uvicorn cadenza.api:app`; send a POST with curl or httpie; verify response is a valid CN string usable in Dorico |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
