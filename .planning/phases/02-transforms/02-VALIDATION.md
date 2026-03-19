---
phase: 2
slug: transforms
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x + hypothesis 6.x |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/ -x --timeout=30` |
| **Full suite command** | `pytest tests/ -v --cov=cadenza --cov-report=term-missing` |
| **Estimated runtime** | ~20 seconds |

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
| PTCH-01 | 02-01 | 1 | PTCH-01 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_chromatic_transpose -x` | ❌ W0 | ⬜ pending |
| PTCH-02 | 02-01 | 1 | PTCH-02 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_diatonic_transpose_stub -x` | ❌ W0 | ⬜ pending |
| PTCH-03 | 02-01 | 1 | PTCH-03 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_transpose_spelling -x` | ❌ W0 | ⬜ pending |
| PTCH-04 | 02-01 | 1 | PTCH-04 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_invert -x` | ❌ W0 | ⬜ pending |
| PTCH-05 | 02-01 | 1 | PTCH-05 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_invert_axis -x` | ❌ W0 | ⬜ pending |
| PTCH-06 | 02-01 | 1 | PTCH-06 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_interval_between -x` | ❌ W0 | ⬜ pending |
| PTCH-07 | 02-01 | 1 | PTCH-07 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_pitch_conversions -x` | ❌ W0 | ⬜ pending |
| PTCH-08 | 02-01 | 1 | PTCH-08 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_enharmonic_stub -x` | ❌ W0 | ⬜ pending |
| PTCH-09 | 02-01 | 1 | PTCH-09 | unit | `pytest tests/transforms/test_pitch_transforms.py::test_normalize_stub -x` | ❌ W0 | ⬜ pending |
| RHYT-01 | 02-02 | 1 | RHYT-01 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_augment -x` | ❌ W0 | ⬜ pending |
| RHYT-02 | 02-02 | 1 | RHYT-02 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_diminish -x` | ❌ W0 | ⬜ pending |
| RHYT-03 | 02-02 | 1 | RHYT-03 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_rhythm_retrograde -x` | ❌ W0 | ⬜ pending |
| RHYT-04 | 02-02 | 1 | RHYT-04 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_rotate_rhythm -x` | ❌ W0 | ⬜ pending |
| RHYT-05 | 02-02 | 1 | RHYT-05 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_metric_modulation -x` | ❌ W0 | ⬜ pending |
| RHYT-07 | 02-02 | 1 | RHYT-07 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_quantize -x` | ❌ W0 | ⬜ pending |
| RHYT-08 | 02-02 | 1 | RHYT-08 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_swing -x` | ❌ W0 | ⬜ pending |
| RHYT-09 | 02-02 | 1 | RHYT-09 | unit | `pytest tests/transforms/test_rhythm_transforms.py::test_rest_transforms -x` | ❌ W0 | ⬜ pending |
| MELO-01 | 02-03 | 2 | MELO-01 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_pitch_retrograde -x` | ❌ W0 | ⬜ pending |
| MELO-02 | 02-03 | 2 | MELO-02 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_retrograde_inversion -x` | ❌ W0 | ⬜ pending |
| MELO-03 | 02-03 | 2 | MELO-03 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_full_retrograde -x` | ❌ W0 | ⬜ pending |
| MELO-04 | 02-03 | 2 | MELO-04 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_rotation -x` | ❌ W0 | ⬜ pending |
| MELO-05 | 02-03 | 2 | MELO-05 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_interpolation -x` | ❌ W0 | ⬜ pending |
| MELO-06 | 02-03 | 2 | MELO-06 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_omission -x` | ❌ W0 | ⬜ pending |
| MELO-07 | 02-03 | 2 | MELO-07 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_mirror -x` | ❌ W0 | ⬜ pending |
| MELO-08 | 02-03 | 2 | MELO-08 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_fragmentation -x` | ❌ W0 | ⬜ pending |
| MELO-09 | 02-03 | 2 | MELO-09 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_concatenation -x` | ❌ W0 | ⬜ pending |
| MELO-10 | 02-03 | 2 | MELO-10 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_interleave -x` | ❌ W0 | ⬜ pending |
| MELO-11 | 02-03 | 2 | MELO-11 | unit | `pytest tests/transforms/test_melodic_transforms.py::test_permutation -x` | ❌ W0 | ⬜ pending |
| MELO-12 | 02-03 | 2 | MELO-12 | unit+property | `pytest tests/transforms/test_melodic_transforms.py::test_chaining -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All transform test files must be created before implementation tasks run:

- [ ] `tests/transforms/__init__.py` — transforms test package
- [ ] `tests/transforms/test_pitch_transforms.py` — stubs for PTCH-01..09
- [ ] `tests/transforms/test_rhythm_transforms.py` — stubs for RHYT-01..05, RHYT-07..09
- [ ] `tests/transforms/test_melodic_transforms.py` — stubs for MELO-01..12

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Enharmonic spelling feels musically correct after transposition | PTCH-03 | Subjective correctness of note spelling in context | Transpose C major scale up a minor third; verify output is Eb, F, G, Ab, Bb, C, D (not D#, E#, F#, G#, A#, B#, C#) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
