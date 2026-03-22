# Phase 11: Algorithmic Composition - Research

**Researched:** 2026-03-22
**Domain:** Algorithmic melody generation (Markov chains, L-systems, stochastic selection, variation)
**Confidence:** HIGH

## Summary

Phase 11 implements seven algorithmic composition capabilities as pure functions operating on the existing `Phrase` type. The domain is well-understood (Markov chains, Lindenmayer systems, weighted random selection, random walks, tendency masks) and all algorithms have straightforward implementations using Python's standard library -- specifically `random.Random` for seeded reproducibility and `dataclasses` for the frozen `MarkovModel`.

The phase is unusual in that it has zero external dependencies. Every algorithm is implementable with Python stdlib (`random`, `collections`, `dataclasses`). The primary complexity lies in correctly interfacing with the existing type system -- particularly constructing `Note` objects with proper `Pitch`, `Duration`, and `Interval` types, and correctly calling Phase 2 transforms (which take `Interval` objects, not raw integers) for variation generation.

**Primary recommendation:** Use `random.Random(seed)` instances (not `random.seed()` global state) for all stochastic functions. Build a small internal helper to construct ascending chromatic intervals from semitone counts, since `chromatic_transpose` requires `Interval` objects.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Reusable `MarkovModel` frozen dataclass** -- `train_markov(phrase, order=1) -> MarkovModel`. Returns an opaque model (frozen dataclass: `order`, `transition_table`). No methods -- data only.
- **Separate generation function** -- `markov_melody(model, length, seed=None) -> Phrase`. Train once, generate many times.
- **Single training phrase** -- `train_markov(phrase: Phrase, order: int = 1)`. Callers can concatenate phrases if multi-phrase training is needed.
- **`order=1` covers ALGO-01 and ALGO-02** -- no separate first-order vs higher-order functions. Order 1 = ALGO-01, order 2+ = ALGO-02.
- **`seed: int | None = None` on all stochastic functions** -- `None` = system randomness. Integer = reproducible output.
- **`probabilistic_melody(weights: dict[Pitch, float], length: int, seed=None) -> Phrase`** -- dict[Pitch, float] as weighted pitch set.
- **`tendency_mask_melody(mask: Callable[[float], dict[Pitch, float]], length: int, seed=None) -> Phrase`** -- mask is a function of position in [0.0, 1.0] returning pitch weights.
- **`random_walk(start: Pitch, length: int, scale: Scale, max_step: int = 2, seed=None) -> Phrase`** -- walk stays within scale, each step <= max_step semitones.
- **`dict[str, str]` for L-system production rules** -- classic Lindenmayer form.
- **Separate `dict[str, Note | Rest]` alphabet** for musical meaning.
- **`lsystem_melody(axiom: str, rules: dict[str, str], alphabet: dict[str, Note | Rest], generations: int) -> Phrase`** -- symbols not in alphabet silently skipped.
- **`generate_variations(phrase: Phrase, n: int) -> list[Phrase]`** -- deterministic priority order, one transform per variation.
- **Priority order**: chromatic_transpose(+1..+N), invert, pitch_retrograde, augment(2), diminish(2), rotate(1..+N), cycling if n exceeds base set.
- **Uses existing Phase 2 transforms** -- chromatic_transpose, invert, pitch_retrograde, augment, diminish, rotate.

### Claude's Discretion

- **`MarkovModel` internal structure** -- exact shape of `transition_table` (e.g., `dict[tuple[int,...], dict[int, float]]` keyed by pitch-class n-gram).
- **Rhythm in Markov generation** -- whether markov_melody also models rhythmic transitions or uses fixed/carried-forward duration.
- **Module location** -- `src/cadenza/composition/` package.
- **Duration for probabilistic/tendency/random_walk outputs** -- default duration for each generated note.

### Deferred Ideas (OUT OF SCOPE)

None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ALGO-01 | First-order Markov chain melody generation from a trained phrase | `train_markov(phrase, order=1)` + `markov_melody(model, length, seed)` -- order=1 case |
| ALGO-02 | Higher-order Markov chain generation (configurable order) | Same functions with order=2+ -- unified API per locked decision |
| ALGO-03 | L-system melody/rhythm generation with configurable rules | `lsystem_melody(axiom, rules, alphabet, generations)` -- deterministic string rewriting + alphabet mapping |
| ALGO-04 | Probabilistic note selection from a weighted pitch set | `probabilistic_melody(weights, length, seed)` -- `random.choices` with normalized weights |
| ALGO-05 | Tendency mask application (pitch probability varies over time) | `tendency_mask_melody(mask, length, seed)` -- mask callable evaluated at each position in [0,1] |
| ALGO-06 | Random walk melody generation within scale/interval constraints | `random_walk(start, length, scale, max_step, seed)` -- uses `nearest_in_scale` for constraint |
| ALGO-07 | Generate variations on a theme (systematic application of transforms) | `generate_variations(phrase, n)` -- deterministic priority order using Phase 2 transforms |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `random` | 3.11+ | Seeded RNG via `random.Random(seed)` | Instance-based RNG avoids global state; `choices()` handles weighted selection natively |
| Python stdlib `dataclasses` | 3.11+ | `MarkovModel` frozen dataclass | Matches project pattern (`ToneRow`, all core types) |
| Python stdlib `collections` | 3.11+ | `defaultdict` for transition table building | Clean accumulation pattern for Markov training |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `cadenza.transforms.pitch` | internal | `chromatic_transpose`, `invert`, `from_midi`, `nearest_in_scale` | Variation generation, random walk |
| `cadenza.transforms.melodic` | internal | `pitch_retrograde`, `rotate`, `augment`, `diminish` | Variation generation |
| `cadenza.transforms.rhythm` | internal | `augment`, `diminish` | Variation generation (rhythmic transforms) |
| `cadenza.theory.scales` | internal | `Scale` type | Random walk constraint parameter |
| `cadenza.core.*` | internal | `Pitch`, `Duration`, `Note`, `Rest`, `Phrase`, `Interval` | All generation functions |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `random.Random` instance | `numpy.random` | numpy adds a dependency; stdlib Random is sufficient for note-level generation |
| Manual Markov impl | External Markov library | No library needed -- transition tables are trivial with dicts |

**Installation:**
```bash
# No new dependencies -- all stdlib + existing cadenza internals
```

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/composition/
    __init__.py          # Re-exports all public functions + MarkovModel
    markov.py            # train_markov, markov_melody, MarkovModel (ALGO-01, ALGO-02)
    lsystem.py           # lsystem_melody (ALGO-03)
    stochastic.py        # probabilistic_melody, tendency_mask_melody, random_walk (ALGO-04, ALGO-05, ALGO-06)
    variation.py         # generate_variations (ALGO-07)
tests/composition/
    __init__.py
    conftest.py          # Shared fixtures (sample phrases, scales)
    test_markov.py
    test_lsystem.py
    test_stochastic.py
    test_variation.py
```

### Pattern 1: Instance-based RNG for Reproducibility
**What:** Create a `random.Random(seed)` instance per function call instead of using `random.seed()`.
**When to use:** Every stochastic function (markov_melody, probabilistic_melody, tendency_mask_melody, random_walk).
**Example:**
```python
import random as _random

def probabilistic_melody(
    weights: dict[Pitch, float],
    length: int,
    seed: int | None = None,
) -> Phrase:
    rng = _random.Random(seed)  # None = system entropy
    pitches = list(weights.keys())
    w = list(weights.values())
    events: list[Event] = []
    for _ in range(length):
        chosen = rng.choices(pitches, weights=w, k=1)[0]
        events.append(Note(pitch=chosen, duration=_DEFAULT_DURATION))
    return tuple(events)
```

### Pattern 2: Frozen Dataclass for MarkovModel
**What:** Opaque data container following ToneRow pattern.
**When to use:** Markov model storage.
**Example:**
```python
@dataclass(frozen=True, slots=True)
class MarkovModel:
    order: int
    transition_table: tuple  # Frozen dict representation -- see Discretion section
```

**Important:** Since `dict` is mutable, the transition table must be stored as a hashable type. Options: (a) store as `tuple[tuple[tuple[int,...], tuple[tuple[int,float],...]],...]]` (ugly but hashable), or (b) use a regular dict but accept that the dataclass won't be truly hashable (follow ToneRow pattern which stores `tuple[int,...]`). Recommendation: store as a plain `dict` inside the frozen dataclass -- `frozen=True` only prevents reassignment, not deep mutation. This matches the pragmatic approach of the codebase. The `__hash__` will need to be overridden or omitted if dict is used.

### Pattern 3: Interval Construction for Variation Transforms
**What:** The `chromatic_transpose` function requires an `Interval` object, not a raw integer. The variation generator needs a helper to build ascending chromatic intervals.
**When to use:** `generate_variations` building its transform list.
**Example:**
```python
from cadenza.core.interval import Interval

def _chromatic_interval(semitones: int) -> Interval:
    """Build an ascending chromatic interval from semitone count.

    Maps semitone count to the simplest interval spelling:
    1 -> m2 up, 2 -> M2 up, 3 -> m3 up, etc.
    """
    _SEMITONE_TO_INTERVAL = {
        1: ("m", 2), 2: ("M", 2), 3: ("m", 3), 4: ("M", 3),
        5: ("P", 4), 6: ("A", 4), 7: ("P", 5), 8: ("m", 6),
        9: ("M", 6), 10: ("m", 7), 11: ("M", 7), 12: ("P", 8),
    }
    quality, number = _SEMITONE_TO_INTERVAL[semitones % 12 or 12]
    octaves = (semitones - 1) // 12
    return Interval(quality=quality, number=number + 7 * octaves, direction=1)
```

### Anti-Patterns to Avoid
- **Global `random.seed()` calls:** Mutates global state, breaks parallelism. Use `random.Random(seed)` instances.
- **Storing mutable state in frozen dataclass then relying on `__hash__`:** Frozen dataclass with dict field won't be hashable by default. Either don't hash MarkovModel or use immutable internals.
- **Exponential L-system output without guard:** L-systems grow exponentially. While the user controls via `generations`, document that large generation counts produce massive strings.
- **Normalizing weights to sum=1 manually:** `random.choices()` normalizes weights internally -- no need to pre-normalize.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Weighted random selection | Custom cumulative distribution | `random.Random.choices(population, weights=w)` | Handles normalization, edge cases |
| Pitch transposition | Manual MIDI arithmetic | `chromatic_transpose(phrase, interval)` | Correct spelling preservation |
| Scale membership check | Manual pitch-class comparison | `nearest_in_scale(pitch, scale)` | Handles octave wrapping, multiple candidates |
| Melodic transforms for variations | Re-implementing invert/retrograde | Phase 2 functions directly | Already tested, correct |

**Key insight:** Phase 11 is a thin algorithmic layer on top of well-tested Phase 1-3 primitives. The algorithms themselves are simple; the value comes from correct integration with existing types.

## Common Pitfalls

### Pitfall 1: Markov Dead Ends
**What goes wrong:** A trained Markov model reaches a state with no observed successor (especially with higher-order models on short training phrases).
**Why it happens:** The training phrase may not contain all possible n-gram continuations.
**How to avoid:** When generation reaches a dead end, either (a) fall back to a lower-order model, (b) restart from a random state, or (c) raise an error. Recommendation: restart from a random observed state with a warning.
**Warning signs:** Generated melody is shorter than requested `length`.

### Pitfall 2: Empty Transition Table
**What goes wrong:** `train_markov` on a very short phrase (fewer events than order+1) produces an empty or useless model.
**Why it happens:** Not enough data to build any transitions.
**How to avoid:** Validate that the phrase has at least `order + 1` notes. Raise `ValueError` for insufficient data.
**Warning signs:** `len([n for n in phrase if isinstance(n, Note)]) <= order`.

### Pitfall 3: L-System Exponential Growth
**What goes wrong:** User specifies `generations=10` with branching rules, producing millions of symbols.
**Why it happens:** L-system output grows exponentially with generation count.
**How to avoid:** This is expected behavior. Document it. Do NOT add artificial limits -- the caller controls via `generations`. Optionally log/warn for very long strings.
**Warning signs:** Output phrase has thousands of notes.

### Pitfall 4: Random Walk Stuck in Corner
**What goes wrong:** Random walk at the top/bottom of a scale with `max_step=1` has very few valid moves, producing repetitive melodies.
**Why it happens:** Constrained by scale boundary and small step size.
**How to avoid:** Allow steps in both directions (up and down). If no valid step exists within constraints, stay on current pitch (or raise). Always generate candidate steps in both directions.
**Warning signs:** Many consecutive repeated pitches in output.

### Pitfall 5: Variation Priority Overflow
**What goes wrong:** `generate_variations(phrase, n=100)` for a phrase needs to cycle through transforms multiple times.
**Why it happens:** The base transform set is finite (transpositions 1-11, invert, retrograde, augment, diminish, rotations 1-N).
**How to avoid:** Define the full priority list including all chromatic transpositions (1-11) and all rotations (1 to len(phrase)-1), then cycle. With an 8-note phrase: 11 transpositions + 1 invert + 1 retrograde + 1 augment + 1 diminish + 7 rotations = 22 unique transforms. For n > 22, cycle from the start.
**Warning signs:** Index out of range in priority list.

### Pitfall 6: Duration for Generated Notes
**What goes wrong:** Generated notes need a Duration but the stochastic functions don't inherently produce rhythm.
**Why it happens:** `probabilistic_melody`, `tendency_mask_melody`, and `random_walk` generate pitch sequences, not rhythmic ones.
**How to avoid:** Use a default quarter-note duration. Consider adding an optional `duration: Duration = Duration.from_cn("q")` parameter.
**Warning signs:** Notes created without duration fail at construction time.

## Code Examples

### Markov Training (building transition table)
```python
from collections import defaultdict
from cadenza.core.note import Note

def train_markov(phrase: Phrase, order: int = 1) -> MarkovModel:
    if order < 1:
        raise ValueError(f"order must be >= 1, got {order}")
    notes = [e for e in phrase if isinstance(e, Note)]
    if len(notes) <= order:
        raise ValueError(
            f"Phrase has {len(notes)} notes but order={order} requires at least {order + 1}"
        )
    # Use MIDI numbers as state representation
    midis = [n.pitch.midi_number for n in notes]
    table: dict[tuple[int, ...], dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for i in range(len(midis) - order):
        state = tuple(midis[i : i + order])
        successor = midis[i + order]
        table[state][successor] += 1
    # Convert counts to probabilities
    prob_table: dict[tuple[int, ...], dict[int, float]] = {}
    for state, successors in table.items():
        total = sum(successors.values())
        prob_table[state] = {s: c / total for s, c in successors.items()}
    return MarkovModel(order=order, transition_table=prob_table)
```

### Markov Generation
```python
import random as _random

def markov_melody(
    model: MarkovModel,
    length: int,
    seed: int | None = None,
) -> Phrase:
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    rng = _random.Random(seed)
    table = model.transition_table
    states = list(table.keys())
    # Start from a random observed state
    state = rng.choice(states)
    result_midis = list(state)
    while len(result_midis) < length:
        if state not in table:
            state = rng.choice(states)  # Dead-end recovery
        successors = table[state]
        pitches = list(successors.keys())
        weights = list(successors.values())
        next_midi = rng.choices(pitches, weights=weights, k=1)[0]
        result_midis.append(next_midi)
        state = tuple(result_midis[-model.order:])
    # Convert MIDI numbers to Notes
    duration = Duration.from_cn("q")
    events = [Note(pitch=from_midi(m), duration=duration) for m in result_midis[:length]]
    return tuple(events)
```

### L-System Expansion
```python
def lsystem_melody(
    axiom: str,
    rules: dict[str, str],
    alphabet: dict[str, Note | Rest],
    generations: int,
) -> Phrase:
    if generations < 0:
        raise ValueError(f"generations must be non-negative, got {generations}")
    # Expand
    current = axiom
    for _ in range(generations):
        current = "".join(rules.get(ch, ch) for ch in current)
    # Translate to Phrase via alphabet (skip unknown symbols)
    events = [alphabet[ch] for ch in current if ch in alphabet]
    return tuple(events)
```

### Random Walk
```python
def random_walk(
    start: Pitch,
    length: int,
    scale: Scale,
    max_step: int = 2,
    seed: int | None = None,
) -> Phrase:
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    if max_step < 1:
        raise ValueError(f"max_step must be >= 1, got {max_step}")
    rng = _random.Random(seed)
    duration = Duration.from_cn("q")
    current = nearest_in_scale(start, scale)
    events: list[Event] = [Note(pitch=current, duration=duration)]
    for _ in range(length - 1):
        # Generate candidate steps: -max_step to +max_step semitones
        candidates = []
        for step in range(-max_step, max_step + 1):
            if step == 0:
                continue
            candidate_midi = current.midi_number + step
            candidate = nearest_in_scale(from_midi(candidate_midi), scale)
            candidates.append(candidate)
        if not candidates:
            candidates = [current]  # Stay put if no valid move
        current = rng.choice(candidates)
        events.append(Note(pitch=current, duration=duration))
    return tuple(events)
```

### Variation Generation
```python
def generate_variations(phrase: Phrase, n: int) -> list[Phrase]:
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if not phrase:
        raise ValueError("Cannot generate variations of empty phrase")
    # Build priority-ordered transform list
    transforms: list[Callable[[Phrase], Phrase]] = []
    # 1. Chromatic transpositions +1 through +11
    for semitones in range(1, 12):
        interval = _chromatic_interval(semitones)
        transforms.append(lambda p, iv=interval: chromatic_transpose(p, iv))
    # 2. Invert
    transforms.append(lambda p: invert(p))
    # 3. Pitch retrograde
    transforms.append(lambda p: pitch_retrograde(p))
    # 4. Augment x2
    transforms.append(lambda p: augment(p, 2))
    # 5. Diminish /2
    transforms.append(lambda p: diminish(p, 2))
    # 6. Rotations 1 through len(phrase)-1
    for r in range(1, len(phrase)):
        transforms.append(lambda p, n=r: rotate(p, n))
    # Generate n variations, cycling if needed
    return [transforms[i % len(transforms)](phrase) for i in range(n)]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `random.seed(n)` global state | `random.Random(n)` instance | Python 3.x best practice | Thread-safe, composable, no global side effects |
| Class-based generators | Pure functions + data | Cadenza convention | Matches project style (all transforms are functions) |

**Deprecated/outdated:**
- None relevant -- Markov chains and L-systems are stable algorithms unchanged for decades.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `pytest tests/composition/ -x -q` |
| Full suite command | `pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ALGO-01 | First-order Markov melody follows training phrase patterns | unit | `pytest tests/composition/test_markov.py::test_first_order_markov -x` | Wave 0 |
| ALGO-02 | Higher-order Markov with order=2+ produces different results than order=1 | unit | `pytest tests/composition/test_markov.py::test_higher_order_markov -x` | Wave 0 |
| ALGO-03 | L-system expands rules for N generations, translates via alphabet | unit | `pytest tests/composition/test_lsystem.py::test_lsystem_expansion -x` | Wave 0 |
| ALGO-04 | Probabilistic melody selects from weighted pitch set | unit | `pytest tests/composition/test_stochastic.py::test_probabilistic_melody -x` | Wave 0 |
| ALGO-05 | Tendency mask varies pitch distribution over time | unit | `pytest tests/composition/test_stochastic.py::test_tendency_mask -x` | Wave 0 |
| ALGO-06 | Random walk stays within scale and step constraints | unit | `pytest tests/composition/test_stochastic.py::test_random_walk -x` | Wave 0 |
| ALGO-07 | Variations are distinct but use expected transforms in priority order | unit | `pytest tests/composition/test_variation.py::test_generate_variations -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/composition/ -x -q`
- **Per wave merge:** `pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/composition/__init__.py` -- package init
- [ ] `tests/composition/conftest.py` -- shared fixtures (sample phrases, scales, durations)
- [ ] `tests/composition/test_markov.py` -- covers ALGO-01, ALGO-02
- [ ] `tests/composition/test_lsystem.py` -- covers ALGO-03
- [ ] `tests/composition/test_stochastic.py` -- covers ALGO-04, ALGO-05, ALGO-06
- [ ] `tests/composition/test_variation.py` -- covers ALGO-07
- [ ] `src/cadenza/composition/__init__.py` -- package init with re-exports

## Open Questions

1. **MarkovModel hashability with dict field**
   - What we know: Frozen dataclass with a `dict` field is not hashable by default. ToneRow uses `tuple[int, ...]` which is hashable.
   - What's unclear: Whether MarkovModel needs to be hashable (used in sets/dicts).
   - Recommendation: Store transition_table as a plain `dict` inside the frozen dataclass. Skip `__hash__` -- MarkovModel is a data transfer object, not a dict key. If hashability is later needed, convert to nested tuples.

2. **Rhythm modeling in Markov chains**
   - What we know: CONTEXT.md leaves this to Claude's discretion. The simplest approach models only pitch transitions.
   - What's unclear: Whether modeling rhythm transitions adds enough musical value for the complexity.
   - Recommendation: Model pitch only (MIDI numbers as states). Use a fixed quarter-note duration for generated notes. This keeps the implementation clean and focused. Users who want rhythm variation can post-process with `apply_rhythm` from Phase 10.

3. **Default duration for stochastic generators**
   - What we know: `probabilistic_melody`, `tendency_mask_melody`, `random_walk` all need to produce Notes with durations.
   - What's unclear: Whether a parameter or a hardcoded default is better.
   - Recommendation: Add an optional `duration: Duration = Duration.from_cn("q")` parameter to each function. This gives flexibility without complicating the API.

## Sources

### Primary (HIGH confidence)
- Project codebase: `src/cadenza/core/`, `src/cadenza/transforms/`, `src/cadenza/theory/scales.py`, `src/cadenza/settheory/serial.py`, `src/cadenza/patterns/` -- direct inspection of all dependency modules
- Python stdlib documentation: `random.Random`, `random.choices`, `dataclasses` -- stable stdlib APIs

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions -- direct user input, verified against codebase compatibility

### Tertiary (LOW confidence)
- None -- all algorithms are well-established and require no external research

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero external deps, all stdlib
- Architecture: HIGH -- follows exact patterns from Phases 9 and 10 (frozen dataclass, pure functions, subpackage structure)
- Pitfalls: HIGH -- well-known algorithmic edge cases (Markov dead ends, L-system explosion, walk boundaries)

**Research date:** 2026-03-22
**Valid until:** Indefinite -- algorithms and stdlib APIs are stable
