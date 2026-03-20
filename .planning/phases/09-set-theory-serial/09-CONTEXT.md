# Phase 9: Set Theory & Serial - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 delivers two capabilities operating on pitch class sets and 12-tone rows:

1. **Pitch class set operations (SETTH-01..09)** — prime form, interval vector, Forte number lookup, complement, inversion, transposition, subset/superset/Z-relation testing, similarity measures (Rp, R0, R1, R2).

2. **12-tone serial operations (SERI-01..06)** — define a row, generate the 48-form matrix, detect row properties (all-interval, combinatoriality), realize a row as pitched notes, segment into trichords/tetrachords/hexachords, derive a row from a smaller set.

New module: `src/cadenza/settheory/` or `src/cadenza/analysis/settheory.py`. Depends only on Phase 1 (`Pitch`, `Phrase`).

</domain>

<decisions>
## Implementation Decisions

### Area 1: PitchClassSet Input/Output Types

- **No named wrapper type** — pitch class sets are plain `frozenset[int]` throughout. All functions accept and return `frozenset[int]` (or `tuple[int, ...]` where order is meaningful). No `PitchClassSet` class needed.
- **Construction pattern:** Callers build sets from `Pitch.pitch_class`:
  ```python
  pc_set = frozenset(p.pitch_class for p in phrase if isinstance(p, Note))
  ```
- **`prime_form(pcs: frozenset[int]) -> tuple[int, ...]`** — returns an ordered tuple starting from 0 (e.g., `(0, 1, 3, 7)`). Order is meaningful in prime form.
- **`interval_vector(pcs: frozenset[int]) -> tuple[int, int, int, int, int, int]`** — 6-element tuple of interval class counts.
- **`forte_number(pcs: frozenset[int]) -> str`** — returns string like `'4-Z15'`.
- **`lookup_by_forte(forte: str) -> tuple[int, ...]`** — returns prime form tuple; raises `ValueError` if not found.
- **`complement(pcs: frozenset[int]) -> frozenset[int]`** — set of all 12 pitch classes not in the input.
- **`invert_pcs(pcs: frozenset[int]) -> frozenset[int]`** — inversion (mod 12).
- **`transpose_pcs(pcs: frozenset[int], n: int) -> frozenset[int]`** — transposition by `n` semitones (mod 12).
- **Relationship predicates — individual boolean functions:**
  ```python
  is_subset(a: frozenset[int], b: frozenset[int]) -> bool
  is_superset(a: frozenset[int], b: frozenset[int]) -> bool
  is_z_related(a: frozenset[int], b: frozenset[int]) -> bool
  ```
- **Similarity predicates — individual boolean functions (Rahn's Rp, R0, R1, R2):**
  ```python
  rp_relation(a: frozenset[int], b: frozenset[int]) -> bool  # shares a subset
  r0(a: frozenset[int], b: frozenset[int]) -> bool            # same interval vector
  r1(a: frozenset[int], b: frozenset[int]) -> bool            # one ic differs by ±1
  r2(a: frozenset[int], b: frozenset[int]) -> bool            # two ics differ by ±1
  ```

### Area 2: Prime Form Algorithm

- **Canonical algorithm: Forte (1973)** — required for correctness of the Forte number table. The ~6 set classes that differ between Forte and Rahn resolve to Forte's results.
- **Forte number table: hardcoded** — embed all 208 set classes as a module-level dict constant:
  ```python
  FORTE_TABLE: dict[str, tuple[int, ...]] = {
      '2-1': (0, 1),
      '2-2': (0, 2),
      # ... 208 entries ...
      '4-Z15': (0, 1, 4, 6),
      '12-1': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
  }
  ```
  O(1) lookup, guaranteed correctness, no startup computation cost.
- **Reverse index** — also build `PRIME_TO_FORTE: dict[tuple[int,...], str]` at module load for `forte_number()` lookup.

### Claude's Discretion

- **ToneRow type** — whether a 12-tone row is a named `ToneRow` dataclass wrapping `tuple[int, ...]` or a plain `tuple[int, ...]`. Planner decides based on what makes the SERI API cleanest.
- **ToneRow API shape** — whether matrix access is `row.prime(n)` / `row.inversion(n)` methods or standalone functions `prime_form_row(row, n)` / `inversion_row(row, n)`. Choose whichever is most consistent with the existing codebase patterns (frozen dataclass with methods is acceptable).
- **Row realization output (SERI-04)** — whether `realize_row(row_form, octave)` returns `Phrase` or `tuple[Pitch, ...]`. Octave placement strategy (all in one octave, voice-leading minimization, or configurable).
- **Row segmentation (SERI-05)** — return type for `segment_row(row, sizes)`.
- **Row derivation (SERI-06)** — exact algorithm for `derive_row(seed_set)`.
- **Module location** — `src/cadenza/settheory/` package or single `src/cadenza/analysis/settheory.py` file.

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — SETTH-01 through SETTH-09, SERI-01 through SERI-06

### Prior phase patterns to follow
- `src/cadenza/core/pitch.py` — `Pitch.pitch_class` property (returns `int`, `midi_number % 12`)
- `src/cadenza/analysis/voiceleading.py` — frozen dataclass + pure functions pattern; individual predicate functions (`_check_parallels` etc.)
- `src/cadenza/analysis/phrases.py` — analysis functions returning plain Python types (`list[str]`, `float`, etc.)
- `src/cadenza/counterpoint/validation.py` — `CounterpointViolation` dataclass pattern for any result types

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Pitch.pitch_class` (`cadenza.core.pitch`) — already computes `midi_number % 12`; primary bridge between musical `Pitch` objects and integer pitch class sets
- `Pitch.midi_number` — needed for row realization (converting pitch class + octave to concrete Pitch)
- `cadenza.transforms.pitch.from_midi(n)` — builds a `Pitch` from MIDI number; useful in SERI-04 row realization

### Established Patterns
- Frozen dataclasses: `@dataclass(frozen=True, slots=True)` for all result types
- `ValueError` for invalid inputs (invalid Forte number, row with duplicates, etc.)
- Module-level constants for lookup tables (established in `cadenza.counterpoint.rules`)
- Plain Python types for analysis results (`frozenset[int]`, `tuple[int, ...]`) — avoids new classes where not needed

### Integration Points
- New module: `src/cadenza/settheory/` or `src/cadenza/analysis/settheory.py`
- `cadenza.__init__` re-exports need updating
- Tests: `tests/settheory/` or `tests/analysis/test_settheory.py`

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

*Phase: 09-set-theory-serial*
*Context gathered: 2026-03-20*
