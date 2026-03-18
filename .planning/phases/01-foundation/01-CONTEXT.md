# Phase 1: Foundation - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the core data model and OMN parser/serializer. Deliverable: typed Python objects for musical events (Pitch, Duration, Interval, Note, Rest, Phrase, Score) plus lossless round-trip between OMN notation strings and internal representation. No transforms, no analysis, no API — pure foundation. Everything in Phases 2–13 depends on correctness here.

</domain>

<decisions>
## Implementation Decisions

### OMN Sticky Parameters
- Full sticky support: parser inherits duration, dynamic, and articulation from the previous note when omitted
- Matches Opusmodus convention exactly: `(e c4 pp stacc d4 e4)` → d4 and e4 inherit `e`, `pp`, `stacc`
- Internal representation is always fully explicit — stickiness is resolved at parse time, not stored
- Serializer outputs compact OMN (only writes values that differ from the previous note)

### Octave Numbering
- Middle C = C4 (Scientific Pitch Notation / SPN standard)
- Aligns with Music21, MusicXML, and MIDI spec
- This diverges from Opusmodus (which uses C3 for middle C) — document this difference prominently
- Any Opusmodus example strings in docs must note the octave offset

### Rest Encoding
- Negative duration convention: `-e` = eighth rest, `-q` = quarter rest, `-h` = half rest
- Matches Opusmodus exactly
- Rest is modeled as a distinct `Rest` type (not a Note with a null pitch), but serializes as negative duration

### Multi-Voice Score Model
- Score stores voices as a named dict: `{'soprano': Phrase, 'alto': Phrase, 'tenor': Phrase, 'bass': Phrase}`
- Any string key is valid (not limited to SATB names)
- Voice order within the dict is preserved (Python 3.7+ dict ordering)
- Serializes to JSON as `{"voices": {"soprano": [...], "alto": [...]}}`

### Articulation Vocabulary (Phase 1 Core Set)
- Supported: `stacc` (staccato), `ten` (tenuto), `acc` (accent), `leg` (legato), `marc` (marcato), `fermata`, `trill`, `pizz`, `arco`
- Extended articulations (sul-pont, snap-pizz, flutter, harmonics, etc.) deferred to a later phase
- Unknown articulation tokens should produce a clear parse warning (not a hard error) so real-world OMN strings don't break entirely

### Claude's Discretion
- Internal data structure for pitch accidentals (string vs integer — use string: "b", "s", "bb", "ss", "n" for readability)
- Fraction internal representation for duration (use `fractions.Fraction` throughout, never float)
- Python version target (3.11+ recommended for match statements and performance)
- Project package name: `cadenza` with submodules `cadenza.core`, `cadenza.omn`
- Testing framework: pytest with property-based tests via hypothesis for round-trip validation
- Packaging: pyproject.toml with uv/pip installable structure

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### OMN Notation Spec
- `.planning/research/ARCHITECTURE.md` — OMN EBNF grammar, data model sketches, module tree
- `.planning/research/STACK.md` — Technology choices, dependency decisions, data model rationale
- `.planning/research/PITFALLS.md` — Critical pitfalls: enharmonic encoding, float duration errors, rest representation

### Requirements
- `.planning/REQUIREMENTS.md` — CORE-01..10, NOTA-01..07, NOTA-12 (the exact requirements for this phase)
- `.planning/PROJECT.md` — Core value, constraints, key decisions

### External References
- https://opusmodus.com/media/pdf/Introduction%20to%20OMN%20The%20Language.pdf — OMN notation spec (source of truth for syntax)

No external specs on disk yet — project is greenfield.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — this is Phase 1, greenfield

### Established Patterns
- None yet — patterns will be established here and carried forward

### Integration Points
- Phase 2 (Transforms) will import from `cadenza.core` — keep core types stable and well-typed
- Phase 4 (REST API) will import from `cadenza.omn` for parsing — OMN parser must be importable without FastAPI
- Phase 8 (Counterpoint) will produce `Score` objects with named voices — Score model must be defined correctly here

</code_context>

<specifics>
## Specific Ideas

- The OMN format `(e f3 pp stacc)` is the canonical example — parsing this must work perfectly from day one
- Note that all examples in conversation and docs use C4 = middle C (SPN), NOT Opusmodus's C3 convention
- The pitch type must make Eb3 ≠ D#3 by default — this is the single most important design constraint in the entire project
- `enharmonic_equal(Eb3, Ds3)` should return True; `Eb3 == Ds3` should return False

</specifics>

<deferred>
## Deferred Ideas

- Tie notation (`~` suffix) — deferred; likely Phase 2 or addressed when needed
- Grace notes (acciaccatura, appoggiatura) — deferred; Phase 2 or later
- Dynamic hairpin span events — deferred to Phase 6 (Batch Operations)
- Extended articulations (sul-pont, snap-pizz, flutter, harmonics) — deferred to a later phase

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-19*
