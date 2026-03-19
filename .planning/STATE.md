---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: completed
stopped_at: Phase 6 context gathered
last_updated: "2026-03-19T20:06:26.137Z"
last_activity: 2026-03-19 -- Completed 05-02 Key Detection & Harmonic Analysis (detect_key, roman_numeral, harmonic_rhythm, borrowed chords)
progress:
  total_phases: 13
  completed_phases: 5
  total_plans: 12
  completed_plans: 12
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** A notation software user can select any musical phrase, send it to Cadenza, and receive back a musically correct transformation or harmonization -- without needing to understand the theory behind it.
**Current focus:** Phase 5: Harmonic Analysis

## Current Position

Phase: 5 of 13 (Harmonic Analysis) -- COMPLETE
Plan: 2 of 2 in current phase
Status: Phase 5 complete
Last activity: 2026-03-19 -- Completed 05-02 Key Detection & Harmonic Analysis (detect_key, roman_numeral, harmonic_rhythm, borrowed chords)

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: 4 min
- Total execution time: 0.55 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3/3 | 18 min | 6 min |
| 02-transforms | 1/3 | 3 min | 3 min |

**Recent Trend:**
- Last 5 plans: 01-01 (6 min), 01-02 (6 min), 01-03 (6 min), 02-02 (3 min)
- Trend: Improving

*Updated after each plan completion*
| Phase 02-transforms P01 | 3 | 2 tasks | 5 files |
| Phase 02-transforms P03 | 3 | 2 tasks | 3 files |
| Phase 03-01 P01 | 6 | 2 tasks | 7 files |
| Phase 03 P02 | 4 | 2 tasks | 3 files |
| Phase 04-01 | 3 | 2 tasks | 12 files |
| Phase 04 P02 | 4 | 2 tasks | 6 files |
| Phase 05-01 | 4 | 2 tasks | 4 files |
| Phase 05-02 | 5 | 2 tasks | 5 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Roadmap: Frozen dataclasses for core data model (zero external deps), Pydantic only at API boundary
- Roadmap: Hand-written recursive descent OMN parser (not Lark) for better error messages
- Roadmap: REST API introduced at Phase 4 (after core + transforms + libraries), expanded incrementally
- Roadmap: MusicXML/MIDI I/O deferred to Phase 12 (not bundled with parser phase) to keep foundation focused
- 01-01: Pre-convert objects via _to_serializable() before json.dumps to handle tuple serialization
- 01-01: Score uses tuple[tuple[str, Phrase], ...] internally for true immutability and hashability
- 01-01: JSON codec uses _type discriminator field for polymorphic deserialization
- 01-02: Word-based tokenizer (split on whitespace) for simpler disambiguation of e/f/s ambiguity
- 01-02: Serializer does not track None dynamic or empty articulations as sticky state changes (OMN cannot unset these)
- 01-02: Chord tokens deferred -- tokenized as single PITCH, parser uses first pitch with warning
- [Phase 01-03]: OMN round-trip tests compare against sticky-resolved expected values (None dynamics inherit from previous note)
- 02-02: Keep original OMN metadata (base/dots/tuplet) as hint after duration scaling; fraction is source of truth
- 02-02: Float ratios converted to Fraction via limit_denominator(1000) to avoid drift
- [Phase 02-01]: Used MIDI-based lookup tables for from_midi and enharmonic_respell
- [Phase 02-01]: Interval-based spelling preservation in _transpose_pitch: derive letter from generic interval, accidental from MIDI difference
- [Phase 02-03]: mirror uses full_retrograde per CONTEXT.md palindrome definition
- [Phase 02-03]: interpolation uses chromatic passing notes via from_midi; sharps ascending, flats descending
- [Phase 02-03]: omit requires exactly one of n or predicate, raises ValueError otherwise
- [Phase 03-01]: round() for octave computation in _build_pitch to handle boundary cases like Bb
- [Phase 03-01]: _infer_degree_steps for custom scales uses chromatic-to-diatonic semitone mapping
- [Phase 03-01]: Phase 2 stub tests updated from NotImplementedError to functional assertions
- [Phase 03]: Chord registry stores dual encoding (semitones + degree steps) for correct enharmonic spelling
- [Phase 03]: Duplicated _build_pitch in chords.py rather than importing private function from scales.py
- [Phase 03]: aug6_chord and neapolitan_chord use key-relative construction, not chord registry lookup
- [Phase 04-01]: FastAPI as optional [api] extra -- core library stays zero-dep
- [Phase 04-01]: App factory pattern (create_app) for testability and multiple instance support
- [Phase 04-01]: Compact string parsers in api.parsing bridge human-readable pitch/interval strings to core types
- [Phase 04-01]: Three-layer exception handler: CadenzaAPIError -> specific code, ParseError -> INVALID_CN, ValueError -> INVALID_INPUT
- [Phase 04]: Thin route handlers: all business logic stays in cadenza.transforms/theory, routes only parse CN and serialize responses
- [Phase 04]: Theory endpoints serialize pitch tuples as space-separated CN strings, not full phrase notation
- [Phase 05-01]: Brute-force 12-root x registry matching for chord identification (simple, correct, fast enough)
- [Phase 05-01]: Complexity ranking: triads(0) > sevenths/sus(1) > extended(2+) for disambiguation
- [Phase 05-01]: Single-digit octave in chord symbol regex to separate octave from numeric quality
- [Phase 05-01]: Multi-strategy quality resolution for aliases and case variations
- [Phase 05-02]: Krumhansl-Kessler profiles for major/natural_minor; synthetic weighted profiles for harmonic/melodic minor
- [Phase 05-02]: max(0.0, r) for confidence clipping; uniform scale distributions yield ~0.75 correlation
- [Phase 05-02]: Parallel key comparison for borrowed chord detection (bVII, bIII, bVI)
- [Phase 05-02]: Sliding window with consecutive-change confirmation for modulation detection

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 5 (Harmonic Analysis): Key detection algorithm selection needs research during planning
- Phase 8 (Counterpoint): Constraint satisfaction approach needs research during planning
- Phase 12 (I/O Expansion): MusicXML vendor divergence between Dorico/Sibelius requires real test fixtures

## Session Continuity

Last session: 2026-03-19T20:06:26.130Z
Stopped at: Phase 6 context gathered
Resume file: .planning/phases/06-batch-operations-analysis/06-CONTEXT.md
