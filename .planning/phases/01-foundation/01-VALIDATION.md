---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x + hypothesis 6.x |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/ -x --timeout=30` |
| **Full suite command** | `pytest tests/ -v --cov=cadenza --cov-report=term-missing` |
| **Estimated runtime** | ~15 seconds |

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
| CORE-01 | 01-01 | 1 | CORE-01 | unit | `pytest tests/core/test_pitch.py -x` | ❌ W0 | ⬜ pending |
| CORE-02 | 01-01 | 1 | CORE-02 | unit | `pytest tests/core/test_pitch.py::test_enharmonic -x` | ❌ W0 | ⬜ pending |
| CORE-03 | 01-01 | 1 | CORE-03 | unit | `pytest tests/core/test_duration.py -x` | ❌ W0 | ⬜ pending |
| CORE-04 | 01-01 | 1 | CORE-04 | unit | `pytest tests/core/test_interval.py -x` | ❌ W0 | ⬜ pending |
| CORE-05 | 01-01 | 1 | CORE-05 | unit | `pytest tests/core/test_note.py -x` | ❌ W0 | ⬜ pending |
| CORE-06 | 01-01 | 1 | CORE-06 | unit | `pytest tests/core/test_note.py::test_rest -x` | ❌ W0 | ⬜ pending |
| CORE-07 | 01-01 | 1 | CORE-07 | unit | `pytest tests/core/test_phrase.py -x` | ❌ W0 | ⬜ pending |
| CORE-08 | 01-01 | 1 | CORE-08 | unit | `pytest tests/core/test_score.py -x` | ❌ W0 | ⬜ pending |
| CORE-09 | 01-01 | 1 | CORE-09 | unit+property | `pytest tests/core/test_json_codec.py -x` | ❌ W0 | ⬜ pending |
| CORE-10 | 01-01 | 1 | CORE-10 | unit+property | `pytest tests/core/test_pitch.py::test_hash -x` | ❌ W0 | ⬜ pending |
| NOTA-01 | 01-02 | 2 | NOTA-01 | unit+property | `pytest tests/omn/test_parser.py -x` | ❌ W0 | ⬜ pending |
| NOTA-02 | 01-02 | 2 | NOTA-02 | property | `pytest tests/omn/test_round_trip.py -x` | ❌ W0 | ⬜ pending |
| NOTA-03 | 01-02 | 2 | NOTA-03 | unit | `pytest tests/omn/test_tokenizer.py::test_durations -x` | ❌ W0 | ⬜ pending |
| NOTA-04 | 01-02 | 2 | NOTA-04 | unit | `pytest tests/omn/test_parser.py::test_rests -x` | ❌ W0 | ⬜ pending |
| NOTA-05 | 01-02 | 2 | NOTA-05 | unit | `pytest tests/omn/test_parser.py::test_tuplets -x` | ❌ W0 | ⬜ pending |
| NOTA-06 | 01-02 | 2 | NOTA-06 | unit | `pytest tests/omn/test_parser.py::test_dynamics -x` | ❌ W0 | ⬜ pending |
| NOTA-07 | 01-02 | 2 | NOTA-07 | unit | `pytest tests/omn/test_parser.py::test_articulations -x` | ❌ W0 | ⬜ pending |
| NOTA-12 | 01-02 | 2 | NOTA-12 | unit | `pytest tests/omn/test_parser.py::test_error_messages -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test infrastructure must be created from scratch (greenfield):

- [ ] `pyproject.toml` — project config with pytest/hypothesis/ruff/mypy dev deps
- [ ] `tests/__init__.py` — test package
- [ ] `tests/conftest.py` — shared fixtures (sample phrases, pitches, notes)
- [ ] `tests/strategies.py` — hypothesis custom strategies for Pitch, Duration, Note, Rest, Phrase
- [ ] `tests/core/__init__.py`
- [ ] `tests/core/test_pitch.py` — covers CORE-01, CORE-02, CORE-10
- [ ] `tests/core/test_duration.py` — covers CORE-03
- [ ] `tests/core/test_interval.py` — covers CORE-04
- [ ] `tests/core/test_note.py` — covers CORE-05, CORE-06
- [ ] `tests/core/test_phrase.py` — covers CORE-07
- [ ] `tests/core/test_score.py` — covers CORE-08
- [ ] `tests/core/test_json_codec.py` — covers CORE-09
- [ ] `tests/omn/__init__.py`
- [ ] `tests/omn/test_tokenizer.py` — covers NOTA-03, NOTA-04, NOTA-05
- [ ] `tests/omn/test_parser.py` — covers NOTA-01, NOTA-04..07, NOTA-12
- [ ] `tests/omn/test_serializer.py` — covers NOTA-02
- [ ] `tests/omn/test_round_trip.py` — covers NOTA-02 (property-based)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OMN sticky carry-forward feels correct | NOTA-01 | Subjective correctness of compact notation | Manually inspect serialized output of a multi-note phrase with shared dynamics |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
