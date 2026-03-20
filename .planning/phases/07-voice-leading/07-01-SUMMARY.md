---
phase: 07-voice-leading
plan: 01
subsystem: analysis
tags: [voice-leading, parallel-fifths, parallel-octaves, voice-crossing, counterpoint]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "Pitch, Interval, Note, Rest, Score, Phrase core types"
provides:
  - "VoiceLeadingViolation dataclass for structured violation reports"
  - "check_voice_leading orchestrator for comprehensive score analysis"
  - "Private detectors: _check_parallels, _check_crossing, _check_overlap, _check_leaps"
affects: [07-voice-leading, 08-counterpoint, rest-api-v1]

# Tech tracking
tech-stack:
  added: []
  patterns: ["itertools.combinations for voice pair iteration", "mod-12 semitone comparison for interval equivalence"]

key-files:
  created:
    - src/cadenza/analysis/voiceleading.py
    - tests/analysis/test_voiceleading.py
  modified:
    - src/cadenza/analysis/__init__.py

key-decisions:
  - "Parallel detection uses mod-12 semitones for octave/unison equivalence and same-direction + both-voices-moved checks"
  - "Score tuple order determines upper/lower voice designation (first = upper)"

patterns-established:
  - "Voice pair analysis via itertools.combinations on Score._voices"
  - "Pitch extraction with None for rests enabling graceful skip logic"

requirements-completed: [VLEAD-01, VLEAD-02, VLEAD-03, VLEAD-04, VLEAD-06, VLEAD-07]

# Metrics
duration: 3min
completed: 2026-03-20
---

# Phase 7 Plan 1: Voice Leading Violation Detection Summary

**VoiceLeadingViolation dataclass with parallel fifth/octave, crossing, overlap, and leap detectors orchestrated by check_voice_leading**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-20T09:09:29Z
- **Completed:** 2026-03-20T09:12:22Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- VoiceLeadingViolation frozen dataclass with rule, voice names, position, interval, and severity
- Six detector functions: parallel fifths, parallel octaves, voice crossing, voice overlap, large leaps, augmented/diminished leaps
- check_voice_leading orchestrator analyzing all voice pairs and returning sorted violations
- 16 tests covering all rules, edge cases (contrary motion, oblique motion, rests, compound intervals), and orchestrator behavior

## Task Commits

Each task was committed atomically:

1. **Task 1: VoiceLeadingViolation dataclass and all detector functions with tests** - `9edc69d` (test: RED), `f73a9b9` (feat: GREEN)
2. **Task 2: Update analysis __init__.py re-exports** - `fc41434` (chore)

## Files Created/Modified
- `src/cadenza/analysis/voiceleading.py` - VoiceLeadingViolation dataclass, _extract_pitches, _check_parallels, _check_crossing, _check_overlap, _check_leaps, check_voice_leading
- `tests/analysis/test_voiceleading.py` - 16 tests for all violation types and edge cases
- `src/cadenza/analysis/__init__.py` - Re-exports VoiceLeadingViolation and check_voice_leading

## Decisions Made
- Parallel detection uses mod-12 semitones for octave/unison equivalence (0) and fifths (7), requiring same-direction motion and both voices moving
- Score tuple order determines upper/lower voice designation (first in tuple = upper)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Voice leading violation detection complete, ready for Plan 07-02 (smooth voice leading and inner voice generation)
- check_voice_leading can be used to validate results from voice generation functions

---
*Phase: 07-voice-leading*
*Completed: 2026-03-20*
