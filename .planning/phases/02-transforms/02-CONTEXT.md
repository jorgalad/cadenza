# Phase 2: Transforms - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement all pitch, rhythm, and melodic transformation functions that operate on Phrase objects and return new Phrase objects. Pure functions (not methods), immutable inputs, immutable outputs. No analysis, no harmonic context — pure structural transformations. 29 requirements across 3 categories (PTCH, RHYT, MELO).

</domain>

<decisions>
## Implementation Decisions

### Transposition Modes
- Two modes, two functions:
  - `chromatic_transpose(phrase, interval: Interval) -> Phrase` — shifts each note by the given Interval; spelling follows the interval's direction (minor third up from C = Eb, not D#)
  - `diatonic_transpose(phrase, n: int, scale) -> Phrase` — moves each note by N scale degrees within a given scale; stub until Phase 3 scale library, but the function signature is defined now
- Enharmonic spelling for chromatic transposition: follow the interval's direction — augmented intervals prefer sharps, diminished/minor prefer flats for downward motion. Deterministic, no caller configuration needed.
- Success criterion 1: "Transposing a C major scale up by a minor third produces Eb major" — this is satisfied by `chromatic_transpose` with an `Interval('m', 3, 1)`

### Retrograde Flavors
- Two named functions:
  - `pitch_retrograde(phrase) -> Phrase` — reverses pitch sequence only; each note keeps its original duration but gets the pitch of the corresponding note from the reversed pitch list
  - `full_retrograde(phrase) -> Phrase` — reverses the entire event sequence (pitch + rhythm together, the classical definition used in serial music)
- MELO-01 maps to `pitch_retrograde`, MELO-02 (retrograde-inversion) = `pitch_retrograde` then `invert`

### Melodic Inversion
- `invert(phrase, axis: Pitch | None = None) -> Phrase`
- Default axis: first note of the phrase (stays fixed, all subsequent notes mirrored around it)
- Caller can override: `invert(phrase, axis=Pitch('g', 'n', 4))`
- Inversion is chromatic: each interval from the axis is reflected exactly (a minor third above becomes a minor third below)

### Claude's Discretion
- Module layout: `cadenza/transforms/pitch.py`, `cadenza/transforms/rhythm.py`, `cadenza/transforms/melodic.py` with a `cadenza/transforms/__init__.py` exporting all functions
- Diatonic transpose stub: raise `NotImplementedError("Diatonic transpose requires Phase 3 scale library")` until Phase 3
- Rotation direction: positive N = rotate left (first N events move to end), negative N = rotate right
- Augmentation/diminution ratio type: accept `fractions.Fraction` or `int` or `float` (convert float to Fraction internally)
- Quantization grid: accept Duration objects or OMN duration strings

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core types (Phase 1 foundation)
- `src/cadenza/core/pitch.py` — Pitch type, STEP_INDEX, enharmonic_equal, midi_number
- `src/cadenza/core/duration.py` — Duration type, Fraction arithmetic
- `src/cadenza/core/interval.py` — Interval type, between(), semitones property
- `src/cadenza/core/note.py` — Note, Rest, Event union type
- `src/cadenza/core/phrase.py` — Phrase type (tuple of Events)

### Requirements
- `.planning/REQUIREMENTS.md` — PTCH-01..09, RHYT-01..05/07..09, MELO-01..12

### Project context
- `.planning/PROJECT.md` — Core value and constraints
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions carried forward

No external specs — all transform semantics are standard music theory.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Interval.between(p1, p2)` — already implemented; transposition can use this to compute and verify intervals
- `Interval.semitones` property — needed for chromatic transposition implementation
- `Pitch.midi_number` property — available for enharmonic comparisons
- `Pitch.pitch_class` property — available for set theory operations (later phases)
- `Phrase` is `tuple[Event, ...]` — transforms return new tuples, no mutation needed
- `Duration.from_omn()` and `Duration` arithmetic already handle Fraction correctly

### Established Patterns
- Pure functions: all Phase 1 operations are module-level functions, not methods — maintain this
- Frozen dataclasses: all types are immutable — transforms always return new objects
- TDD: tests written first (RED → GREEN), then implementation
- Zero runtime dependencies: `cadenza.transforms` must also have zero runtime deps (stdlib only)

### Integration Points
- Phase 3 (Theory Libraries) will add `Scale` type — `diatonic_transpose` stub must accept it when it arrives
- Phase 4 (REST API) will expose all transform functions as endpoints — keep function signatures simple and JSON-serializable
- Phase 6 (Batch Operations) will apply transforms to note sequences — batch ops import from `cadenza.transforms`

</code_context>

<specifics>
## Specific Ideas

- The `(e f3 pp stacc)` OMN notation is the canonical example; transform functions should accept Phrases parsed from OMN strings and return Phrases that can be serialized back to OMN
- Transposing "C major scale up a minor third" is the canonical test: `[c4, d4, e4, f4, g4, a4, b4]` → `[eb4, f4, g4, ab4, bb4, c5, d5]` — all spelled with flats, not sharps

</specifics>

<deferred>
## Deferred Ideas

- Diatonic transposition (full implementation) — deferred to Phase 3 when Scale library exists
- Interpolation rules (chromatic vs diatonic passing notes) — deferred; not discussed, planner uses chromatic as default
- Omission predicates (lambda vs named conditions) — deferred; not discussed, planner implements both

</deferred>

---

*Phase: 02-transforms*
*Context gathered: 2026-03-19*
