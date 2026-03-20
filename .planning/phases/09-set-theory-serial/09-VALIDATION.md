---
phase: 9
slug: set-theory-serial
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python -m pytest tests/settheory/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/settheory/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| SETTH-01 | 09-01 | 1 | SETTH-01 | unit | `python -m pytest tests/settheory/test_pcset.py::test_prime_form -x` | ❌ W0 | ⬜ pending |
| SETTH-02 | 09-01 | 1 | SETTH-02 | unit | `python -m pytest tests/settheory/test_pcset.py::test_interval_vector -x` | ❌ W0 | ⬜ pending |
| SETTH-03 | 09-01 | 1 | SETTH-03 | unit | `python -m pytest tests/settheory/test_pcset.py::test_forte_number -x` | ❌ W0 | ⬜ pending |
| SETTH-04 | 09-01 | 1 | SETTH-04 | unit | `python -m pytest tests/settheory/test_pcset.py::test_lookup_by_forte -x` | ❌ W0 | ⬜ pending |
| SETTH-05 | 09-01 | 1 | SETTH-05 | unit | `python -m pytest tests/settheory/test_pcset.py::test_complement -x` | ❌ W0 | ⬜ pending |
| SETTH-06 | 09-01 | 1 | SETTH-06 | unit | `python -m pytest tests/settheory/test_pcset.py::test_invert_pcs -x` | ❌ W0 | ⬜ pending |
| SETTH-07 | 09-01 | 1 | SETTH-07 | unit | `python -m pytest tests/settheory/test_pcset.py::test_transpose_pcs -x` | ❌ W0 | ⬜ pending |
| SETTH-08 | 09-01 | 1 | SETTH-08 | unit | `python -m pytest tests/settheory/test_pcset.py::test_relationships -x` | ❌ W0 | ⬜ pending |
| SETTH-09 | 09-01 | 1 | SETTH-09 | unit | `python -m pytest tests/settheory/test_pcset.py::test_similarity -x` | ❌ W0 | ⬜ pending |
| SERI-01 | 09-02 | 2 | SERI-01 | unit | `python -m pytest tests/settheory/test_serial.py::test_tone_row_creation -x` | ❌ W0 | ⬜ pending |
| SERI-02 | 09-02 | 2 | SERI-02 | unit | `python -m pytest tests/settheory/test_serial.py::test_matrix -x` | ❌ W0 | ⬜ pending |
| SERI-03 | 09-02 | 2 | SERI-03 | unit | `python -m pytest tests/settheory/test_serial.py::test_row_properties -x` | ❌ W0 | ⬜ pending |
| SERI-04 | 09-02 | 2 | SERI-04 | unit | `python -m pytest tests/settheory/test_serial.py::test_realize_row -x` | ❌ W0 | ⬜ pending |
| SERI-05 | 09-02 | 2 | SERI-05 | unit | `python -m pytest tests/settheory/test_serial.py::test_segment_row -x` | ❌ W0 | ⬜ pending |
| SERI-06 | 09-02 | 2 | SERI-06 | unit | `python -m pytest tests/settheory/test_serial.py::test_derive_row -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/settheory/__init__.py` — test package init
- [ ] `tests/settheory/conftest.py` — shared fixtures (well-known PC sets, Webern row)
- [ ] `tests/settheory/test_pcset.py` — stubs for SETTH-01 through SETTH-09
- [ ] `tests/settheory/test_serial.py` — stubs for SERI-01 through SERI-06

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
