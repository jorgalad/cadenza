---
phase: 01-foundation
plan: 01
subsystem: core
tags: [frozen-dataclass, fractions, music-theory, json-codec, hypothesis, tdd]

# Dependency graph
requires: []
provides:
  - "Pitch frozen dataclass with step/accidental/octave, midi_number, enharmonic_equal"
  - "Duration frozen dataclass with Fraction arithmetic, from_omn factory"
  - "Interval frozen dataclass with between() factory computing quality from spelling"
  - "Note and Rest frozen dataclasses with Event union type"
  - "Phrase type alias as tuple[Event, ...]"
  - "Score frozen dataclass with tuple-based voice storage"
  - "JSON codec with lossless round-trip for all core types"
  - "pyproject.toml with zero runtime deps, hatchling build"
affects: [omn-parser, transforms, analysis, api, counterpoint]

# Tech tracking
tech-stack:
  added: [pytest, hypothesis, ruff, mypy, hatchling, pytest-cov]
  patterns: [frozen-dataclass, fraction-arithmetic, tdd-red-green, type-discriminator-json]

key-files:
  created:
    - src/cadenza/core/pitch.py
    - src/cadenza/core/duration.py
    - src/cadenza/core/interval.py
    - src/cadenza/core/note.py
    - src/cadenza/core/phrase.py
    - src/cadenza/core/score.py
    - src/cadenza/core/json_codec.py
    - src/cadenza/omn/errors.py
    - pyproject.toml
    - tests/strategies.py
  modified:
    - src/cadenza/__init__.py
    - src/cadenza/core/__init__.py

key-decisions:
  - "Pre-convert objects in to_json via _to_serializable() to avoid tuple-as-JSON-array flattening"
  - "Score stores _voices as tuple[tuple[str, Phrase], ...] for true immutability and hashability"
  - "JSON codec uses _type discriminator field for polymorphic deserialization"

patterns-established:
  - "Frozen dataclass pattern: @dataclass(frozen=True, order=False) with custom __lt__ for domain ordering"
  - "Fraction-only duration arithmetic: never use float for musical time values"
  - "Type alias pattern: Phrase = tuple[Event, ...] as lightweight wrapper"
  - "TDD workflow: RED (failing tests) -> GREEN (minimal implementation) -> commit each phase"

requirements-completed: [CORE-01, CORE-02, CORE-03, CORE-04, CORE-05, CORE-06, CORE-07, CORE-08, CORE-09, CORE-10]

# Metrics
duration: 6min
completed: 2026-03-19
---

# Phase 1 Plan 1: Core Data Model Summary

**Frozen dataclasses for Pitch/Duration/Interval/Note/Rest/Phrase/Score with Fraction arithmetic, spelling-sensitive equality, and lossless JSON round-trip codec**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-18T23:29:47Z
- **Completed:** 2026-03-18T23:35:30Z
- **Tasks:** 2
- **Files modified:** 20

## Accomplishments
- Complete immutable type system: Pitch (Eb3 != D#3, enharmonic_equal for MIDI comparison), Duration (Fraction-only, dots, tuplets), Interval (quality from spelling)
- Note/Rest/Phrase/Score hierarchy with full hashability and set/dict compatibility
- JSON codec with _type discriminator for lossless round-trip of all core types including nested Fractions
- 89 tests passing at 85% coverage, including Hypothesis property-based tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Project scaffolding + Pitch, Duration, Interval** (TDD)
   - `5b58551` (test: RED - failing tests for Pitch, Duration, Interval)
   - `4bc165a` (feat: GREEN - implement Pitch, Duration, Interval)
2. **Task 2: Note, Rest, Phrase, Score + JSON codec** (TDD)
   - `254f15e` (test: RED - failing tests for Note, Rest, Phrase, Score, JSON codec)
   - `a73222a` (feat: GREEN - implement Note, Rest, Phrase, Score, JSON codec)
3. **Housekeeping**
   - `c0b3a91` (chore: add .gitignore)

## Files Created/Modified
- `pyproject.toml` - Project config with zero runtime deps, dev deps for testing/linting
- `src/cadenza/core/pitch.py` - Pitch frozen dataclass with step/accidental/octave, midi_number, enharmonic_equal
- `src/cadenza/core/duration.py` - Duration frozen dataclass with Fraction arithmetic, from_omn factory
- `src/cadenza/core/interval.py` - Interval frozen dataclass with between() factory for quality computation
- `src/cadenza/core/note.py` - Note and Rest frozen dataclasses, Event type alias
- `src/cadenza/core/phrase.py` - Phrase type alias as tuple[Event, ...]
- `src/cadenza/core/score.py` - Score frozen dataclass with tuple-based voice storage
- `src/cadenza/core/json_codec.py` - JSON encoder/decoder with _type discriminator
- `src/cadenza/omn/errors.py` - ParseError and ParseWarning dataclasses
- `tests/strategies.py` - Hypothesis strategies for Pitch, Duration
- `tests/conftest.py` - Shared fixtures for pitches and durations
- `tests/core/test_pitch.py` - 22 tests for Pitch
- `tests/core/test_duration.py` - 20 tests for Duration
- `tests/core/test_interval.py` - 11 tests for Interval
- `tests/core/test_note.py` - 11 tests for Note/Rest
- `tests/core/test_phrase.py` - 5 tests for Phrase
- `tests/core/test_score.py` - 7 tests for Score
- `tests/core/test_json_codec.py` - 13 tests for JSON codec

## Decisions Made
- Pre-convert objects via _to_serializable() before json.dumps to handle tuples correctly (json.dumps treats tuples as arrays natively, bypassing the custom encoder's default method)
- Score uses tuple[tuple[str, Phrase], ...] internally instead of dict for true immutability and hashability
- JSON codec uses _type discriminator field for polymorphic deserialization of nested types

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed tuple serialization in JSON codec**
- **Found during:** Task 2 (JSON codec implementation)
- **Issue:** json.dumps treats Python tuples as JSON arrays natively, so CadenzaEncoder.default() was never called for top-level tuples (Phrases). Round-trip returned lists instead of tuples.
- **Fix:** Added _to_serializable() helper that recursively converts all cadenza types to plain dicts/lists before json.dumps. to_json() pre-converts via this function.
- **Files modified:** src/cadenza/core/json_codec.py
- **Verification:** Phrase round-trip test passes (returns tuple, not list)
- **Committed in:** a73222a (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Essential for correctness of JSON round-trip. No scope creep.

## Issues Encountered
- System Python on macOS is externally managed (PEP 668); created a venv at .venv/ for development

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All core types are complete and tested, ready for OMN parser (plan 02) and serializer (plan 03)
- cadenza.core package exports everything needed: Pitch, Duration, Interval, Note, Rest, Event, Phrase, Score, to_json, from_json
- Hypothesis strategies available in tests/strategies.py for property-based testing in subsequent plans

---
*Phase: 01-foundation*
*Completed: 2026-03-19*
