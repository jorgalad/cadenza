---
phase: 3
slug: theory-libraries
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x + hypothesis 6.x |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/ -x --timeout=30` |
| **Full suite command** | `pytest tests/ -v --cov=cadenza --cov-report=term-missing` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x --timeout=30`
- **After every plan wave:** Run `pytest tests/ -v --cov=cadenza --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| SCAL-01 | 03-01 | 1 | SCAL-01 | unit | `pytest tests/theory/test_scales.py::test_major_minor_scales -x` | ❌ W0 | ⬜ pending |
| SCAL-02 | 03-01 | 1 | SCAL-02 | unit | `pytest tests/theory/test_scales.py::test_church_modes -x` | ❌ W0 | ⬜ pending |
| SCAL-03 | 03-01 | 1 | SCAL-03 | unit | `pytest tests/theory/test_scales.py::test_pentatonic -x` | ❌ W0 | ⬜ pending |
| SCAL-04 | 03-01 | 1 | SCAL-04 | unit | `pytest tests/theory/test_scales.py::test_blues -x` | ❌ W0 | ⬜ pending |
| SCAL-05 | 03-01 | 1 | SCAL-05 | unit | `pytest tests/theory/test_scales.py::test_symmetric_scales -x` | ❌ W0 | ⬜ pending |
| SCAL-06 | 03-01 | 1 | SCAL-06 | unit | `pytest tests/theory/test_scales.py::test_bebop -x` | ❌ W0 | ⬜ pending |
| SCAL-07 | 03-01 | 1 | SCAL-07 | unit | `pytest tests/theory/test_scales.py::test_non_western -x` | ❌ W0 | ⬜ pending |
| SCAL-08 | 03-01 | 1 | SCAL-08 | unit | `pytest tests/theory/test_scales.py::test_custom_scale -x` | ❌ W0 | ⬜ pending |
| SCAL-09 | 03-01 | 1 | SCAL-09 | unit | `pytest tests/theory/test_scales.py::test_get_scale -x` | ❌ W0 | ⬜ pending |
| SCAL-10 | 03-01 | 1 | SCAL-10 | unit | `pytest tests/theory/test_scales.py::test_identify_scale -x` | ❌ W0 | ⬜ pending |
| SCAL-11 | 03-01 | 1 | SCAL-11 | unit | `pytest tests/theory/test_scales.py::test_scale_degree -x` | ❌ W0 | ⬜ pending |
| SCAL-12 | 03-01 | 1 | SCAL-12 | unit | `pytest tests/theory/test_scales.py::test_relative_parallel -x` | ❌ W0 | ⬜ pending |
| CHRD-01 | 03-02 | 2 | CHRD-01 | unit | `pytest tests/theory/test_chords.py::test_triads -x` | ❌ W0 | ⬜ pending |
| CHRD-02 | 03-02 | 2 | CHRD-02 | unit | `pytest tests/theory/test_chords.py::test_seventh_chords -x` | ❌ W0 | ⬜ pending |
| CHRD-03 | 03-02 | 2 | CHRD-03 | unit | `pytest tests/theory/test_chords.py::test_extended_chords -x` | ❌ W0 | ⬜ pending |
| CHRD-04 | 03-02 | 2 | CHRD-04 | unit | `pytest tests/theory/test_chords.py::test_added_sus -x` | ❌ W0 | ⬜ pending |
| CHRD-05 | 03-02 | 2 | CHRD-05 | unit | `pytest tests/theory/test_chords.py::test_inversions -x` | ❌ W0 | ⬜ pending |
| CHRD-06 | 03-02 | 2 | CHRD-06 | unit | `pytest tests/theory/test_chords.py::test_diatonic_chords -x` | ❌ W0 | ⬜ pending |
| CHRD-07 | 03-02 | 2 | CHRD-07 | unit | `pytest tests/theory/test_chords.py::test_secondary_dominants -x` | ❌ W0 | ⬜ pending |
| CHRD-08 | 03-02 | 2 | CHRD-08 | unit | `pytest tests/theory/test_chords.py::test_aug6_neapolitan -x` | ❌ W0 | ⬜ pending |
| CHRD-09 | 03-02 | 2 | CHRD-09 | unit | `pytest tests/theory/test_chords.py::test_custom_chord -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All theory test files must be created before implementation tasks run:

- [ ] `tests/theory/__init__.py` — theory test package
- [ ] `tests/theory/test_scales.py` — stubs for SCAL-01..12
- [ ] `tests/theory/test_chords.py` — stubs for CHRD-01..09

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D dorian returns correct spelling | SCAL-02 | Canonical correctness check | Call `get_scale(Pitch('d','n',4), 'dorian')` and verify all 7 pitches are natural (D,E,F,G,A,B,C) with no accidentals |
| Non-Western scale spellings are musically reasonable | SCAL-07 | Subjective correctness of 12-TET approximations | Inspect Hijaz, Persian, Hungarian minor output and verify accidentals match standard textbook representations |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
