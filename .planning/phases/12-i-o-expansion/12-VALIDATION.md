---
phase: 12
slug: i-o-expansion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `python3 -m pytest tests/io/ -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -x -q` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/io/ -x -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| NOTA-08 | 12-01 | 1 | NOTA-08 | unit+integration | `python3 -m pytest tests/io/test_musicxml_import.py -x` | ❌ W0 | ⬜ pending |
| NOTA-09 | 12-01 | 1 | NOTA-09 | unit+integration | `python3 -m pytest tests/io/test_musicxml_export.py tests/io/test_roundtrip.py::test_musicxml_roundtrip -x` | ❌ W0 | ⬜ pending |
| NOTA-10 | 12-02 | 2 | NOTA-10 | unit | `python3 -m pytest tests/io/test_midi_import.py -x` | ❌ W0 | ⬜ pending |
| NOTA-11 | 12-02 | 2 | NOTA-11 | unit+integration | `python3 -m pytest tests/io/test_midi_export.py tests/io/test_roundtrip.py::test_midi_roundtrip -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files must be created before implementation tasks run:

- [ ] `tests/io/__init__.py` — test package init
- [ ] `tests/io/conftest.py` — shared fixtures (sample MusicXML strings, in-memory mido MidiFile helpers)
- [ ] `tests/io/test_musicxml_import.py` — stubs for NOTA-08
- [ ] `tests/io/test_musicxml_export.py` — stubs for NOTA-09
- [ ] `tests/io/test_midi_import.py` — stubs for NOTA-10
- [ ] `tests/io/test_midi_export.py` — stubs for NOTA-11
- [ ] `tests/io/test_roundtrip.py` — roundtrip stubs for both formats
- [ ] `mido` added to `pyproject.toml` `[project.optional-dependencies]` as `io` group

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Exported MusicXML opens correctly in Dorico/Sibelius | NOTA-09 | Requires notation software to verify | Export a test phrase; open in Dorico or Sibelius; verify pitches, rhythms, and dynamics display correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
