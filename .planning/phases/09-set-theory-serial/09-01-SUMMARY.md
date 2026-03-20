---
phase: 09-set-theory-serial
plan: 01
subsystem: analysis
tags: [set-theory, forte, pitch-class, interval-vector, prime-form]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Pitch.pitch_class property for constructing PC sets
provides:
  - 208-entry Forte table with reverse index (FORTE_TABLE, PRIME_TO_FORTE)
  - 14 pure functions for pitch class set analysis
  - Forte (1973) prime form algorithm
  - Interval vector computation
  - Set relationship predicates (subset, superset, Z-relation)
  - Similarity measures (Rp, R0, R1, R2)
affects: [09-02-serial, phase-10-generative, api-endpoints]

# Tech tracking
tech-stack:
  added: []
  patterns: [right-comparison prime form (Forte 1973), module-level constant tables]

key-files:
  created:
    - src/cadenza/settheory/__init__.py
    - src/cadenza/settheory/_forte_table.py
    - src/cadenza/settheory/pcset.py
    - tests/settheory/__init__.py
    - tests/settheory/conftest.py
    - tests/settheory/test_pcset.py
  modified: []

key-decisions:
  - "Forte prime form uses right-comparison (reversed tuple key), not Rahn's left-comparison (lexicographic min)"
  - "Forte table limited to cardinalities 3-9 (208 entries); dyads/decachords excluded as trivially enumerable"

patterns-established:
  - "Right-comparison for Forte prime form: compare reversed tuples to select candidate with smallest intervals packed from right"
  - "Module-level constant dict for lookup tables (_forte_table.py)"

requirements-completed: [SETTH-01, SETTH-02, SETTH-03, SETTH-04, SETTH-05, SETTH-06, SETTH-07, SETTH-08, SETTH-09]

# Metrics
duration: 7min
completed: 2026-03-20
---

# Phase 9 Plan 1: Pitch Class Set Operations Summary

**Forte (1973) prime form algorithm with 208-entry table, interval vectors, set relationships, and similarity measures -- all as pure functions on frozenset[int]**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-20T15:13:58Z
- **Completed:** 2026-03-20T15:20:55Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files created:** 6

## Accomplishments
- 208-entry Forte table verified against all known prime forms (0 mismatches)
- Forte (1973) prime form algorithm correctly handles all 6 Forte/Rahn disagreement cases
- All 14 SETTH functions implemented with locked signatures from CONTEXT.md
- 57 unit tests covering prime form, interval vector, Forte number, complement, inversion, transposition, relationships, and similarity measures

## Task Commits

Each task was committed atomically (TDD):

1. **Task 1 RED: Failing tests** - `72f5804` (test)
2. **Task 1 GREEN: Implementation** - `9e9737c` (feat)

## Files Created/Modified
- `src/cadenza/settheory/__init__.py` - Package init, re-exports all 14 public functions
- `src/cadenza/settheory/_forte_table.py` - FORTE_TABLE (208 entries) and PRIME_TO_FORTE reverse index
- `src/cadenza/settheory/pcset.py` - All 14 SETTH functions: prime_form, interval_vector, forte_number, lookup_by_forte, complement, invert_pcs, transpose_pcs, is_subset, is_superset, is_z_related, rp_relation, r0, r1, r2
- `tests/settheory/__init__.py` - Test package init
- `tests/settheory/conftest.py` - Fixtures: major_triad, all_interval_tetrachord, z_related_pair
- `tests/settheory/test_pcset.py` - 57 tests covering all 9 SETTH requirements

## Decisions Made
- Forte prime form uses right-comparison algorithm (compare reversed tuples) rather than Rahn's left-comparison (lexicographic min). This correctly resolves all ~6 disagreement cases (5-20, 6-Z29, 6-31, 7-Z18, 7-20, 8-26).
- Forte table limited to cardinalities 3-9 (208 entries). Dyads (card 2) and decachords (card 10) excluded as they are trivially enumerable and not part of the standard 208-entry catalog.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed incorrect test expectation for Z-related pair**
- **Found during:** Task 1 GREEN (test execution)
- **Issue:** Plan specified `prime_form(frozenset({0,1,3,7})) == (0,1,4,6)` but {0,1,3,7} is 4-Z29 (prime form (0,1,3,7)), not 4-Z15 ((0,1,4,6)). These are Z-related pairs with same interval vector but different prime forms.
- **Fix:** Split into two tests: one for 4-Z15 ({0,1,4,6} -> (0,1,4,6)) and one for 4-Z29 ({0,1,3,7} -> (0,1,3,7))
- **Files modified:** tests/settheory/test_pcset.py
- **Verification:** Both tests pass; verified against hardcoded Forte table
- **Committed in:** 9e9737c (Task 1 GREEN commit)

**2. [Rule 1 - Bug] Corrected prime form algorithm from Rahn to Forte**
- **Found during:** Task 1 GREEN (5-20 test failure)
- **Issue:** Initial implementation used lexicographic min (Rahn's algorithm), producing (0,1,3,7,8) for 5-20 instead of Forte's (0,1,5,6,8)
- **Fix:** Rewrote algorithm to generate all transposed rotations of both original and inversion, selecting candidate by reversed-tuple comparison (right-packing)
- **Files modified:** src/cadenza/settheory/pcset.py
- **Verification:** All 208 Forte table entries verified, 5-20 specifically produces correct (0,1,5,6,8)
- **Committed in:** 9e9737c (Task 1 GREEN commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes essential for correctness. The plan's test data and research document had an error conflating Z-related pair members. The algorithm fix was required to match Forte (1973) rather than Rahn (1980).

## Issues Encountered
None beyond the deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- settheory package ready for 09-02 (serial/12-tone operations) which will import from this module
- All functions use frozenset[int] per CONTEXT.md locked signatures
- No external dependencies added

---
*Phase: 09-set-theory-serial*
*Completed: 2026-03-20*
