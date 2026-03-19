---
phase: 03-theory-libraries
plan: 01
subsystem: theory
tags: [scales, modes, music-theory, registry, diatonic-transpose]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "Pitch, Interval, Note, Phrase core types"
  - phase: 02-transforms
    provides: "pitch transform stubs (diatonic_transpose, pitch_in_scale, nearest_in_scale)"
provides:
  - "Scale frozen dataclass with root, name, pitches, intervals"
  - "36 built-in scale definitions covering Western, modal, pentatonic, blues, symmetric, bebop, non-Western"
  - "get_scale, register_scale, scales_for_pitches, scale_degree, relative_key, parallel_key"
  - "Completed Phase 2 stubs: diatonic_transpose, pitch_in_scale, nearest_in_scale"
affects: [03-02-chords, 05-harmonic-analysis, 06-key-detection]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Scale registry pattern with _SCALE_REGISTRY dict and _DEGREE_STEPS for pitch spelling", "Auto-infer degree steps for custom registered scales"]

key-files:
  created:
    - src/cadenza/theory/__init__.py
    - src/cadenza/theory/scales.py
    - tests/theory/__init__.py
    - tests/theory/test_scales.py
    - tests/transforms/test_pitch_stubs.py
  modified:
    - src/cadenza/transforms/pitch.py
    - tests/transforms/test_pitch_transforms.py

key-decisions:
  - "round() for octave computation in _build_pitch to handle boundary cases like Bb"
  - "_infer_degree_steps for custom scales uses chromatic-to-diatonic semitone mapping"
  - "Phase 2 stub tests updated from NotImplementedError to functional assertions"

patterns-established:
  - "Theory module pattern: frozen dataclass + registry dict + builder function"
  - "Degree steps mapping separates letter-name logic from semitone logic for correct enharmonic spelling"

requirements-completed: [SCAL-01, SCAL-02, SCAL-03, SCAL-04, SCAL-05, SCAL-06, SCAL-07, SCAL-08, SCAL-09, SCAL-10, SCAL-11, SCAL-12]

# Metrics
duration: 6min
completed: 2026-03-19
---

# Phase 3 Plan 1: Scale Library Summary

**Scale/mode registry with 36 built-in scales, query functions (scales_for_pitches, scale_degree, relative/parallel key), and completed Phase 2 diatonic stubs**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-19T09:13:58Z
- **Completed:** 2026-03-19T09:20:25Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Scale frozen dataclass with 36 built-in scales covering all major categories (Western, church modes, pentatonic, blues, symmetric, bebop, 16 non-Western)
- Query functions: scales_for_pitches, scale_degree, relative_key, parallel_key
- Completed Phase 2 stubs: diatonic_transpose, pitch_in_scale, nearest_in_scale now fully functional
- 56 new tests (45 scale tests + 9 pitch stub tests + 2 updated existing tests), full suite 380 tests green

## Task Commits

Each task was committed atomically:

1. **Task 1: Scale type, registry, get_scale, and all built-in scales** - `6e09756` (test: RED) then `6c174b2` (feat: GREEN)
2. **Task 2: Scale query functions and Phase 2 stub completion** - `3206e23` (test: RED) then `46c31d3` (feat: GREEN)

## Files Created/Modified
- `src/cadenza/theory/__init__.py` - Public API re-exports for theory package
- `src/cadenza/theory/scales.py` - Scale dataclass, 36 built-in scales, registry, query functions
- `tests/theory/__init__.py` - Test package init
- `tests/theory/test_scales.py` - 45 tests for SCAL-01 through SCAL-12
- `tests/transforms/test_pitch_stubs.py` - 9 tests for completed Phase 2 stubs
- `src/cadenza/transforms/pitch.py` - diatonic_transpose, pitch_in_scale, nearest_in_scale implementations
- `tests/transforms/test_pitch_transforms.py` - Updated 3 stub tests to functional tests

## Decisions Made
- Used `round()` instead of `//` for octave computation in `_build_pitch` to handle boundary cases (e.g., Bb where floor division puts the pitch in the wrong octave)
- Added `_infer_degree_steps` function for custom registered scales so `register_scale` works without requiring manual degree step mapping
- Updated Phase 2 stub tests from `NotImplementedError` expectations to functional assertions since stubs are now implemented

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed octave computation in _build_pitch**
- **Found during:** Task 1 (Scale type implementation)
- **Issue:** Floor division `//` for octave gave wrong octave for pitches near letter-name boundaries (e.g., Bb4 was computed as Bb3 with acc_semitones=11)
- **Fix:** Changed to `round()` which selects the octave keeping accidental within [-2, 2] range
- **Files modified:** src/cadenza/theory/scales.py
- **Verification:** F major scale test passes with correct Bb4
- **Committed in:** 6c174b2

**2. [Rule 1 - Bug] Fixed blues scale degree steps**
- **Found during:** Task 1 (Scale type implementation)
- **Issue:** Blues scale degree_steps had `(0, 2, 3, 3, 4, 6)` producing F# instead of Gb for the tritone
- **Fix:** Changed to `(0, 2, 3, 4, 4, 6)` so both Gb and G use letter G
- **Files modified:** src/cadenza/theory/scales.py
- **Verification:** C blues test passes with Gb4 not F#4
- **Committed in:** 6c174b2

**3. [Rule 1 - Bug] Updated Phase 2 stub tests**
- **Found during:** Task 2 (Phase 2 stub completion)
- **Issue:** Existing tests expected `NotImplementedError` from now-implemented functions
- **Fix:** Updated 3 tests to verify actual behavior instead of error
- **Files modified:** tests/transforms/test_pitch_transforms.py
- **Verification:** Full suite 380 tests green
- **Committed in:** 46c31d3

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed items above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Scale infrastructure complete; chord library (Plan 03-02) can build diatonic chords using Scale type
- diatonic_transpose enables scale-aware melodic transformations
- scales_for_pitches enables scale detection for harmonic analysis (Phase 5)

---
*Phase: 03-theory-libraries*
*Completed: 2026-03-19*
