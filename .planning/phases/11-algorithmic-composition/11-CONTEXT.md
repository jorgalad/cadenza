# Phase 11: Algorithmic Composition - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 delivers seven algorithmic generation capabilities operating on `Phrase` objects:

1. **Markov chain melody generation (ALGO-01, ALGO-02)** — train a first- or higher-order Markov model from a phrase; generate new melodies from the trained model.
2. **L-system melody generation (ALGO-03)** — apply Lindenmayer production rules for N generations; translate the resulting symbol string to a `Phrase` via a user-supplied alphabet.
3. **Probabilistic note selection (ALGO-04)** — generate a melody by selecting pitches from a weighted pitch set.
4. **Tendency mask application (ALGO-05)** — generate a melody where pitch probabilities vary over time via a time-position callable.
5. **Random walk (ALGO-06)** — generate a melody by walking from a starting pitch within scale + interval constraints.
6. **Variation generation (ALGO-07)** — produce N distinct but recognizably related variations of a phrase via systematic application of Phase 2 transforms.

New module: `src/cadenza/composition/` package. Depends on Phases 1, 2, 3.

</domain>

<decisions>
## Implementation Decisions

### Area 1: Markov Model API

- **Reusable `MarkovModel` frozen dataclass** — `train_markov(phrase, order=1) -> MarkovModel`. Returns an opaque model (frozen dataclass: `order`, `transition_table`). No methods — data only.
- **Separate generation function** — `markov_melody(model, length, seed=None) -> Phrase`. Train once, generate many times.
- **Single training phrase** — `train_markov(phrase: Phrase, order: int = 1)`. Callers can concatenate phrases if multi-phrase training is needed.
- **`order=1` covers ALGO-01 and ALGO-02** — no separate first-order vs higher-order functions. Order 1 = ALGO-01, order 2+ = ALGO-02.

### Area 2: Randomness & Reproducibility

- **`seed: int | None = None` on all stochastic functions** — applies to: `markov_melody`, `probabilistic_melody`, `tendency_mask_melody`, `random_walk`. `None` = system randomness (non-deterministic). Integer = reproducible output.
- **`probabilistic_melody(weights: dict[Pitch, float], length: int, seed=None) -> Phrase`** — `dict[Pitch, float]` as weighted pitch set. Weights are relative (normalized internally).
- **`tendency_mask_melody(mask: Callable[[float], dict[Pitch, float]], length: int, seed=None) -> Phrase`** — `mask` is a function of position in `[0.0, 1.0]` returning pitch weights at that point. Maximally flexible time-varying distribution.
- **`random_walk(start: Pitch, length: int, scale: Scale, max_step: int = 2, seed=None) -> Phrase`** — walk stays within `scale`, each step ≤ `max_step` semitones.

### Area 3: L-System Rule Representation

- **`dict[str, str]` for production rules** — classic Lindenmayer form: `{'A': 'AB', 'B': 'A'}`. Simple, readable, familiar from the L-system literature.
- **Separate `dict[str, Note | Rest]` alphabet** — rules define rewriting; alphabet defines musical meaning. e.g. `{'A': Note(Pitch('c4'), Duration.from_cn('q')), 'B': Note(Pitch('e4'), Duration.from_cn('e'))}`. Clean separation of concerns.
- **`lsystem_melody(axiom: str, rules: dict[str, str], alphabet: dict[str, Note | Rest], generations: int) -> Phrase`** — applies rules for N generations, translates to `Phrase` via alphabet. Symbols not in alphabet are silently skipped (e.g., bracket/stack symbols from turtle graphics L-systems).
- **`generations: int` (not max_notes)** — standard L-system parameter. Phrase length grows exponentially; caller controls via generations count.

### Area 4: Variation Generation

- **`generate_variations(phrase: Phrase, n: int) -> list[Phrase]`** — returns `n` variations in a deterministic priority order.
- **One transform per variation** — each variation = one Phase 2 transform applied once. Simple, recognizable relationship to original.
- **Priority order (deterministic, no seed needed)**:
  1. `chromatic_transpose(phrase, +1)` through `chromatic_transpose(phrase, +N)` — transpositions first
  2. `invert(phrase)` — melodic inversion
  3. `pitch_retrograde(phrase)` — pitch retrograde
  4. `augment(phrase, 2)` — rhythmic augmentation (×2)
  5. `diminish(phrase, 2)` — rhythmic diminution (÷2)
  6. `rotate(phrase, 1)` through `rotate(phrase, +N)` — rotations
  - Continues cycling through available transforms if `n` exceeds the base set.
- **Uses existing Phase 2 transforms** — `chromatic_transpose`, `invert`, `pitch_retrograde`, `augment`, `diminish`, `rotate` from `cadenza.transforms`.

### Claude's Discretion

- **`MarkovModel` internal structure** — exact shape of `transition_table` (e.g., `dict[tuple[int,...], dict[int, float]]` keyed by pitch-class n-gram); choose whatever makes Markov generation cleanest.
- **Rhythm in Markov generation** — whether `markov_melody` also models rhythmic transitions or uses a fixed/carried-forward duration from the training phrase.
- **Module location** — `src/cadenza/composition/` package (matches the scope and follows established subpackage pattern).
- **Duration for probabilistic/tendency/random_walk outputs** — default duration to use for each generated note (suggest: quarter note, or carry from a provided `Duration` parameter).

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — ALGO-01 through ALGO-07

### Prior phase patterns to follow
- `src/cadenza/transforms/pitch.py` — `chromatic_transpose`, `invert`, `from_midi` — direct dependencies for variation generation and random walk
- `src/cadenza/transforms/melodic.py` — `pitch_retrograde`, `rotate`, `augment`, `diminish` — direct dependencies for variation generation
- `src/cadenza/patterns/rhythm.py` — `euclidean_rhythm` / `binary_rhythm` — established pure-function, seed-free pattern (Phase 10); Phase 11 adds seed support
- `src/cadenza/settheory/serial.py` — `ToneRow` frozen dataclass — reference for the `MarkovModel` frozen dataclass pattern (Phase 9)
- `src/cadenza/counterpoint/__init__.py` — model for new `composition/` subpackage `__init__` structure
- `src/cadenza/theory/scales.py` — `Scale` type used in `random_walk` constraint

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.transforms.pitch.chromatic_transpose` / `invert` / `from_midi` — core building blocks for variation generation and pitch walking
- `cadenza.transforms.melodic.pitch_retrograde` / `rotate` / `augment` / `diminish` / `permute` — full variation transform set already implemented and tested
- `cadenza.transforms.pitch.nearest_in_scale` — constrains random walk to scale tones
- `cadenza.theory.scales.Scale` — scale type for `random_walk` constraint parameter
- `cadenza.core.note.Note` / `Rest` — used directly in L-system alphabet
- `cadenza.core.pitch.Pitch` — used in `probabilistic_melody` weights dict and `random_walk` start pitch

### Established Patterns
- Frozen dataclasses: `@dataclass(frozen=True, slots=True)` for `MarkovModel`
- `ValueError` for invalid inputs (negative order, empty alphabet, n=0 variations, etc.)
- Pure functions throughout — no global state; all stochastic state via `seed` parameter
- Module-level constants acceptable for transform priority lists (variation ordering)
- Plain Python types: `dict[Pitch, float]` for weights, `dict[str, str]` for L-system rules

### Integration Points
- New module: `src/cadenza/composition/` package
- `cadenza.__init__` re-exports need updating
- Tests: `tests/composition/` directory

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

*Phase: 11-algorithmic-composition*
*Context gathered: 2026-03-22*
