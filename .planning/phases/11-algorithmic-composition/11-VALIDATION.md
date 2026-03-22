---
phase: 11
slug: algorithmic-composition
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `pytest tests/composition/ -x -q` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/composition/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| ALGO-01 | 11-01 | 1 | ALGO-01 | unit | `pytest tests/composition/test_markov.py::test_first_order_markov -x` | ❌ W0 | ⬜ pending |
| ALGO-02 | 11-01 | 1 | ALGO-02 | unit | `pytest tests/composition/test_markov.py::test_higher_order_markov -x` | ❌ W0 | ⬜ pending |
| ALGO-03 | 11-01 | 1 | ALGO-03 | unit | `pytest tests/composition/test_lsystem.py::test_lsystem_expansion -x` | ❌ W0 | ⬜ pending |
| ALGO-04 | 11-02 | 2 | ALGO-04 | unit | `pytest tests/composition/test_stochastic.py::test_probabilistic_melody -x` | ❌ W0 | ⬜ pending |
| ALGO-05 | 11-02 | 2 | ALGO-05 | unit | `pytest tests/composition/test_stochastic.py::test_tendency_mask -x` | ❌ W0 | ⬜ pending |
| ALGO-06 | 11-02 | 2 | ALGO-06 | unit | `pytest tests/composition/test_stochastic.py::test_random_walk -x` | ❌ W0 | ⬜ pending |
| ALGO-07 | 11-02 | 2 | ALGO-07 | unit | `pytest tests/composition/test_variation.py::test_generate_variations -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/composition/__init__.py` — test package init
- [ ] `tests/composition/conftest.py` — shared fixtures (sample phrases, scales, durations)
- [ ] `tests/composition/test_markov.py` — stubs for ALGO-01, ALGO-02
- [ ] `tests/composition/test_lsystem.py` — stubs for ALGO-03
- [ ] `tests/composition/test_stochastic.py` — stubs for ALGO-04, ALGO-05, ALGO-06
- [ ] `tests/composition/test_variation.py` — stubs for ALGO-07

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
