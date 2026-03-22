---
phase: 12-i-o-expansion
plan: 02
subsystem: io
tags: [midi, mido, import, export, quantization, velocity, dynamics]

# Dependency graph
requires:
  - phase: 12-i-o-expansion-01
    provides: "Shared I/O infrastructure (_warnings, _duration_conv, _dynamics_map), MusicXML I/O"
provides:
  - "MIDI import with grid quantization and velocity-to-dynamic mapping"
  - "MIDI export with note_on/off events, velocity, and tempo"
  - "Full I/O re-exports from cadenza.io and cadenza top-level"
affects: [13-documentation]

# Tech tracking
tech-stack:
  added: [mido]
  patterns: [lazy-import-guard, grid-quantization, note-pairing]

key-files:
  created:
    - src/cadenza/io/midi.py
    - tests/io/test_midi_import.py
    - tests/io/test_midi_export.py
  modified:
    - src/cadenza/io/__init__.py
    - src/cadenza/__init__.py
    - tests/io/test_roundtrip.py
    - tests/io/conftest.py

key-decisions:
  - "Grid string '16'/'8' mapped to CN base via lookup table (not Duration.from_cn directly)"
  - "Flat preference by default (prefer_sharps=False) per CONTEXT.md"
  - "Conditional MIDI import in io/__init__.py and cadenza/__init__.py to keep MusicXML always available"
  - "480 ticks_per_beat for export (standard, cleanly represents all standard durations)"

patterns-established:
  - "Lazy import guard (_require_mido) for optional dependencies"
  - "Grid-based quantization with snap-to-nearest for MIDI import"

requirements-completed: [NOTA-10, NOTA-11]

# Metrics
duration: 5min
completed: 2026-03-22
---

# Phase 12 Plan 02: MIDI I/O Summary

**MIDI import/export with grid quantization, velocity-dynamic mapping, and multi-track Score support using mido**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-22T19:54:08Z
- **Completed:** 2026-03-22T19:59:08Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- MIDI import with note_on/note_off pairing, grid quantization, velocity-to-dynamic mapping, and flat preference
- MIDI export with correct note events, velocities, tempo meta messages, and rest gap handling
- Multi-track MIDI imports as Score, single-track as Phrase; exports Score as Type 1 MIDI
- Roundtrip verification: export then import preserves pitches, durations, and dynamics
- All I/O functions re-exported from cadenza.io and conditionally from cadenza top-level

## Task Commits

Each task was committed atomically:

1. **Task 1: MIDI import (RED)** - `1ca39e9` (test)
2. **Task 1: MIDI import (GREEN)** - `30759a9` (feat)
3. **Task 2: MIDI export + roundtrip (RED)** - `f1dd79b` (test)
4. **Task 2: MIDI export + roundtrip + wiring (GREEN)** - `254f583` (feat)

_TDD tasks have separate test and implementation commits._

## Files Created/Modified
- `src/cadenza/io/midi.py` - MIDI import/export with import_midi, export_midi, _snap_to_grid
- `tests/io/test_midi_import.py` - 14 tests for MIDI import
- `tests/io/test_midi_export.py` - 12 tests for MIDI export including init re-exports
- `tests/io/test_roundtrip.py` - Added 2 MIDI roundtrip tests alongside existing MusicXML roundtrips
- `src/cadenza/io/__init__.py` - Conditional re-export of import_midi, export_midi
- `src/cadenza/__init__.py` - Top-level re-exports: MusicXML always, MIDI conditionally

## Decisions Made
- Grid string ('16', '8') mapped via _GRID_TO_CN lookup table since Duration.from_cn expects CN base letters ('s', 'e'), not numeric strings
- prefer_sharps=False as default per CONTEXT.md flat-preference convention
- Conditional import in both io/__init__.py and cadenza/__init__.py: MusicXML (stdlib only) always available, MIDI requires mido
- 480 ticks_per_beat for export: standard resolution that cleanly represents all standard note durations

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Grid string conversion for Duration.from_cn**
- **Found during:** Task 1 (MIDI import)
- **Issue:** Plan used `Duration.from_cn(grid)` with grid='16', but from_cn expects CN base letters ('s', 'e'), not numeric strings
- **Fix:** Added _GRID_TO_CN lookup table mapping '16' -> 's', '8' -> 'e', etc.
- **Files modified:** src/cadenza/io/midi.py
- **Verification:** All quantization tests pass with both '16' and '8' grids
- **Committed in:** 30759a9

**2. [Rule 3 - Blocking] Installed mido dependency in virtual environment**
- **Found during:** Task 1 (MIDI import)
- **Issue:** mido not installed in project venv
- **Fix:** `pip install mido` in .venv
- **Verification:** `import mido` succeeds

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes necessary for correct operation. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All I/O expansion complete (MusicXML + MIDI)
- 941 tests pass across full project suite
- Ready for Phase 13 (Documentation) or any future work

## Self-Check: PASSED

All 6 files verified present. All 4 commit hashes verified in git log.

---
*Phase: 12-i-o-expansion*
*Completed: 2026-03-22*
