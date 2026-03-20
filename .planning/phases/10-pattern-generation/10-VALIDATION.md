---
phase: 10
slug: pattern-generation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python3 -m pytest tests/patterns/ -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/patterns/ -x -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| RHYT-06 | 10-01 | 1 | RHYT-06 | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_euclidean_rhythm -x` | ❌ W0 | ⬜ pending |
| PATT-01 | 10-01 | 1 | PATT-01 | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_isorhythm -x` | ❌ W0 | ⬜ pending |
| PATT-02 | 10-01 | 1 | PATT-02 | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_ostinato -x` | ❌ W0 | ⬜ pending |
| PATT-03 | 10-02 | 2 | PATT-03 | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_apply_rhythm -x` | ❌ W0 | ⬜ pending |
| PATT-04 | 10-01 | 1 | PATT-04 | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_binary_rhythm -x` | ❌ W0 | ⬜ pending |
| PATT-05 | 10-02 | 2 | PATT-05 | unit | `python3 -m pytest tests/patterns/test_multivoice.py::test_rhythmic_canon -x` | ❌ W0 | ⬜ pending |
| PATT-06 | 10-02 | 2 | PATT-06 | unit | `python3 -m pytest tests/patterns/test_multivoice.py::test_hocket -x` | ❌ W0 | ⬜ pending |
| PATT-07 | 10-01 | 1 | PATT-07 | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_accent_pattern -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/patterns/__init__.py` — test package init
- [ ] `tests/patterns/conftest.py` — shared fixtures (sample Phrase, Duration tuples, quarter note helper)
- [ ] `tests/patterns/test_rhythm.py` — stubs for RHYT-06, PATT-03, PATT-04
- [ ] `tests/patterns/test_melodic.py` — stubs for PATT-01, PATT-02, PATT-07
- [ ] `tests/patterns/test_multivoice.py` — stubs for PATT-05, PATT-06

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
