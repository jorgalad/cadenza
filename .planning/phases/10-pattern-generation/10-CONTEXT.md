# Phase 10: Pattern Generation - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 10 delivers eight pattern generation capabilities:

1. **Isorhythm (PATT-01)** — generate isorhythmic patterns from a talea (rhythm) and color (pitch sequence), cycling independently until both align.
2. **Ostinato (PATT-02)** — loop a phrase with optional variation.
3. **Apply rhythm (PATT-03)** — apply a rhythmic bitmap to a pitch sequence, separating rhythm from pitch.
4. **Binary rhythm (PATT-04)** — generate a rhythm pattern from an integer bit representation.
5. **Rhythmic canon (PATT-05)** — generate canon voices from a phrase with time offsets.
6. **Hocket (PATT-06)** — distribute notes of a phrase across multiple voices.
7. **Accent patterns (PATT-07)** — mark every Nth note as accented.
8. **Euclidean rhythm (RHYT-06)** — distribute N beats over M slots using Bjorklund's algorithm.

New module: `src/cadenza/patterns/` package. Depends on Phase 1 (`Phrase`, `Note`, `Rest`, `Duration`, `Pitch`, `Score`).

</domain>

<decisions>
## Implementation Decisions

### Area 1: Euclidean / Binary Rhythm Output

- **`euclidean_rhythm(n, m) -> tuple[bool, ...]`** — hit/rest bitmap of length `m`, with `n` hits distributed as evenly as possible (Bjorklund's algorithm). Duration-agnostic.
- **`binary_rhythm(n) -> tuple[bool, ...]`** — hit/rest bitmap derived from the binary representation of integer `n`. Same type as `euclidean_rhythm` output.
- **Both are duration-agnostic** — callers use `apply_rhythm` to bind the bitmap to actual pitches/durations. No slot duration parameter.

### Area 2: Multi-Voice Output Type

- **`rhythmic_canon(phrase, n, offset) -> Score`** — `n` voices each entering `offset` beats apart. Voice names: `'voice_0'`, `'voice_1'`, ..., `'voice_{n-1}'`. Consistent with Phase 8's `generate_multi_voice_counterpoint` return type.
- **`hocket(phrase, n) -> Score`** — `n` voices, notes distributed round-robin across voices. Voice names: `'voice_0'`, `'voice_1'`, ..., `'voice_{n-1}'`.
- **Index-based naming** (`'voice_0'`, `'voice_1'`, ...) — predictable, consistent with Phase 8 patterns, no added parameter complexity.

### Area 3: Rhythm/Pitch Separation

- **`apply_rhythm(pitches: tuple[int, ...], rhythm: tuple[bool, ...]) -> Phrase`**
  - `pitches` = pitch classes (ints, like MIDI numbers) mapped to `Note` objects
  - `rhythm` = hit/rest bitmap (output of `euclidean_rhythm` / `binary_rhythm`)
  - `True` entries → `Note` with a default quarter duration; `False` entries → `Rest`
  - **Length mismatch: cycle the shorter one** — if 3 pitches and 8 hits, pitches repeat cyclically until all hits are filled. Most musical; handles ostinato-style patterns naturally.
- **`isorhythm(talea: tuple[Duration, ...], color: tuple[int, ...], n: int) -> Phrase`**
  - `talea` = rhythm sequence (Duration objects)
  - `color` = pitch sequence (ints — MIDI numbers / pitch classes)
  - `n` = number of full LCM cycles to generate
  - Returns a single `Phrase` containing the complete isorhythmic pattern
  - LCM cycles: e.g., talea length 3 + color length 4 → LCM = 12 notes per cycle; multiply by `n`

### Claude's Discretion

- **Ostinato variation (PATT-02)** — exact variation strategy (random pitch substitution, dynamic shift, ornament addition) and `variation` parameter shape.
- **Default quarter duration in `apply_rhythm`** — whether to use `Duration.from_cn("q")` or accept an optional `duration` parameter for caller control.
- **Canon offset unit** — whether `offset` in `rhythmic_canon` is a `Duration`, `Fraction` (beat count), or int (note index); choose whatever is most natural given `Score` time alignment.
- **Accent pattern (PATT-07)** — exact articulation string used to mark accented notes (e.g., `'accent'` or `'>'`).
- **Module location** — `src/cadenza/patterns/` package (matches the scope).

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — RHYT-06, PATT-01 through PATT-07

### Prior phase patterns to follow
- `src/cadenza/transforms/rhythm.py` — pure functions on `Phrase`; `Duration` arithmetic uses `Fraction`; same pattern for all rhythm operations
- `src/cadenza/analysis/voiceleading.py` — `generate_inner_voices` as model for multi-voice generation returning `list[Phrase]`; Phase 8's `generate_multi_voice_counterpoint` as model for `Score`-returning generators
- `src/cadenza/core/note.py` — `Note(pitch, duration)` and `Rest(duration)` — immutable events; `Phrase = tuple[Event, ...]`
- `src/cadenza/counterpoint/__init__.py` — model for new subpackage `__init__` structure

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.core.phrase.Phrase` — `tuple[Event, ...]`; all pattern generators accept/return this type
- `cadenza.core.note.Note` / `Rest` — frozen dataclasses; `Note(pitch=..., duration=...)`, `Rest(duration=...)`
- `cadenza.core.duration.Duration.from_cn("q")` — builds a quarter note duration; use as default in `apply_rhythm`
- `cadenza.core.score.Score` — return type for `rhythmic_canon` and `hocket`; named voice pairs `(name, phrase)`
- `cadenza.transforms.rhythm` — `extract_rhythm`, `augment`, `rhythmic_rotation` — potentially composable in canon/ostinato generation

### Established Patterns
- Frozen dataclasses: `@dataclass(frozen=True, slots=True)` for any new result types
- `ValueError` for invalid inputs (n > m in euclidean_rhythm, empty phrases, etc.)
- Pure functions throughout — accept `Phrase`, return `Phrase` or `Score`
- Module-level constants for lookup tables (not needed here)
- Plain Python types: `tuple[bool, ...]` for bitmaps, `tuple[int, ...]` for pitch sequences

### Integration Points
- New module: `src/cadenza/patterns/` package
- `cadenza.__init__` re-exports need updating
- Tests: `tests/patterns/` directory

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 10-pattern-generation*
*Context gathered: 2026-03-20*
