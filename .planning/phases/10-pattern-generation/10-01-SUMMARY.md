---
phase: 10-pattern-generation
plan: 01
subsystem: patterns
tags: [euclidean-rhythm, bjorklund, isorhythm, ostinato, accent, binary-rhythm]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Note, Rest, Duration, Pitch, Phrase core types
  - phase: 02-transforms
    provides: from_midi pitch conversion
provides:
  - euclidean_rhythm (Bjorklund's algorithm)
  - binary_rhythm (integer to bitmap)
  - apply_rhythm (bitmap + pitches to Phrase)
  - isorhythm (talea/color independent cycling via LCM)
  - ostinato (phrase repetition with variation callback)
  - accent_pattern (every Nth Note accented, Rests skipped)
affects: [10-02-PLAN, api-routes, cn-serialization]

# Tech tracking
tech-stack:
  added: []
  patterns: [Bjorklund algorithm, itertools.cycle for pitch cycling, math.lcm for isorhythm, dataclasses.replace for immutable articulation update]

key-files:
  created:
    - src/cadenza/patterns/__init__.py
    - src/cadenza/patterns/rhythm.py
    - src/cadenza/patterns/melodic.py
    - tests/patterns/__init__.py
    - tests/patterns/conftest.py
    - tests/patterns/test_rhythm.py
    - tests/patterns/test_melodic.py
  modified: []

key-decisions:
  - "Bjorklund's algorithm for Euclidean rhythm (iterative group-merge, not recursive)"
  - "binary_rhythm(0) returns (False,) single slot, not empty tuple"
  - "accent_pattern uses 1-based counting: accent at count % n == 0"

patterns-established:
  - "Pattern subpackage follows counterpoint __init__.py re-export pattern"
  - "Rhythm functions return tuple[bool, ...] bitmaps; apply_rhythm bridges to Phrase"

requirements-completed: [RHYT-06, PATT-01, PATT-02, PATT-03, PATT-04, PATT-07]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 10 Plan 01: Pattern Generation Summary

**Euclidean/binary rhythm generation, apply_rhythm pitch mapping, isorhythm with LCM cycling, ostinato with variation callbacks, and accent patterns skipping Rests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T14:32:54Z
- **Completed:** 2026-03-22T14:35:33Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Six pattern generation functions implemented in new `cadenza.patterns` subpackage
- Bjorklund's algorithm produces correct Euclidean rhythms (tresillo, cinquillo verified)
- Isorhythm independently cycles talea and color with LCM-based cycle length
- 29 tests covering all functions with edge cases and error handling

## Task Commits

Each task was committed atomically:

1. **Task 1: Euclidean rhythm, binary rhythm, and apply_rhythm** - `4c5e778` (feat)
2. **Task 2: Isorhythm, ostinato, and accent pattern** - `609de25` (feat)

_TDD workflow: RED (import errors) -> GREEN (implementation) for both tasks._

## Files Created/Modified
- `src/cadenza/patterns/__init__.py` - Package init with 6-function re-export
- `src/cadenza/patterns/rhythm.py` - euclidean_rhythm, binary_rhythm, apply_rhythm
- `src/cadenza/patterns/melodic.py` - isorhythm, ostinato, accent_pattern
- `tests/patterns/__init__.py` - Test package init
- `tests/patterns/conftest.py` - Shared fixtures (sample_phrase, quarter)
- `tests/patterns/test_rhythm.py` - 16 tests for rhythm functions
- `tests/patterns/test_melodic.py` - 13 tests for melodic functions

## Decisions Made
- Bjorklund's algorithm uses iterative group-merge approach (not recursive) for clarity
- binary_rhythm(0) returns (False,) as a single-slot rest pattern, not empty tuple
- accent_pattern uses 1-based counting: first Note is count=1, accent when count % n == 0

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All six single-voice pattern functions ready for use
- Plan 10-02 (multi-voice patterns like hocket, canon) can build on these
- All 828 project tests pass with no regressions

## Self-Check: PASSED

All 7 created files verified on disk. Both task commits (4c5e778, 609de25) verified in git log.

---
*Phase: 10-pattern-generation*
*Completed: 2026-03-22*
