---
phase: 13
slug: api-completion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x with httpx TestClient |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python -m pytest tests/api/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/api/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| API-06 | 13-01 | 1 | API-06 | integration | `python -m pytest tests/api/test_jobs.py -x` | ❌ W0 | ⬜ pending |
| API-09 | 13-02 | 2 | API-09 | integration | `python -m pytest tests/api/test_batch.py -x` | ❌ W0 | ⬜ pending |
| routes-analysis | 13-01 | 1 | — | integration | `python -m pytest tests/api/test_analysis.py -x` | ❌ W0 | ⬜ pending |
| routes-counterpoint | 13-01 | 1 | API-06 | integration | `python -m pytest tests/api/test_counterpoint.py -x` | ❌ W0 | ⬜ pending |
| routes-settheory | 13-01 | 1 | — | integration | `python -m pytest tests/api/test_settheory.py -x` | ❌ W0 | ⬜ pending |
| routes-patterns | 13-01 | 1 | — | integration | `python -m pytest tests/api/test_patterns.py -x` | ❌ W0 | ⬜ pending |
| routes-composition | 13-01 | 1 | — | integration | `python -m pytest tests/api/test_composition.py -x` | ❌ W0 | ⬜ pending |
| routes-io | 13-01 | 1 | — | integration | `python -m pytest tests/api/test_io.py -x` | ❌ W0 | ⬜ pending |
| routes-batch-ops | 13-02 | 2 | — | integration | `python -m pytest tests/api/test_batch_ops.py -x` | ❌ W0 | ⬜ pending |
| openapi | 13-02 | 2 | — | smoke | `python -m pytest tests/api/test_openapi.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/api/test_analysis.py` — stubs for analysis route endpoints
- [ ] `tests/api/test_batch_ops.py` — stubs for batch_ops route endpoints
- [ ] `tests/api/test_counterpoint.py` — stubs for counterpoint sync + async endpoints
- [ ] `tests/api/test_settheory.py` — stubs for set theory route endpoints
- [ ] `tests/api/test_patterns.py` — stubs for patterns route endpoints
- [ ] `tests/api/test_composition.py` — stubs for composition route endpoints
- [ ] `tests/api/test_io.py` — stubs for I/O import/export endpoints
- [ ] `tests/api/test_jobs.py` — stubs for job polling, TTL, 410 Gone
- [ ] `tests/api/test_batch.py` — stubs for batch dispatch endpoint (API-09)
- [ ] `tests/api/test_openapi.py` — stubs asserting new endpoint paths in OpenAPI schema

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
