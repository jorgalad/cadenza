---
phase: 05-harmonic-analysis
plan: 01
subsystem: analysis
tags: [chord-identification, chord-symbols, cn-format, brute-force-matching, inversions]

# Dependency graph
requires:
  - phase: 03-music-theory
    provides: "_CHORD_REGISTRY, get_chord, Pitch, pitch_class"
  - phase: 04-rest-api
    provides: "parse_pitch_string from api.parsing"
provides:
  - "identify_chord: pitch-set to ChordMatch (root, symbol, inversion)"
  - "chord_symbol / parse_chord_symbol: CN chord string format"
  - "realize_chord: analysis-API wrapper around get_chord"
  - "ChordMatch frozen dataclass"
affects: [05-02-roman-numerals, harmonic-analysis-api]

# Tech tracking
tech-stack:
  added: []
  patterns: ["brute-force pitch-class matching across 12 roots x registry", "complexity ranking for disambiguation", "quality alias resolution chain"]

key-files:
  created:
    - src/cadenza/analysis/__init__.py
    - src/cadenza/analysis/chords.py
    - tests/analysis/__init__.py
    - tests/analysis/test_chords.py
  modified: []

key-decisions:
  - "Brute-force 12-root x registry matching rather than interval fingerprinting for simplicity and correctness"
  - "Complexity ranking: triads(0) > sevenths/sus(1) > 9ths(2) > 11ths(3) > 13ths(4) for disambiguation"
  - "Single-digit octave in chord symbol regex to separate octave from numeric quality (e.g., c47 = C4 dom7)"
  - "Multi-strategy quality resolution: exact alias, exact registry, lowercase registry, lowercase alias"

patterns-established:
  - "Analysis module pattern: analysis/ subpackage with __init__.py re-exports"
  - "ChordMatch dataclass as standard chord identification result type"
  - "CN chord symbol format: {step}{acc}{octave}{quality} e.g., c4maj7, fs4m"

requirements-completed: [HARM-01, HARM-07, HARM-08, HARM-09]

# Metrics
duration: 4min
completed: 2026-03-19
---

# Phase 05 Plan 01: Chord Analysis Foundation Summary

**Chord identification engine with brute-force pitch-class matching, CN chord symbol format, and quality alias resolution**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-19T19:31:26Z
- **Completed:** 2026-03-19T19:35:08Z
- **Tasks:** 2 (TDD: 4 commits total)
- **Files modified:** 4

## Accomplishments
- identify_chord recognizes all registry chord types (triads, sevenths, extended, sus) with inversion detection via bass note analysis
- chord_symbol/parse_chord_symbol provide CN-format chord strings with alias support (Maj, min, -, +, o)
- Round-trip verified for all 21+ registry keys
- 24 analysis tests, 515 total tests green

## Task Commits

Each task was committed atomically (TDD RED/GREEN):

1. **Task 1 RED: Chord identification tests** - `5c3c7d8` (test)
2. **Task 1 GREEN: Chord identification implementation** - `57a4602` (feat)
3. **Task 2 RED: Chord symbol tests** - `3ca1058` (test)
4. **Task 2 GREEN: Chord symbol implementation** - `b2b537b` (feat)

## Files Created/Modified
- `src/cadenza/analysis/__init__.py` - Public API re-exports (ChordMatch, identify_chord, chord_symbol, parse_chord_symbol, realize_chord)
- `src/cadenza/analysis/chords.py` - Chord identification engine, symbol generation/parsing, realization wrapper
- `tests/analysis/__init__.py` - Test package init
- `tests/analysis/test_chords.py` - 24 tests covering identification, inversions, symbols, round-trips

## Decisions Made
- Brute-force 12-root x registry matching: simple, correct, and fast enough for all practical use (21 chord types x 12 roots = 252 candidates)
- Complexity ranking prefers simpler interpretations (triads over extended chords) then root position over inversions
- Single-digit octave regex separator prevents "c47" from being parsed as pitch "c47" instead of "C4 + dom7"
- Multi-strategy quality resolution handles case variations and aliases without requiring exhaustive alias mapping

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed chord symbol regex to use single-digit octave**
- **Found during:** Task 2 (round-trip test)
- **Issue:** `\d+` in regex consumed all digits, making "c47" parse as octave 47 instead of C4 + "7" quality
- **Fix:** Changed `\d+` to `\d` (single digit) since octaves are always 0-9
- **Files modified:** src/cadenza/analysis/chords.py
- **Verification:** Round-trip test passes for all registry keys including "7", "9", "11", "13"
- **Committed in:** b2b537b (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential fix for correct chord symbol parsing. No scope creep.

## Issues Encountered
None beyond the regex fix documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Chord identification foundation ready for Plan 02 (Roman numeral analysis, key detection)
- identify_chord provides the core algorithm that Roman numeral labeling will use
- ChordMatch dataclass established as standard result type

---
*Phase: 05-harmonic-analysis*
*Completed: 2026-03-19*
