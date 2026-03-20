---
phase: 7
slug: voice-leading
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python3 -m pytest tests/analysis/test_voiceleading.py -x` |
| **Full suite command** | `python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/analysis/test_voiceleading.py -x`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| VLEAD-01 | 07-01 | 1 | VLEAD-01 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_parallel_fifths -x` | ❌ W0 | ⬜ pending |
| VLEAD-02 | 07-01 | 1 | VLEAD-02 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_parallel_octaves -x` | ❌ W0 | ⬜ pending |
| VLEAD-03 | 07-01 | 1 | VLEAD-03 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_voice_crossing -x` | ❌ W0 | ⬜ pending |
| VLEAD-04 | 07-01 | 1 | VLEAD-04 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_voice_overlap -x` | ❌ W0 | ⬜ pending |
| VLEAD-06 | 07-01 | 1 | VLEAD-06 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_large_leaps -x` | ❌ W0 | ⬜ pending |
| VLEAD-05 | 07-02 | 2 | VLEAD-05 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_smooth_voice_leading -x` | ❌ W0 | ⬜ pending |
| VLEAD-07 | 07-02 | 2 | VLEAD-07 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_check_voice_leading -x` | ❌ W0 | ⬜ pending |
| VLEAD-08 | 07-02 | 2 | VLEAD-08 | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_generate_inner_voices -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/analysis/test_voiceleading.py` — stubs for VLEAD-01 through VLEAD-08

*No framework install needed — pytest already configured in pyproject.toml.*

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
