# Phase 6: Batch Operations & Analysis - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 delivers two capabilities on top of the existing `Phrase`/`Note`/`Rest` model:

1. **Batch mutations** — operations that produce a new Phrase by modifying every note matching a condition (BATCH-01…09): articulation, dynamic, crescendo/decrescendo, pitch replacement, filtering, quantize, humanize, windowed transforms.

2. **Analysis/inspection** — read-only functions that return structured data about a phrase (ANAL-01…09): ambitus, contour, interval sequence, pitch class histogram, rhythmic density, complexity score, motif detection, phrase similarity, sequence detection.

Both capabilities follow the same immutable pattern: inputs are `Phrase` objects, outputs are new `Phrase` objects (mutations) or plain data types (analysis). Nothing in Phase 2 (transforms) is replaced — these are complementary.

</domain>

<decisions>
## Implementation Decisions

### Area 1: Crescendo / Decrescendo (BATCH-03)

- **Algorithm:** Proportional mapping — distribute dynamics linearly across note count, rounding to the nearest available dynamic level. E.g. crescendo from `pp` to `ff` (5 steps) across 6 notes: `pp, pp, p, mf, f, ff`.
- **Rests:** Skip. Only `Note` events consume positions in the dynamic progression. Rests pass through unchanged.
- **Validation:** `crescendo(phrase, start, end)` requires `start < end` (raises `ValueError` otherwise). A separate `decrescendo(phrase, start, end)` requires `start > end` (raises `ValueError`). No auto-direction detection.

### Area 2: Humanize (BATCH-06)

- **Scope:** Dynamics only — shift each `Note`'s dynamic by ±1 step randomly. Notes without a dynamic (`dynamic=None`) are left unchanged. Rests pass through unchanged.
- **Boundary behavior:** Clamp at extremes. A `ppp` note can only go to `ppp` or `pp` (never wrap). A `fff` note can only go to `fff` or `ff`.
- **Reproducibility:** `humanize(phrase, seed=None)` — optional `seed` parameter. With seed: fully deterministic. Without seed: uses `random` module default state.

### Area 3: Analysis Return Types

- **`melodic_contour(phrase) -> list[str]`** — returns `['U', 'D', 'S']` symbols (Up/Down/Same). Length = number of consecutive Note pairs (skipping Rests). Plain strings, no enum import required.
- **`find_motifs(phrase, min_length=2) -> list[MotifMatch]`** — returns `MotifMatch(motif: Phrase, positions: list[int])` frozen dataclass instances. Groups all occurrences of each distinct motif. Consistent with `ChordMatch`/`KeyResult` pattern from Phase 5.
- **`phrase_similarity(phrase1, phrase2) -> float`** — scalar `0.0`–`1.0`. `1.0` = identical, `0.0` = completely different. Combines pitch, rhythm, and contour sub-scores internally; only the combined score is returned.
- **`interval_sequence(phrase) -> list[Interval]`** — skips Rests; returns intervals only between consecutive `Note` events. Length varies with rest count.

### Area 4: Windowed Transform (BATCH-09)

- **Signature:** `apply_windowed(phrase, fn, window_size: int, step: int | None = None) -> Phrase`
  - `step` defaults to `window_size` (non-overlapping). Set `step < window_size` for overlapping windows.
- **Tail behavior:** Include partial window — last window may be smaller than `window_size` if the phrase length isn't divisible. No events are dropped.
- **Return type:** Single concatenated `Phrase` — all transformed windows joined in order. Consistent with how transforms work throughout the library.

### Claude's Discretion

- Exact complexity scoring algorithm for `ANAL-06` (melodic complexity score) — combine interval variety, rhythm variety, and contour change count in whatever proportion produces musically sensible results.
- Internal representation of `MotifMatch.positions` — 0-based note index vs. onset time as `Fraction`. Choose whatever is most useful for the motif detection algorithm.
- `detect_sequence(phrase1, phrase2)` (ANAL-09) detection algorithm — exact imitation, transposed imitation, or both; Claude decides what's practical.
- `rhythmic_density(phrase)` (ANAL-05) time window granularity.

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements are fully captured in decisions above and in REQUIREMENTS.md.

### Phase requirements
- `.planning/REQUIREMENTS.md` — BATCH-01 through BATCH-09, ANAL-01 through ANAL-09 (full spec for each operation)

### Prior phase patterns to follow
- `src/cadenza/analysis/chords.py` — frozen dataclass result pattern (`ChordMatch`) used for `MotifMatch`
- `src/cadenza/analysis/keys.py` — `detect_key` / `KeyResult` dataclass pattern
- `src/cadenza/transforms/melodic.py` — `omit`, `pitch_map` patterns for predicate-based batch operations
- `src/cadenza/core/pitch.py` — `Pitch` type for ambitus return values

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.transforms.melodic.omit(phrase, n=None, predicate=None)` — existing predicate-based note removal; batch filter (BATCH-08) is a generalization of this pattern
- `cadenza.transforms.melodic.pitch_map(phrase, fn)` — applies a function to every pitch; batch pitch replacement (BATCH-07) wraps this
- `cadenza.transforms.rhythm._map_durations` (private) — internal pattern for mapping over durations; quantize (BATCH-05) follows this
- `cadenza.analysis.chords.ChordMatch` — frozen dataclass example for `MotifMatch`
- `cadenza.core.note.Note` fields: `pitch`, `duration`, `dynamic`, `articulation` — batch operations target these fields

### Established Patterns
- All operations return new objects — never mutate (`@dataclass(frozen=True, slots=True)` throughout)
- `ValueError` for invalid inputs (not `None` returns, not silent no-ops)
- Private helpers `_map_*` for the iteration logic; public functions compose them
- Dynamic string constants: `"ppp"`, `"pp"`, `"p"`, `"mp"`, `"mf"`, `"f"`, `"ff"`, `"fff"` (ordered list needed for crescendo)

### Integration Points
- New module: `src/cadenza/batch/` for mutation operations (BATCH-01…09)
- New module: `src/cadenza/analysis/` already exists — add `metrics.py` for ANAL functions, or add to a new `src/cadenza/analysis/phrases.py`
- `cadenza.__init__` re-exports — both `cadenza.batch` and expanded `cadenza.analysis` need top-level export entries
- Tests: `tests/batch/` and `tests/analysis/` (extends existing analysis test dir)

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

*Phase: 06-batch-operations-analysis*
*Context gathered: 2026-03-19*
