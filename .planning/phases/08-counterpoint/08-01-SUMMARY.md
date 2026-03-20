---
phase: 08-counterpoint
plan: 01
subsystem: counterpoint
tags: [counterpoint, species, backtracking, validation, music-theory]

# Dependency graph
requires:
  - phase: 07-voice-leading
    provides: "Voice leading violation detection patterns, _extract_pitches helper"
provides:
  - "CounterpointViolation dataclass for rule violations"
  - "check_counterpoint validation with configurable severity"
  - "classify_interval consonance classification"
  - "Reusable _backtrack search engine for all species generators"
  - "generate_first_species with above/below and range support"
affects: [08-02-counterpoint, counterpoint-species-II-V]

# Tech tracking
tech-stack:
  added: []
  patterns: [backtracking-search, candidate-priority-ordering, species-constraint-validation]

key-files:
  created:
    - src/cadenza/counterpoint/__init__.py
    - src/cadenza/counterpoint/rules.py
    - src/cadenza/counterpoint/validation.py
    - src/cadenza/counterpoint/_engine.py
    - src/cadenza/counterpoint/generation.py
    - tests/counterpoint/__init__.py
    - tests/counterpoint/conftest.py
    - tests/counterpoint/test_validation.py
    - tests/counterpoint/test_generation.py
  modified: []

key-decisions:
  - "Candidate priority ordering with random tiebreaking instead of full shuffle for stepwise motion preference"
  - "Voice direction (above/below) inferred from first pitch pair, not explicit parameter in validation"
  - "builtins.range used to avoid shadowing Python range() by API parameter name"
  - "Penultimate position must be step-distance from valid final pitch for cadential approach"

patterns-established:
  - "Backtracking engine: candidates_fn provides ordered candidates, validate_fn filters, _backtrack recurses"
  - "Counterpoint validation: extract pitches, run per-rule checkers, apply severity map, sort by position"

requirements-completed: [CPTR-01, CPTR-06, CPTR-07, CPTR-10]

# Metrics
duration: 6min
completed: 2026-03-20
---

# Phase 8 Plan 01: Counterpoint Rules Engine and First Species Summary

**Counterpoint validation engine with configurable severity rules and backtracking first species generator supporting above/below CF with range constraints**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-20T12:44:21Z
- **Completed:** 2026-03-20T12:50:30Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- CounterpointViolation frozen dataclass with rule, species, position, interval, severity fields
- check_counterpoint detects parallel 5ths/8ves, dissonance on beat, voice crossing, large leaps, repeated notes with configurable severity overrides
- Reusable _backtrack DFS engine for all future species generators
- generate_first_species produces valid counterpoint above and below CF with perfect consonances at endpoints, stepwise motion preference, and range constraints
- 24 passing counterpoint tests, 670 total suite tests with zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Counterpoint rules engine, CounterpointViolation dataclass, and check_counterpoint validation** - `f035450` (test)
2. **Task 2: Backtracking engine and first species generation** - `14916b0` (feat)

## Files Created/Modified
- `src/cadenza/counterpoint/__init__.py` - Package re-exports: CounterpointViolation, check_counterpoint, generate_first_species
- `src/cadenza/counterpoint/rules.py` - Consonance classification, PERFECT/IMPERFECT/DISSONANCE sets, DEFAULT_SEVERITIES map
- `src/cadenza/counterpoint/validation.py` - CounterpointViolation dataclass and check_counterpoint with 6 rule checkers
- `src/cadenza/counterpoint/_engine.py` - Shared backtracking search engine (_backtrack) for all species generators
- `src/cadenza/counterpoint/generation.py` - generate_first_species with candidate priority ordering and constraint validation
- `tests/counterpoint/__init__.py` - Test package init
- `tests/counterpoint/conftest.py` - Shared fixtures: cf_c_major, make_phrase helper
- `tests/counterpoint/test_validation.py` - 14 validation tests covering all rule types and severity overrides
- `tests/counterpoint/test_generation.py` - 10 generation tests covering consonance, parallels, direction, range, stepwise motion

## Decisions Made
- Candidate priority ordering with random tiebreaking within priority groups preserves stepwise motion preference while still producing variety across runs
- Voice direction inferred from first available pitch pair rather than requiring explicit above/below parameter in validation
- Used builtins.range to work around Python range() being shadowed by the API's range parameter (plan-specified name)
- Penultimate note validation ensures step-distance approach to valid final pitch for proper cadential motion

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed range() shadowing by parameter name**
- **Found during:** Task 2 (generation implementation)
- **Issue:** Function parameter `range` shadowed Python's builtin `range()`, causing TypeError in nested functions
- **Fix:** Imported `builtins` module and used `builtins.range()` for iteration
- **Files modified:** src/cadenza/counterpoint/generation.py
- **Verification:** All 10 generation tests pass
- **Committed in:** 14916b0 (Task 2 commit)

**2. [Rule 1 - Bug] Fixed random.shuffle destroying candidate ordering**
- **Found during:** Task 2 (generation implementation)
- **Issue:** Full random.shuffle in _backtrack destroyed priority-based candidate ordering, preventing stepwise motion
- **Fix:** Moved randomness to candidate function (shuffle before stable sort by priority), removed shuffle from engine
- **Files modified:** src/cadenza/counterpoint/_engine.py, src/cadenza/counterpoint/generation.py
- **Verification:** Stepwise motion test passes (>50% intervals <= 4 semitones)
- **Committed in:** 14916b0 (Task 2 commit)

**3. [Rule 1 - Bug] Fixed invalid valid-counterpoint test fixture**
- **Found during:** Task 1 (test validation)
- **Issue:** Plan-suggested counterpoint line C5,B4,A4,C5,E5,D5,A4,C5 had parallel fifths at positions 4-5
- **Fix:** Replaced with E5,D5,A4,C5,C5,B4,A4,C5 which has no error-level violations
- **Files modified:** tests/counterpoint/test_validation.py
- **Verification:** test_valid_first_species_no_violations passes
- **Committed in:** f035450 (Task 1 commit)

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed items above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Backtracking engine ready for species II-V generators in plan 08-02
- Validation framework extensible with new rule checkers
- All counterpoint types properly re-exported from package __init__

---
*Phase: 08-counterpoint*
*Completed: 2026-03-20*
