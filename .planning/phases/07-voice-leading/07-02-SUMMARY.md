---
phase: 07-voice-leading
plan: 02
subsystem: analysis
tags: [voice-leading, smooth-voice-leading, inner-voices, permutation, greedy]

# Dependency graph
requires:
  - phase: 07-voice-leading
    provides: "VoiceLeadingViolation, check_voice_leading, _extract_pitches from plan 07-01"
  - phase: 01-foundation
    provides: "Pitch, Note, Rest, Duration, Phrase, Score core types"
  - phase: 02-transforms
    provides: "from_midi for MIDI-to-Pitch conversion in inner voice generation"
provides:
  - "smooth_voice_leading: minimum-movement chord voice assignment via permutation search"
  - "generate_inner_voices: greedy beat-by-beat inner voice generation with configurable ranges"
affects: [08-counterpoint, rest-api-v1]

# Tech tracking
tech-stack:
  added: []
  patterns: ["itertools.permutations for exhaustive minimum-cost voice assignment", "greedy clamped-midpoint tracking for inner voice generation"]

key-files:
  created: []
  modified:
    - src/cadenza/analysis/voiceleading.py
    - tests/analysis/test_voiceleading.py
    - src/cadenza/analysis/__init__.py

key-decisions:
  - "Permutation search is exhaustive (O(n!) on chord size) -- acceptable for typical 3-6 voice chords"
  - "Inner voice generation uses greedy clamped midpoint: starts at range midpoint, stays put unless out of range"
  - "Default SATB ranges: alto C3-G5 (midi 48-79), tenor C2-G4 (midi 36-67)"

patterns-established:
  - "Exhaustive permutation search for small combinatorial voice assignment problems"
  - "Greedy beat-by-beat voice generation with range clamping"

requirements-completed: [VLEAD-05, VLEAD-08]

# Metrics
duration: 3min
completed: 2026-03-20
---

# Phase 7 Plan 2: Voice Leading Generation Summary

**smooth_voice_leading via exhaustive permutation search and generate_inner_voices with greedy clamped-midpoint beat-by-beat generation**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-20T09:14:28Z
- **Completed:** 2026-03-20T09:17:46Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- smooth_voice_leading finds minimum-movement voice assignment by trying all permutations of chord2
- generate_inner_voices produces n inner voice Phrases within configurable pitch ranges using greedy beat-by-beat clamped midpoint tracking
- Default SATB ranges (alto C3-G5, tenor C2-G4) with support for custom ranges
- Both functions re-exported from cadenza.analysis
- 11 new tests (5 smooth + 6 inner voices), all 27 voice leading tests pass, full suite 646 green

## Task Commits

Each task was committed atomically:

1. **Task 1: smooth_voice_leading with permutation search** - `54e9070` (test: RED), `c012930` (feat: GREEN)
2. **Task 2: generate_inner_voices with greedy beat-by-beat selection and re-exports** - `79035bd` (test: RED), `f12c344` (feat: GREEN)

_Note: TDD tasks have multiple commits (test -> feat)_

## Files Created/Modified
- `src/cadenza/analysis/voiceleading.py` - Added smooth_voice_leading and generate_inner_voices functions with default SATB ranges
- `tests/analysis/test_voiceleading.py` - 11 new tests for smooth voice leading and inner voice generation
- `src/cadenza/analysis/__init__.py` - Re-exports smooth_voice_leading and generate_inner_voices

## Decisions Made
- Permutation search is exhaustive -- acceptable for typical chord sizes (3-6 voices)
- Inner voice generation uses greedy clamped midpoint: starts at range center, minimizes movement by staying put
- Plan's test_smooth_voice_leading_reorder expected value was incorrect (tied costs, identity found first) -- fixed test to use a case that forces actual reordering

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed incorrect expected value in test_smooth_voice_leading_reorder**
- **Found during:** Task 1
- **Issue:** Plan computed cost of (D4,B4,G4) as 9 but identity (D4,G4,B4) also has cost 9 and is found first
- **Fix:** Replaced test case with chord1=(C4,E4,C5), chord2=(D4,B4,F4) where reordering to (D4,F4,B4) gives cost 4 vs identity cost 16
- **Files modified:** tests/analysis/test_voiceleading.py
- **Committed in:** c012930 (part of Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test fix necessary for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Voice leading analysis and generation complete for phase 07
- smooth_voice_leading and generate_inner_voices available for counterpoint (phase 08)
- check_voice_leading can validate generated voice leading results

---
*Phase: 07-voice-leading*
*Completed: 2026-03-20*
