---
phase: 11-algorithmic-composition
plan: 01
subsystem: composition
tags: [markov, lsystem, stochastic, random-walk, melody-generation]

requires:
  - phase: 02-transforms
    provides: "from_midi, nearest_in_scale pitch transforms"
  - phase: 03-theory
    provides: "Scale dataclass and get_scale for random_walk"
provides:
  - "MarkovModel frozen dataclass for trained Markov chains"
  - "train_markov: build Markov model from Phrase with configurable order"
  - "markov_melody: generate reproducible melodies from trained models"
  - "lsystem_melody: deterministic L-system string rewriting to Phrase"
  - "probabilistic_melody: weighted random pitch selection"
  - "tendency_mask_melody: time-varying pitch distributions"
  - "random_walk: scale-constrained stepwise melody generation"
affects: [11-02-algorithmic-composition]

tech-stack:
  added: []
  patterns: ["instance-based RNG (random.Random(seed)) for reproducibility", "look-ahead filtering to avoid Markov dead-ends"]

key-files:
  created:
    - src/cadenza/composition/__init__.py
    - src/cadenza/composition/markov.py
    - src/cadenza/composition/lsystem.py
    - src/cadenza/composition/stochastic.py
    - tests/composition/__init__.py
    - tests/composition/conftest.py
    - tests/composition/test_markov.py
    - tests/composition/test_lsystem.py
    - tests/composition/test_stochastic.py
  modified: []

key-decisions:
  - "Cyclic training phrase fixture (ascending + descending) to ensure Markov chain has loops and no dead-end states"
  - "One-step look-ahead in markov_melody to prefer successors with valid transitions, maintaining all-pairs invariant"
  - "Instance-based RNG (random.Random(seed)) in all generators for deterministic reproducibility"
  - "random_walk snap-and-filter: candidates snapped via nearest_in_scale, filtered by max_step semitone distance"

patterns-established:
  - "Composition module pattern: pure functions returning Phrase tuples, optional Duration and seed parameters"
  - "Look-ahead transition filtering for Markov chains to avoid dead-end states"

requirements-completed: [ALGO-01, ALGO-02, ALGO-03, ALGO-04, ALGO-05, ALGO-06]

duration: 10min
completed: 2026-03-22
---

# Phase 11 Plan 01: Algorithmic Composition - Generative Algorithms Summary

**Markov chain, L-system, and stochastic melody generators with seed-reproducible output and scale-constrained random walks**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-22T16:17:47Z
- **Completed:** 2026-03-22T16:27:24Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- MarkovModel frozen dataclass with order-configurable training and look-ahead generation
- L-system string-rewriting melody generator with alphabet-to-note translation
- Three stochastic generators: probabilistic, tendency mask, and scale-constrained random walk
- Full TDD: 28 tests covering all six ALGO requirements

## Task Commits

Each task was committed atomically (TDD: RED then GREEN):

1. **Task 1: Markov chains and L-system melody generation**
   - RED: `0ad7eba` (test: add failing tests for Markov chain and L-system)
   - GREEN: `51da16c` (feat: implement Markov chain and L-system melody generation)
2. **Task 2: Stochastic melody generators**
   - RED: `a0884e8` (test: add failing tests for stochastic melody generators)
   - GREEN: `304c4eb` (feat: implement stochastic melody generators)

## Files Created/Modified
- `src/cadenza/composition/__init__.py` - Package init with re-exports of all 7 composition functions
- `src/cadenza/composition/markov.py` - MarkovModel dataclass, train_markov, markov_melody
- `src/cadenza/composition/lsystem.py` - lsystem_melody with string rewriting and alphabet translation
- `src/cadenza/composition/stochastic.py` - probabilistic_melody, tendency_mask_melody, random_walk
- `tests/composition/__init__.py` - Test package init
- `tests/composition/conftest.py` - Shared fixtures: sample phrase, C major scale, quarter duration
- `tests/composition/test_markov.py` - 9 tests for MarkovModel, train_markov, markov_melody
- `tests/composition/test_lsystem.py` - 5 tests for lsystem_melody
- `tests/composition/test_stochastic.py` - 14 tests for all three stochastic generators

## Decisions Made
- Used cyclic training phrase (ascending + descending) for test fixtures to ensure Markov chain has loops
- Implemented one-step look-ahead in markov_melody to prefer successors with valid onward transitions
- All generators use instance-based RNG (random.Random(seed)) for deterministic reproducibility
- random_walk snaps candidates via nearest_in_scale then filters by max_step semitone distance

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Cyclic training phrase for valid Markov transitions**
- **Found during:** Task 1 (Markov chain implementation)
- **Issue:** Original 8-note ascending scale fixture created dead-end states in the Markov chain, making it impossible to generate 10-note sequences with all-valid consecutive transitions
- **Fix:** Changed sample_phrase fixture from pure ascending (C4-C5) to ascending-then-descending (C4-C5-B4-A4), creating bidirectional transitions and eliminating dead-ends
- **Files modified:** tests/composition/conftest.py
- **Verification:** test_markov_melody_transitions_valid passes with all pairs validated
- **Committed in:** 51da16c (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Necessary for correctness -- original fixture couldn't satisfy the must_have truth about valid transitions. No scope creep.

## Issues Encountered
- Pre-existing flaky test in tests/counterpoint/test_generation.py (parallel octave detection) -- unrelated to this plan, not addressed

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Composition subpackage established with 6 of 7 algorithmic functions
- Plan 11-02 can add the remaining algorithm (genetic/evolutionary) and any additional utilities
- All functions follow consistent API: Phrase return type, optional Duration and seed parameters

---
*Phase: 11-algorithmic-composition*
*Completed: 2026-03-22*

## Self-Check: PASSED

All 9 created files verified present. All 4 task commits verified in git log.
