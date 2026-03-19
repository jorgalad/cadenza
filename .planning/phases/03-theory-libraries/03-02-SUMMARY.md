---
phase: 03-theory-libraries
plan: 02
subsystem: theory
tags: [chords, music-theory, diatonic, secondary-dominant, augmented-sixth, neapolitan]

# Dependency graph
requires:
  - phase: 03-theory-libraries/01
    provides: Scale type, get_scale, _build_pitch pattern for pitch spelling
  - phase: 01-foundation
    provides: Pitch type, STEP_INDEX, STEP_SEMITONES, ACCIDENTAL_SEMITONES
provides:
  - get_chord with 22 built-in chord types and inversions
  - register_chord for custom chord definitions
  - diatonic_chords for all triads/sevenths in any scale
  - secondary_dominant for V7 of any scale degree
  - aug6_chord for Italian, French, German augmented sixths
  - neapolitan_chord for bII chord
affects: [05-harmonic-analysis, 04-rest-api]

# Tech tracking
tech-stack:
  added: []
  patterns: [chord-registry-with-dual-encoding, key-relative-chord-construction]

key-files:
  created:
    - src/cadenza/theory/chords.py
    - tests/theory/test_chords.py
  modified:
    - src/cadenza/theory/__init__.py

key-decisions:
  - "Chord registry stores both semitone offsets and letter-step offsets for correct enharmonic spelling"
  - "Duplicated _build_pitch from scales.py rather than importing private function (keeps modules decoupled)"
  - "aug6_chord and neapolitan_chord use key-relative construction (not chord registry) since they are inherently key-context chords"

patterns-established:
  - "Dual-encoding chord registry: (semitones, degree_steps) enables correct spelling for any root"
  - "Key-relative chord functions take (key_root, key_name) rather than chord symbol lookup"

requirements-completed: [CHRD-01, CHRD-02, CHRD-03, CHRD-04, CHRD-05, CHRD-06, CHRD-07, CHRD-08, CHRD-09]

# Metrics
duration: 4min
completed: 2026-03-19
---

# Phase 3 Plan 2: Chord Library Summary

**Complete chord library with 22 built-in types, inversions, diatonic chord generation, secondary dominants, augmented sixths, and Neapolitan chord**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-19T09:22:52Z
- **Completed:** 2026-03-19T09:26:41Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Chord registry with 22 built-in chord types covering triads, sevenths, extended, added, and suspended chords
- get_chord returns correctly-spelled pitches for any root with any accidental, with inversion support
- diatonic_chords generates all triads or sevenths for any scale (major, minor, modes)
- Secondary dominants, augmented sixth chords (Italian/French/German), and Neapolitan chord fully functional
- 45 chord-specific tests, 425 total tests all green

## Task Commits

Each task was committed atomically:

1. **Task 1: Chord registry, get_chord, inversions (RED)** - `06b7e5c` (test)
2. **Task 1: Chord registry, get_chord, inversions (GREEN)** - `990fa44` (feat)
3. **Task 2: Diatonic chords, secondary dominants, aug6, neapolitan (RED)** - `e92bba1` (test)
4. **Task 2: Diatonic chords, secondary dominants, aug6, neapolitan (GREEN)** - `11274d8` (feat)

_TDD: Each task has separate test and implementation commits._

## Files Created/Modified
- `src/cadenza/theory/chords.py` - Chord registry, get_chord, register_chord, diatonic_chords, secondary_dominant, aug6_chord, neapolitan_chord
- `tests/theory/test_chords.py` - 45 tests covering CHRD-01 through CHRD-09
- `src/cadenza/theory/__init__.py` - Updated exports to include all chord functions

## Decisions Made
- Chord registry stores both semitone offsets and letter-step offsets per chord type -- this dual encoding enables correct enharmonic spelling (e.g., F# major = F#-A#-C#, not F#-Bb-Db)
- Duplicated `_build_pitch` helper from scales.py rather than importing a private function -- keeps modules decoupled
- Augmented sixth and Neapolitan chords use key-relative pitch construction (not the chord registry) since they are inherently key-context chords

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 (Theory Libraries) is now fully complete with both scales and chords
- Phase 4 (REST API) can expose all theory functions as endpoints
- Phase 5 (Harmonic Analysis) can import chord functions for chord identification
- All 425 tests green

---
*Phase: 03-theory-libraries*
*Completed: 2026-03-19*

## Self-Check: PASSED
- All created files exist
- All 4 task commits verified (06b7e5c, 990fa44, e92bba1, 11274d8)
