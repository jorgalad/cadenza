---
phase: 12-i-o-expansion
plan: 01
subsystem: io
tags: [musicxml, xml, import, export, duration-conversion, dynamics]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "Pitch, Duration, Note, Rest, Phrase, Score core types"
  - phase: 02-transforms
    provides: "from_midi pitch conversion utility"
provides:
  - "cadenza.io package with shared I/O infrastructure"
  - "import_musicxml: MusicXML file -> Phrase/Score with warnings"
  - "export_musicxml: Phrase/Score -> valid MusicXML 4.0 file"
  - "ImportWarning frozen dataclass for tracking unsupported elements"
  - "Duration conversion utilities (fraction <-> MusicXML divisions)"
  - "Dynamic-velocity mapping (8-level table)"
affects: [12-02-midi-io]

# Tech tracking
tech-stack:
  added: ["xml.etree.ElementTree (stdlib)"]
  patterns: ["ImportWarning for non-fatal import issues", "fraction_to_best_duration for CN base inference", "compute_divisions with prime-factor validation", "sticky dynamics tracking"]

key-files:
  created:
    - src/cadenza/io/__init__.py
    - src/cadenza/io/_warnings.py
    - src/cadenza/io/_duration_conv.py
    - src/cadenza/io/_dynamics_map.py
    - src/cadenza/io/musicxml.py
    - tests/io/__init__.py
    - tests/io/conftest.py
    - tests/io/test_musicxml_import.py
    - tests/io/test_musicxml_export.py
    - tests/io/test_roundtrip.py
  modified:
    - pyproject.toml

key-decisions:
  - "Prime-factor validation (2,3,5 only) for MusicXML divisions rejects non-standard durations like 1/7"
  - "Sticky dynamics in import: last seen dynamic applies to subsequent notes until changed"
  - "4/4 measure splitting in export with automatic tie generation at measure boundaries"
  - "xml.etree.ElementTree (stdlib) for zero-dependency MusicXML handling"

patterns-established:
  - "ImportWarning pattern: frozen dataclass with element/position/message for non-fatal import issues"
  - "Shared _duration_conv/_dynamics_map utilities reusable by MIDI plan"
  - "TDD RED/GREEN workflow: stub files -> failing tests -> implementation"

requirements-completed: [NOTA-08, NOTA-09]

# Metrics
duration: 6min
completed: 2026-03-22
---

# Phase 12 Plan 01: MusicXML I/O Summary

**MusicXML import/export via stdlib xml.etree.ElementTree with shared duration conversion, dynamics mapping, and ImportWarning infrastructure for MIDI reuse**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-22T19:45:57Z
- **Completed:** 2026-03-22T19:51:54Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- MusicXML import handles pitches, durations, dynamics, articulations, rests, tied notes (including 3+ chains), multi-part scores, and varying divisions
- MusicXML export produces valid XML 4.0 with 4/4 measures, automatic ties at measure boundaries, dynamic directions, and articulation notations
- Roundtrip verified: export then import preserves pitches, durations, dynamics, and Score voice names
- Shared infrastructure (ImportWarning, _duration_conv, _dynamics_map) ready for MIDI plan reuse

## Task Commits

Each task was committed atomically:

1. **Task 1: Shared I/O infrastructure + MusicXML import**
   - `b3ab4cc` (test: RED phase - failing tests)
   - `cda5856` (feat: GREEN phase - implementation)
2. **Task 2: MusicXML export + roundtrip tests**
   - `de1ff94` (test: RED phase - failing tests)
   - `d191c9a` (feat: GREEN phase - implementation)

## Files Created/Modified
- `src/cadenza/io/__init__.py` - Package init re-exporting import_musicxml, export_musicxml, ImportWarning
- `src/cadenza/io/_warnings.py` - ImportWarning frozen dataclass
- `src/cadenza/io/_duration_conv.py` - Fraction <-> MusicXML divisions conversion, fraction_to_best_duration, compute_divisions
- `src/cadenza/io/_dynamics_map.py` - 8-level dynamic <-> velocity mapping table and lookup functions
- `src/cadenza/io/musicxml.py` - import_musicxml and export_musicxml implementations
- `tests/io/__init__.py` - Test package init
- `tests/io/conftest.py` - Shared MusicXML fixtures (9 XML templates, write_xml helper)
- `tests/io/test_musicxml_import.py` - 20 import tests covering all scenarios
- `tests/io/test_musicxml_export.py` - 11 export tests covering XML validity, pitch, duration, dynamics, articulations, multi-part, measures
- `tests/io/test_roundtrip.py` - 3 roundtrip tests (pitch/duration, dynamics, Score)
- `pyproject.toml` - Added io = ["mido>=1.3,<2.0"] optional dependency group

## Decisions Made
- Prime-factor validation (2, 3, 5 only) for compute_divisions rejects durations like 1/7 that have no standard musical representation
- Sticky dynamics in import mirrors CN parser pattern: last seen dynamic applies to subsequent notes
- 4/4 measure splitting with automatic tie generation at boundaries for export
- Grace notes and chord notes skipped with ImportWarning rather than raising exceptions

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added prime-factor validation for compute_divisions**
- **Found during:** Task 2 (export tests)
- **Issue:** Fraction(1,7) produced divisions=7 which technically works but represents a non-standard duration
- **Fix:** Added _validate_divisions_primes() checking only factors 2, 3, 5 are used
- **Files modified:** src/cadenza/io/_duration_conv.py
- **Verification:** test_raises_for_unrepresentable_duration passes
- **Committed in:** d191c9a (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Auto-fix necessary for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Shared utilities (_warnings, _duration_conv, _dynamics_map) ready for MIDI I/O (Plan 12-02)
- All 914 tests pass including 34 new I/O tests
- io optional dependency group added to pyproject.toml for mido

---
*Phase: 12-i-o-expansion*
*Completed: 2026-03-22*
