---
phase: 8
slug: counterpoint
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python3 -m pytest tests/counterpoint/ -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/counterpoint/ -x -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| CPTR-06 | 08-01 | 1 | CPTR-06 | unit | `python3 -m pytest tests/counterpoint/test_validation.py -x` | ❌ W0 | ⬜ pending |
| CPTR-10 | 08-01 | 1 | CPTR-10 | unit | `python3 -m pytest tests/counterpoint/test_validation.py::test_configurable_severity -x` | ❌ W0 | ⬜ pending |
| CPTR-01 | 08-01 | 1 | CPTR-01 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_first_species -x` | ❌ W0 | ⬜ pending |
| CPTR-07 | 08-01 | 1 | CPTR-07 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_above_below -x` | ❌ W0 | ⬜ pending |
| CPTR-02 | 08-02 | 2 | CPTR-02 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_second_species -x` | ❌ W0 | ⬜ pending |
| CPTR-03 | 08-02 | 2 | CPTR-03 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_third_species -x` | ❌ W0 | ⬜ pending |
| CPTR-04 | 08-02 | 2 | CPTR-04 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_fourth_species -x` | ❌ W0 | ⬜ pending |
| CPTR-05 | 08-02 | 2 | CPTR-05 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_fifth_species -x` | ❌ W0 | ⬜ pending |
| CPTR-08 | 08-02 | 2 | CPTR-08 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_free_counterpoint -x` | ❌ W0 | ⬜ pending |
| CPTR-09 | 08-02 | 2 | CPTR-09 | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_multi_voice -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/counterpoint/__init__.py` — test package init
- [ ] `tests/counterpoint/conftest.py` — shared fixtures (standard CF phrases, helper constructors)
- [ ] `tests/counterpoint/test_validation.py` — stubs for CPTR-06, CPTR-10
- [ ] `tests/counterpoint/test_generation.py` — stubs for CPTR-01 through CPTR-05, CPTR-07, CPTR-08, CPTR-09

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Generated counterpoint sounds musically satisfying | CPTR-05 | Fifth species has subjective rhythm selection | Apply to 8-note CF, verify the florid line sounds natural and varied |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
