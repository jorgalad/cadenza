# Research Summary -- Cadenza

**Project:** Cadenza -- Music Analysis, Transformation, and Generation Library
**Domain:** Symbolic music theory library with notation software integration (Dorico, Sibelius)
**Researched:** 2026-03-18
**Confidence:** MEDIUM-HIGH

---

## Executive Summary

Cadenza is a Python library for symbolic music analysis, transformation, and algorithmic composition, designed to integrate with professional notation software via REST API. The research confirms this is a well-understood domain with stable foundations -- music theory is centuries old, the target formats (OMN, MusicXML, MIDI) are documented, and Python has mature tooling. The scope is large (~491 functions across 15 categories) but the dependency graph is clear: everything flows from a correct data model and OMN parser, through theory libraries (scales, chords, intervals), into transforms, analysis, and generation. The critical path is unambiguous.

The recommended approach is a layered, dependency-free core library with an optional FastAPI shell. The core uses frozen dataclasses (not Pydantic) for zero external dependencies in the foundational layer. Pydantic enters only at the API boundary for request/response validation. The OMN parser should be hand-written recursive descent rather than Lark -- the grammar is simple enough, sticky-parameter state handling is natural in a hand-written parser, and error messages are far better. Music21 is a test-time oracle only, never a runtime dependency. This keeps the core install small and fast.

The primary risks are: (1) scope explosion -- attempting Music21 + Opusmodus parity simultaneously will prevent shipping; (2) the enharmonic catastrophe -- treating pitches as integers destroys musical correctness and forces a rewrite; (3) Dorico API assumptions -- PROJECT.md claims a Python scripting API but evidence points to Lua + JSON-RPC remote control; (4) MusicXML vendor divergence between Dorico and Sibelius exports. All four are preventable with the phased approach and data model decisions described below.

---

## Resolved Stack

These decisions resolve conflicts between research agents:

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| **Core data model** | Frozen dataclasses in `cadenza.core` (zero deps); Pydantic only in `cadenza.api` | Core library must be importable without pydantic. Validation at construction via `__post_init__`. API layer adds Pydantic schemas that delegate to core types. |
| **OMN parser** | Hand-written recursive descent (not Lark) | OMN grammar is simple (durations, pitches, dynamics, articulations). Sticky-parameter state (omit duration = inherit previous) is stateful and awkward in a pure grammar. Hand-written parser gives better error messages ("Expected pitch at position 14, got 'xyz'") and zero external dependency for the parser. |
| **Dorico integration** | REST API is primary; bridge connects to Dorico's Remote Control API (JSON-RPC/WebSocket) | Regardless of whether Dorico scripting is Python or Lua, Cadenza as an HTTP service is language-agnostic. A thin bridge script handles the Dorico<->Cadenza translation. |
| **Music21** | Test-only oracle in dev dependencies, not a runtime dependency | Music21 is 200MB+ with scipy/matplotlib. Use it to validate Cadenza's music theory output in pytest. Optional `cadenza.compat.music21` for users who want interop. |

**Core dependencies (always installed):** None for `cadenza.core`; `mido` for MIDI I/O; `lxml` for MusicXML I/O.

**Optional dependencies:** `fastapi` + `uvicorn` for API server; `music21` for test oracle and optional compat.

**Tooling:** Python 3.12+, uv (package management), pytest + hypothesis (testing), ruff (lint/format), mypy (type checking).

---

## Feature Scope

**15 categories, ~491 functions, ~145 scale/chord definitions**

| # | Category | Functions | Phase | Priority |
|---|----------|-----------|-------|----------|
| 1 | Notation / Parsing | ~33 | 1 | MUST |
| 2 | Pitch Operations | ~25 | 1 | MUST |
| 3 | Rhythm Operations | ~30 | 1 | MUST |
| 4 | Melodic Transforms | ~25 | 2 | MUST |
| 5 | Harmonic Analysis | ~23 | 3 | SHOULD |
| 6 | Counterpoint | ~20 | 4 | SHOULD |
| 7 | Voice Leading | ~18 | 4 | SHOULD |
| 8 | Scale/Mode Library | ~115 | 2 | MUST |
| 9 | Chord Library | ~71 | 2 | MUST |
| 10 | Set Theory | ~19 | 3 | SHOULD |
| 11 | Serial/12-Tone | ~18 | 3 | SHOULD |
| 12 | Pattern Generation | ~30 | 5 | DEFER |
| 13 | Batch Operations | ~16 | 3 | SHOULD |
| 14 | Algorithmic Composition | ~28 | 5 | DEFER |
| 15 | Analysis | ~20 | 3 | SHOULD |

**Critical path:** Notation/Parsing -> Pitch/Rhythm/Duration/Interval model -> Scale + Chord libraries -> Transforms -> Analysis -> Counterpoint -> Generation

**MVP (notation software cares):** Phases 1-2 deliver OMN parsing, pitch/rhythm transforms, scale/chord libraries, MusicXML/MIDI I/O, and the REST API. This is the minimum to demonstrate value to Dorico/Sibelius teams.

---

## Architecture in One Page

```
                    +------------------------------------------+
                    |         REST API (FastAPI, optional)      |
                    |   Pydantic request/response schemas       |
                    |   /v1/transform, /analyze, /generate, /io |
                    +------------------------------------------+
                                        |
                    +------------------------------------------+
                    |        OMN Parse/Serialize Boundary       |
                    |   parse_omn(str) -> Phrase                |
                    |   to_omn(Phrase) -> str                   |
                    +------------------------------------------+
                                        |
          +--------------------+--------------------+--------------------+
          | Transforms         | Analysis           | Generation         |
          | retrograde         | key detection      | counterpoint       |
          | inversion          | chord ID           | voice leading      |
          | transposition      | roman numerals     | Euclidean rhythms  |
          | augmentation       | interval vectors   | serial/12-tone     |
          +--------------------+--------------------+--------------------+
                                        |
                    +------------------------------------------+
                    |     Core Music Theory Engine              |
                    |  Pitch | Interval | Scale | Key | Chord  |
                    |  Duration | Meter | MusicalContext        |
                    +------------------------------------------+
                                        |
          +--------------------+--------------------+--------------------+
          | OMN Parser         | MIDI I/O (mido)    | MusicXML (lxml)    |
          | (hand-written)     |                    |                    |
          +--------------------+--------------------+--------------------+
                                        |
                    +------------------------------------------+
                    |   Data Model (frozen dataclasses)         |
                    |   Pitch | Duration | Note | Rest | Chord  |
                    |   Phrase | Voice | Part | Score           |
                    |   NO external deps in this layer          |
                    +------------------------------------------+
```

**Key patterns:**
1. **Pure functions on immutable data.** Every transform takes a Phrase, returns a new Phrase. No mutation, no side effects. Thread-safe by construction.
2. **Parse at boundary, typed everywhere else.** OMN strings exist only at API edges. Internal functions accept and return typed objects.
3. **Registry pattern** for scales (80+), chords (45+ types), articulations. Extensible via `register_scale()` etc.
4. **Explicit MusicalContext** for key/meter-aware operations. No global state.
5. **API versioning from day one** (`/v1/` prefix). DAW bridges cannot be updated quickly.

**Anti-patterns to avoid:**
- Mutable shared state (kills concurrency)
- God-object Event class (use Note | Rest | Chord union)
- String-based pitch manipulation (use typed Pitch objects)
- Over-abstracting I/O (MusicXML, MIDI, OMN are too different for a generic adapter)

---

## Top 5 Pitfalls to Avoid

### 1. The Enharmonic Catastrophe (CRITICAL)
Representing pitches as MIDI integers destroys the distinction between Eb4 and D#4. Every downstream operation (transposition, key detection, MusicXML export, display in Dorico) produces wrong results. **Prevention:** Pitch is always `(name: A-G, accidental: -2..+2, octave: int)`. MIDI number is a derived property. Interval arithmetic uses `(generic_size, quality)` pairs.

### 2. Duration as Floating Point (CRITICAL)
Dotted notes and tuplets produce fractions that accumulate IEEE 754 rounding errors. Measures stop summing to the correct beat total. **Prevention:** `fractions.Fraction` for ALL internal duration arithmetic. Quarter note = `Fraction(1, 4)`. Convert to float only at MIDI export boundary.

### 3. Scope Explosion (CRITICAL)
Attempting ~491 functions simultaneously means nothing ships. **Prevention:** Tiered implementation with gates. Phase 1 (core model + parser + basic transforms) must ship and be tested with actual Dorico integration before Phase 2 begins. Each phase validates the architecture.

### 4. Dorico API Assumptions (MODERATE)
PROJECT.md states "Dorico has a Python scripting API." Evidence from training data says Dorico uses Lua scripting + JSON-RPC remote control. Building a Python-native Dorico plugin that cannot run inside Dorico wastes effort. **Prevention:** Design REST API as primary integration (language-agnostic). Verify Dorico's actual API from Steinberg documentation before building any bridge code.

### 5. MusicXML Vendor Divergence (MODERATE)
Dorico and Sibelius export MusicXML differently (beam grouping, voice numbering, chord symbols, tuplet display). Code that works with one breaks on the other. **Prevention:** Test with real exports from both programs. Implement a normalization layer. Be defensive -- every element is optional. Maintain a "known quirks" registry per vendor.

---

## Roadmap Implications

### Phase 1: Core Data Model + OMN Parser + Basic I/O
**Rationale:** Everything depends on this. The data model is the foundation; get it wrong and everything must be rewritten.
**Delivers:** Frozen dataclass model (Pitch, Duration, Note, Rest, Chord, Phrase, Voice, Part, Score), hand-written OMN parser with sticky-parameter support, OMN serializer, basic MIDI I/O (mido), basic MusicXML I/O (lxml subset).
**Features:** Category 1 (Notation/Parsing) table stakes, Category 2 (Pitch Ops) basics, Category 3 (Rhythm Ops) basics.
**Avoids:** Pitfalls 1 (enharmonic), 2 (float duration), 3 (scope). Must get the compound Pitch type and Fraction-based Duration right from day one.
**Research needed:** No -- well-documented patterns. OMN grammar is simple.

### Phase 2: Theory Libraries + Core Transforms + REST API
**Rationale:** Scales, chords, and basic transforms are the minimum to demonstrate value to notation software teams. The REST API makes it callable from any language.
**Delivers:** Scale/mode library (80+ scales), chord library (45+ types with identification), interval model, melodic transforms (retrograde, inversion, transposition, augmentation, rotation), rhythmic transforms, FastAPI application with `/v1/` routes.
**Features:** Categories 4 (Melodic Transforms), 8 (Scales), 9 (Chords) table stakes. REST API wrapping Phase 1+2.
**Avoids:** Pitfall 3 (scope) -- this is the MVP gate. Ship this and test with Dorico before proceeding.
**Research needed:** No -- standard music theory, well-established patterns.

### Phase 3: Analysis + Set Theory + Batch Operations
**Rationale:** Analysis (key detection, chord ID, Roman numerals) and set theory are the next dependency tier. Batch operations add immediate DAW-user value.
**Delivers:** Key detection (Krumhansl-Schmuckler and alternatives), chord identification, Roman numeral analysis, pitch-class set operations, Forte numbers, batch articulation/dynamic application.
**Features:** Categories 5 (Harmonic Analysis), 10 (Set Theory), 11 (Serial/12-Tone), 13 (Batch Ops), 15 (Analysis) table stakes.
**Avoids:** Pitfall 5 (MusicXML vendor divergence) -- by this point, real Dorico/Sibelius exports should be in the test suite.
**Research needed:** YES -- key detection algorithms have multiple implementations with different accuracy profiles. Phase research should compare Krumhansl-Schmuckler, Bellman-Budge, Temperley, and Aarden-Essen weight profiles.

### Phase 4: Voice Leading + Counterpoint
**Rationale:** Counterpoint depends on voice leading, which depends on harmonic analysis and chord library. Cannot be built earlier.
**Delivers:** Voice leading engine (smooth voicing, parallel 5th/8th detection), species counterpoint validation and generation (Species I through III initially).
**Features:** Categories 6 (Counterpoint), 7 (Voice Leading) table stakes.
**Avoids:** Pitfall from PITFALLS.md #9 (counterpoint rule explosion) -- start with Species I only, use configurable rulesets with severity levels.
**Research needed:** YES -- counterpoint generation via constraint satisfaction is a well-studied but non-trivial problem. Phase research should evaluate backtracking vs. constraint propagation approaches.

### Phase 5: Algorithmic Composition + Pattern Generation
**Rationale:** This is the "Opusmodus parity" tier. Depends on everything above. Defer until the foundation is proven.
**Delivers:** Markov chains, L-systems, cellular automata, Euclidean rhythms, isorhythm, tendency masks, stochastic generation tools.
**Features:** Categories 12 (Pattern Generation), 14 (Algorithmic Composition).
**Research needed:** Partially -- individual algorithms are well-documented in computer music literature, but the constraint/mapping tools (tonality-map, ambitus-map) that make raw output musical need design research.

### Phase 6: DAW Integration Bridges + Advanced Analysis
**Rationale:** Build bridges only after the API is stable and tested.
**Delivers:** Dorico bridge (connects to Remote Control API), Sibelius bridge (ManuScript plugin + companion app), advanced analysis (motivic search, form detection, Schenkerian reduction).
**Features:** DAW integration, Category 15 differentiators.
**Research needed:** YES -- Dorico Remote Control API protocol details must be verified from Steinberg documentation. Sibelius ManuScript capabilities need investigation. This phase has the most uncertainty.

### Phase Ordering Rationale
- Phases 1-2 follow the strict dependency graph: data model -> parser -> theory libraries -> transforms -> API.
- Phase 2 is the MVP gate. If the architecture cannot support scales + chords + transforms + REST API cleanly, it will not scale to 491 functions.
- Phase 3 (analysis) before Phase 4 (counterpoint) because counterpoint needs harmonic context.
- Phase 5 (generation) is deferred because it is additive -- it does not validate the architecture, it exercises it.
- Phase 6 (DAW bridges) last because the API must be stable before external consumers depend on it, and because Dorico/Sibelius API details need verification.

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 3:** Key detection algorithm selection (multiple competing approaches with different accuracy)
- **Phase 4:** Constraint satisfaction approach for counterpoint generation
- **Phase 6:** Dorico and Sibelius API verification (CRITICAL -- cannot design bridge without knowing the actual protocol)

**Phases with standard patterns (skip research):**
- **Phase 1:** Data model and parser -- well-documented, established patterns
- **Phase 2:** Transforms and theory libraries -- centuries-old music theory, straightforward implementation
- **Phase 5:** Algorithmic composition algorithms -- well-documented in computer music literature

---

## Open Questions Requiring Verification

These could not be resolved from training data and must be checked before or during implementation:

| Question | Impact | How to Verify |
|----------|--------|---------------|
| Does Dorico have Python scripting, or only Lua + JSON-RPC remote control? | Phase 6 bridge design | Check Steinberg documentation for Dorico 5/6 |
| Has FastAPI released 1.0, or is it still 0.x? | Pin version in pyproject.toml | Check PyPI |
| Is uv's lock file format stable? | Build reproducibility | Check uv docs |
| Sibelius REST plugin API in 2024+ versions? | Phase 6 bridge design | Check Avid documentation |
| Python 3.13 stable? | Minimum Python version decision | Check python.org |
| Exact OMN grammar spec from Opusmodus | Parser correctness | Fetch current Opusmodus PDF docs |
| MusicXML 4.0 vs 4.1 -- any breaking changes? | MusicXML I/O layer | Check W3C MusicXML spec |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Well-established Python libraries. Only version numbers need verification. |
| Features | MEDIUM-HIGH | Feature list based on Opusmodus + Music21 training data. Function names may differ from current versions. Dependency graph is HIGH confidence (follows music theory logic). |
| Architecture | HIGH | Layered library + optional API is a proven pattern. Pure functions on immutable data is well-understood. |
| Pitfalls | HIGH | Music theory pitfalls (enharmonic, float duration) are timeless. Dorico API caveat is the main uncertainty. |

**Overall confidence: MEDIUM-HIGH.** The domain is stable and well-understood. The main risks are scope management and DAW API verification, not technical uncertainty.

### Gaps to Address

- **Dorico API verification** must happen before Phase 6 planning. If Dorico truly has Python scripting now, integration is simpler than assumed.
- **OMN grammar completeness** -- the parser must handle all Opusmodus OMN constructs, not just the common ones. Need to verify against current Opusmodus documentation.
- **MusicXML vendor-specific quirks** -- need real Dorico and Sibelius MusicXML exports as test fixtures. Cannot be resolved from documentation alone.
- **Counterpoint constraint solver** -- Phase 4 should evaluate whether Python's standard library is sufficient or whether a constraint library (python-constraint, or-tools) is needed.

---

## Sources

### Primary (HIGH confidence -- stable domain knowledge)
- Music theory foundations (counterpoint rules, set theory, interval classification) -- centuries-old, version-independent
- Forte, Allen. *The Structure of Atonal Music* (1973) -- set theory, Forte number catalogue
- Krumhansl, Carol. *Cognitive Foundations of Musical Pitch* (1990) -- key detection algorithms
- Toussaint, Godfried. "The Euclidean Algorithm Generates Traditional Musical Rhythms" (2005)
- Fux, Johann Joseph. *Gradus ad Parnassum* (1725) -- species counterpoint rules

### Secondary (MEDIUM confidence -- training data, not live-verified)
- Music21 API (web.mit.edu/music21) -- stable library, API unlikely to have changed drastically
- Opusmodus documentation (opusmodus.com) -- function names and OMN syntax
- FastAPI / Pydantic v2 patterns -- well-established, version numbers need checking
- MusicXML 4.0 specification

### Tertiary (LOW confidence -- needs verification)
- Dorico Remote Control API protocol details -- may have changed in Dorico 5/6
- Sibelius ManuScript capabilities and REST plugin API
- Exact current versions of all Python packages

---
*Research completed: 2026-03-18*
*Ready for roadmap: yes*
