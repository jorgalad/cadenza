# Phase 3: Theory Libraries - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the Scale and Chord libraries: a named registry of all standard Western and curated non-Western scales/modes plus a complete chord library with inversions, diatonic chords, secondary dominants, and augmented sixth chords. All functions return correctly-spelled `Pitch` objects using the existing `cadenza.core` types. This phase also delivers the `Scale` type that unblocks `diatonic_transpose` (Phase 2 stub). No harmonic analysis, no voice leading, no Roman numeral labeling — pure pitch retrieval from theory constructs.

</domain>

<decisions>
## Implementation Decisions

### Scale Name Vocabulary & Aliases
- **Aliases resolve:** "natural minor", "aeolian", and "minor" all return the same scale — one canonical name per scale internally, multiple lookup keys accepted
- **Case-sensitive:** Callers must pass lowercase canonical names (e.g., `'dorian'`, not `'Dorian'`). No case normalization.
- **Separate args signature:** `get_scale(root: Pitch, name: str) -> tuple[Pitch, ...]` — root is a typed `Pitch`, name is a lowercase string. Consistent with Phase 1/2 patterns.
- **User-extensible registry:** `register_scale(name: str, intervals: list[int]) -> None` registers a custom scale by name. Once registered, `get_scale(root, name)` works with it. Satisfies SCAL-08 and makes the registry a live object.
- **SCAL-09 return type:** Returns a `tuple[Pitch, ...]` of the scale pitches within a single octave (ascending). Octave of the root pitch determines the starting point.

### Non-Western Scale Scope
- **Curated named set (~15–20 scales):** Hand-picked coverage across major traditions:
  - Arabic/maqam-approximated: Hijaz (1, b2, 3, 4, 5, b6, b7), Hijaz Kar, Rast (approximate), Bayati (approximate)
  - Eastern European: Hungarian minor (1, 2, b3, #4, 5, b6, 7), Romanian (1, 2, b3, #4, 5, 6, b7), Ukrainian Dorian
  - Neapolitan major, Neapolitan minor
  - Persian (1, b2, 3, 4, b5, b6, 7)
  - Phrygian dominant (1, b2, 3, 4, 5, b6, b7) — also known as Spanish Gypsy
  - Double harmonic (Byzantine scale)
  - Others at Claude's discretion to reach ~15–20 total
- **12-TET approximations only, documented:** Quarter-tone maqam variants are explicitly out of scope for v1. Where a non-Western scale requires microtones for authentic rendering, the 12-TET approximation is used and this limitation is noted in docstrings.

### Chord Symbol Format
- **Lead-sheet style, case-sensitive:** Industry standard naming that every notation app and jazz musician expects:
  - `'maj'`, `'m'` (or `'min'`), `'dim'`, `'aug'` — triads
  - `'7'` = dominant seventh (C7 = C-E-G-Bb), `'maj7'`, `'m7'`, `'m7b5'` (half-dim), `'dim7'`, `'mM7'`, `'aug7'`
  - Extended: `'9'`, `'maj9'`, `'m9'`, `'11'`, `'maj11'`, `'13'`, `'maj13'`
  - Added/suspended: `'add9'`, `'add11'`, `'sus2'`, `'sus4'`
  - Aliases welcome (e.g., `'min'` → `'m'`, `'M7'` → `'maj7'`) at Claude's discretion
- **Mirror scale API signature:** `get_chord(root: Pitch, symbol: str, inversion: int = 0) -> tuple[Pitch, ...]`
  - `inversion=0` = root position, `inversion=1` = first inversion, etc.
  - Covers CHRD-01..05 in one function
- **`'7'` = dominant seventh:** No ambiguity — this is the universal lead-sheet convention

### Special Chord Depth
- **Secondary dominants (CHRD-07):** `secondary_dominant(degree: int, key_root: Pitch, key_name: str) -> tuple[Pitch, ...]` — returns pitches only (the V7 chord that tonicizes the given scale degree). No resolution target or Roman numeral context — that belongs in Phase 5 (Harmonic Analysis).
- **Augmented sixth chords (CHRD-08):** Key-context signature — `aug6_chord(aug6_type: str, key_root: Pitch, key_name: str) -> tuple[Pitch, ...]` where `aug6_type` is `'italian'`, `'french'`, or `'german'`. These chords are inherently key-relative; root-based lookup would be semantically misleading.
- **Neapolitan chord (CHRD-08):** `neapolitan_chord(key_root: Pitch, key_name: str) -> tuple[Pitch, ...]` — the bII chord in root position, returning flat-2nd scale degree pitches.

### Diatonic Chords (CHRD-06)
- `diatonic_chords(scale_root: Pitch, scale_name: str, quality: str = 'triad') -> tuple[tuple[Pitch, ...], ...]`
- `quality` = `'triad'` or `'seventh'` — returns all diatonic triads or seventh chords built on each scale degree
- Returns a tuple of 7 chord-tuples (one per scale degree)

### The Scale Type
- `Scale` is a named dataclass (frozen): `Scale(root: Pitch, name: str, pitches: tuple[Pitch, ...], intervals: tuple[int, ...])`
- `get_scale` returns a `Scale` object (not a bare tuple) so that `diatonic_transpose` can use `scale.pitches` and `scale.intervals` to navigate by degree
- This resolves the Phase 2 `diatonic_transpose` stub: the stub's signature `diatonic_transpose(phrase, n, scale)` accepts a `Scale` object

### Claude's Discretion
- Internal registry data structure (dict of name → interval pattern)
- Chord registry architecture (similar to scale registry)
- Exact alias mappings within the registry
- Which additional non-Western scales to include to reach the ~15–20 target
- `cadenza.theory` module layout: `cadenza/theory/scales.py`, `cadenza/theory/chords.py`, `cadenza/theory/__init__.py`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core types (Phase 1 foundation)
- `src/cadenza/core/pitch.py` — Pitch type, STEP_INDEX, enharmonic_equal, midi_number (Scale pitches use this throughout)
- `src/cadenza/core/interval.py` — Interval type, semitones property (interval patterns that define scales/chords)
- `src/cadenza/core/note.py` — Note, Rest, Event union type
- `src/cadenza/core/phrase.py` — Phrase type

### Phase 2 stubs waiting for Phase 3
- `src/cadenza/transforms/pitch.py` — `diatonic_transpose` stub (line ~96), `pitch_in_scale` stub, `nearest_in_scale` stub — all raise `NotImplementedError("Diatonic transpose requires Phase 3 scale library")`. Phase 3 must define `Scale` so these can be completed.

### Requirements
- `.planning/REQUIREMENTS.md` — SCAL-01..12, CHRD-01..09

### Project context
- `.planning/PROJECT.md` — Core value and constraints (zero runtime deps, enharmonic correctness)
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions (Pitch type conventions, SPN C4=middle C)
- `.planning/phases/02-transforms/02-CONTEXT.md` — Phase 2 decisions (diatonic_transpose signature)

No external specs — all scale/chord theory semantics are standard music theory. The canonical sources are:
- Standard Western music theory: Aldwell & Schachter "Harmony and Voice Leading" (scale/chord definitions)
- Lead-sheet chord symbols: standard jazz notation convention
- Mode names: standard church mode names (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Pitch` type (`src/cadenza/core/pitch.py`) — Scale pitches are `Pitch` objects. The `midi_number` property and `STEP_INDEX` dict are key for computing correct enharmonic spelling in scale construction.
- `Interval.between(p1, p2)` and `Interval.semitones` — Available for computing interval patterns from pitch sequences and vice versa.
- `dataclasses.replace()` pattern — Phase 1/2 use `dataclasses.replace()` for immutable copies; the `Scale` frozen dataclass should follow the same pattern.
- `fractions.Fraction` — Not needed for scale/chord pitch tuples, but already established as the Cadenza precision convention.

### Established Patterns
- **Pure functions, module-level:** All Phase 1/2 operations are module-level functions, not methods — maintain this for `get_scale`, `get_chord`, etc.
- **Frozen dataclasses:** All types are `@dataclass(frozen=True, slots=True)` — `Scale` should follow this pattern.
- **Zero runtime dependencies:** `cadenza.theory` must use only Python stdlib (same constraint as `cadenza.core` and `cadenza.transforms`).
- **TDD:** Tests written first (RED → GREEN), then implementation.
- **Tuple return types:** All sequences returned as `tuple[...]`, never `list[...]`.

### Integration Points
- `diatonic_transpose` in `src/cadenza/transforms/pitch.py` (line ~96) — directly imports from `cadenza.theory.scales` once Phase 3 ships. The stub signature `diatonic_transpose(phrase, n: int, scale: Any)` will be updated to `scale: Scale`.
- `pitch_in_scale` and `nearest_in_scale` stubs (~line 200+) in `src/cadenza/transforms/pitch.py` — will be completed with Phase 3 `Scale` type.
- Phase 5 (Harmonic Analysis) will import chord functions from `cadenza.theory.chords` for chord identification.
- Phase 4 (REST API) will expose all `cadenza.theory` functions as endpoints.

</code_context>

<specifics>
## Specific Ideas

- The canonical correctness test: `get_scale(Pitch('d','n',4), 'dorian')` must return `(D4, E4, F4, G4, A4, B4, C5)` — spelled with naturals, not with sharps or flats
- Lead-sheet convention is the reference for all chord symbols — if a jazz musician would write it on a chart, it should work
- The `Scale` type is the unlocking artifact for Phase 2 stubs — the `diatonic_transpose` function in `pitch.py` is explicitly waiting for it

</specifics>

<deferred>
## Deferred Ideas

- Full Arabic maqam system with quarter-tones — requires microtonal pitch model (v2, out of scope for 12-TET v1)
- Chord symbol parsing from a string like `"Cmaj7"` (parsing root + quality from a combined string) — deferred; the separate-args `get_chord(root, symbol)` API is sufficient for Phase 3
- Scale-aware pitch spelling correction (re-spelling a pitch to match the key signature) — deferred to Phase 5 harmonic analysis
- Chord progressions as first-class objects — deferred; Phase 3 returns individual chords only

</deferred>

---

*Phase: 03-theory-libraries*
*Context gathered: 2026-03-19*
