# Phase 6: Batch Operations & Analysis - Research

**Researched:** 2026-03-19
**Domain:** Batch phrase mutations and phrase analysis/inspection (pure Python, zero dependencies)
**Confidence:** HIGH

## Summary

Phase 6 adds two complementary capability sets to Cadenza: (1) batch mutation operations that produce new Phrase objects by modifying notes matching conditions, and (2) analysis/inspection functions that return structured data about phrases. Both follow the established immutable pattern -- frozen dataclasses, tuple-based Phrases, `dataclasses.replace()` for field updates.

The codebase already contains all the building blocks: `_map_pitches`, `_map_durations`, `omit` (predicate-based filtering), `pitch_map`, `quantize`, `Interval.between()`, the `_pitch_class_histogram` helper in keys.py, and the `ChordMatch`/`KeyResult` frozen dataclass pattern. Phase 6 functions are compositions of these existing primitives plus new iteration logic. No external libraries are needed -- the entire phase uses only Python stdlib (`random`, `dataclasses`, `fractions`, `math`, `collections`).

**Primary recommendation:** Organize batch operations in `src/cadenza/batch/` (new package) and analysis functions in `src/cadenza/analysis/phrases.py` (extending existing analysis package). Follow the `_map_*` private helper + public function composition pattern from transforms. Use `dataclasses.replace()` for all note mutations.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Crescendo/Decrescendo (BATCH-03):** Proportional mapping -- distribute dynamics linearly across note count, rounding to nearest available dynamic level. Rests skip (only Notes consume positions). `crescendo(phrase, start, end)` requires `start < end` (ValueError). Separate `decrescendo(phrase, start, end)` requires `start > end` (ValueError). No auto-direction detection.
- **Humanize (BATCH-06):** Dynamics only -- shift each Note's dynamic by +/-1 step randomly. Notes with `dynamic=None` unchanged. Rests pass through. Clamp at extremes (ppp/fff). `humanize(phrase, seed=None)` -- optional seed for determinism.
- **melodic_contour return type:** `list[str]` with `['U', 'D', 'S']` symbols. Length = consecutive Note pairs (skipping Rests). Plain strings, no enum.
- **find_motifs return type:** `list[MotifMatch]` where `MotifMatch(motif: Phrase, positions: list[int])` is a frozen dataclass. Groups all occurrences of each distinct motif.
- **phrase_similarity return type:** `float` 0.0-1.0. `1.0` = identical, `0.0` = completely different. Combines pitch/rhythm/contour sub-scores internally.
- **interval_sequence return type:** `list[Interval]` -- skips Rests, returns intervals between consecutive Note events only.
- **Windowed Transform (BATCH-09):** `apply_windowed(phrase, fn, window_size: int, step: int | None = None) -> Phrase`. Step defaults to window_size (non-overlapping). Partial tail window included. Returns single concatenated Phrase.

### Claude's Discretion
- Exact complexity scoring algorithm for ANAL-06 (melodic complexity score) -- combine interval variety, rhythm variety, and contour change count in whatever proportion produces musically sensible results.
- Internal representation of `MotifMatch.positions` -- 0-based note index vs. onset time as Fraction.
- `detect_sequence(phrase1, phrase2)` (ANAL-09) detection algorithm -- exact imitation, transposed imitation, or both.
- `rhythmic_density(phrase)` (ANAL-05) time window granularity.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BATCH-01 | Set articulation on every Nth note | `_map_notes_nth` helper + `dataclasses.replace(note, articulations=...)` |
| BATCH-02 | Set dynamic on every Nth note | `_map_notes_nth` helper + `dataclasses.replace(note, dynamic=...)` |
| BATCH-03 | Crescendo/decrescendo across phrase | Ordered DYNAMICS list + proportional index mapping across Note-only events |
| BATCH-04 | Add/remove articulation by predicate | Predicate pattern from `omit()` + articulation tuple manipulation |
| BATCH-05 | Quantize note lengths to grid | Reuse/delegate to existing `rhythm.quantize()` or follow same `_snap` pattern |
| BATCH-06 | Humanize dynamics | `random.Random(seed)` for determinism + DYNAMICS ordered list + clamp logic |
| BATCH-07 | Replace pitch/pitch class | Wrap existing `pitch_map()` with equality/pitch-class comparison |
| BATCH-08 | Filter phrase by predicate | Generalization of existing `omit()` -- keep matching instead of remove matching |
| BATCH-09 | Windowed transform | Slice phrase into windows, apply fn to each, concatenate results |
| ANAL-01 | Ambitus (highest/lowest pitch) | `min/max` over Note pitches by `midi_number`, return `(Pitch, Pitch)` |
| ANAL-02 | Melodic contour | Pairwise Note comparison by midi_number, return `['U','D','S']` list |
| ANAL-03 | Interval sequence | `Interval.between()` on consecutive Note pairs (skip Rests) |
| ANAL-04 | Pitch class histogram | Reuse `_pitch_class_histogram` from keys.py or extract shared helper |
| ANAL-05 | Rhythmic density | Accumulate onset times via `Fraction`, count notes per time window |
| ANAL-06 | Melodic complexity score | Combine interval variety + rhythm variety + contour changes (discretion) |
| ANAL-07 | Find motifs | Sliding window substring matching on Note sequences; `MotifMatch` frozen dataclass |
| ANAL-08 | Phrase similarity | Combine pitch/rhythm/contour sub-scores into 0.0-1.0 float |
| ANAL-09 | Detect sequence/imitation | Compare phrase2 against sliding windows of phrase1, with optional transposition |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib only | 3.11+ | All operations | Zero-dependency core is a project constraint |
| `dataclasses.replace` | stdlib | Immutable field updates | Established pattern throughout codebase |
| `fractions.Fraction` | stdlib | Duration arithmetic | All duration math uses Fraction, never float |
| `random.Random` | stdlib | Humanize reproducibility | Instance-based RNG with seed for determinism |
| `collections.Counter` | stdlib | Histogram/frequency counting | Cleaner than manual dict for pitch class histogram |

### Supporting
No external libraries needed. All building blocks exist in the codebase.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual similarity | difflib.SequenceMatcher | Built-in but designed for text; music similarity needs pitch/rhythm/contour weighting |
| Manual histogram | collections.Counter | Counter is cleaner; existing `_pitch_class_histogram` uses manual list which works fine too |

**Installation:** No new dependencies required.

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/
  batch/
    __init__.py          # Re-exports all batch functions
    mutations.py         # BATCH-01..04 (articulation/dynamic batch ops)
    pitch_ops.py         # BATCH-07 (pitch replacement), BATCH-08 (filter)
    rhythm_ops.py        # BATCH-05 (quantize lengths)
    humanize.py          # BATCH-06 (randomized dynamic perturbation)
    windowed.py          # BATCH-09 (apply_windowed)
  analysis/
    __init__.py          # Updated: add new exports
    chords.py            # Existing (unchanged)
    harmony.py           # Existing (unchanged)
    keys.py              # Existing (unchanged)
    phrases.py           # NEW: ANAL-01..09
tests/
  batch/
    __init__.py
    test_mutations.py    # Tests for BATCH-01..04
    test_pitch_ops.py    # Tests for BATCH-07, BATCH-08
    test_rhythm_ops.py   # Tests for BATCH-05
    test_humanize.py     # Tests for BATCH-06
    test_windowed.py     # Tests for BATCH-09
  analysis/
    test_phrases.py      # NEW: Tests for ANAL-01..09 (extends existing test dir)
```

**Alternative (simpler):** All batch ops in a single `batch/operations.py`. Given 9 operations with distinct concerns, splitting by domain (mutations, pitch, rhythm, humanize, windowed) is cleaner and more aligned with the transforms package pattern.

**Recommendation for discretion items:**

- **MotifMatch.positions:** Use 0-based event index (index into the Phrase tuple). This is consistent with how `omit()` and `permute()` work -- they operate on event indices. Onset-time representation would require computing cumulative durations, adding complexity without clear benefit for the motif use case.

- **detect_sequence (ANAL-09):** Support both exact and transposed imitation. Check for exact match first (direct pitch comparison), then check transposition (compare interval sequences). Return a result indicating which type was detected. This is practical and covers the most common musical use cases.

- **rhythmic_density (ANAL-05):** Use beat-level granularity (quarter note = `Fraction(1,4)` as default window). Return `list[float]` where each element is notes-per-beat for that time window. Allow an optional `window` parameter for different granularities.

- **complexity_score (ANAL-06):** Normalize three sub-scores to 0.0-1.0 each, then average: (1) interval variety = unique interval count / total intervals, (2) rhythm variety = unique duration count / total events, (3) contour change rate = direction changes / total contour points. Simple, transparent, and musically sensible.

### Pattern 1: Batch Note Mapping with Nth-Note Logic
**What:** A private helper that iterates over a Phrase, applies a mutation function to every Nth Note (skipping Rests), and returns a new Phrase.
**When to use:** BATCH-01, BATCH-02
**Example:**
```python
# Follows _map_pitches / _map_durations pattern from transforms
def _map_nth_notes(
    phrase: Phrase,
    n: int,
    fn: Callable[[Note], Note],
) -> Phrase:
    """Apply fn to every nth Note in phrase. Rests are skipped in counting."""
    note_count = 0
    result: list[Event] = []
    for event in phrase:
        if isinstance(event, Note):
            note_count += 1
            if note_count % n == 0:
                result.append(fn(event))
            else:
                result.append(event)
        else:
            result.append(event)
    return tuple(result)
```

### Pattern 2: Ordered Dynamic Constants
**What:** An ordered tuple of dynamic levels for crescendo/humanize operations.
**When to use:** BATCH-03, BATCH-06
**Example:**
```python
DYNAMICS: tuple[str, ...] = ("ppp", "pp", "p", "mp", "mf", "f", "ff", "fff")
DYNAMIC_INDEX: dict[str, int] = {d: i for i, d in enumerate(DYNAMICS)}
```

### Pattern 3: Frozen Dataclass Result Type
**What:** Follow ChordMatch/KeyResult pattern for MotifMatch.
**When to use:** ANAL-07
**Example:**
```python
@dataclass(frozen=True, slots=True)
class MotifMatch:
    """A repeated motif found within a phrase."""
    motif: Phrase  # The motif itself as a sub-phrase
    positions: list[int]  # 0-based event indices where motif starts
```
Note: `list[int]` is mutable inside a frozen dataclass. This is acceptable since the dataclass only prevents reassignment of the field itself. Alternatively, use `tuple[int, ...]` for full immutability consistency.

### Pattern 4: Analysis Helper -- Extract Notes Only
**What:** Many analysis functions need to iterate over Notes only, skipping Rests.
**When to use:** ANAL-01 through ANAL-09
**Example:**
```python
def _extract_notes(phrase: Phrase) -> list[Note]:
    """Extract only Note events from a phrase, preserving order."""
    return [e for e in phrase if isinstance(e, Note)]
```

### Anti-Patterns to Avoid
- **Mutating events in place:** Never. Always use `dataclasses.replace()` to create new Note/Rest objects.
- **Float duration arithmetic:** Always use `Fraction`. The project explicitly forbids float for durations.
- **Importing private helpers cross-package:** The codebase duplicates `_build_pitch` rather than importing it across packages. Follow this pattern -- if `_pitch_class_histogram` is needed in phrases.py, either extract to a shared module or duplicate.
- **Returning None for empty results:** Raise `ValueError` for invalid inputs. Return empty collections for valid-but-empty inputs (e.g., empty phrase -> empty list for contour).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pitch class histogram | Manual counting loop | Reuse pattern from `keys._pitch_class_histogram` or `collections.Counter` | Already exists, tested |
| Duration quantization | New snap-to-grid logic | Delegate to or copy pattern from `rhythm.quantize()` | BATCH-05 is essentially the same operation |
| Pitch mapping over phrase | Manual Note/Rest iteration | `_map_pitches` from `transforms.pitch` | Handles Note/Rest discrimination correctly |
| Duration mapping over phrase | Manual iteration | `_map_durations` from `transforms.rhythm` | Handles both Note and Rest |
| Interval computation | Manual semitone math | `Interval.between(p1, p2)` | Handles all edge cases, compound intervals |
| Deterministic randomness | `random.seed()` global state | `random.Random(seed)` instance | Avoids polluting global RNG state |

**Key insight:** Most batch operations are thin wrappers around existing `_map_*` helpers plus domain-specific logic. The analysis functions compose `_extract_notes`, `Interval.between`, and basic statistics.

## Common Pitfalls

### Pitfall 1: Rest Handling in Note-Counting Operations
**What goes wrong:** Operations that count "every Nth note" accidentally count Rests, changing which Notes get modified.
**Why it happens:** Iterating with `enumerate()` over the full phrase counts all events.
**How to avoid:** Maintain a separate note counter that only increments for `isinstance(event, Note)`.
**Warning signs:** Tests pass with all-Note phrases but fail when Rests are interspersed.

### Pitfall 2: Dynamic None Handling in Crescendo/Humanize
**What goes wrong:** `DYNAMIC_INDEX[note.dynamic]` raises KeyError when `dynamic is None`.
**Why it happens:** Notes can have `dynamic=None` (inherits from previous note in CN semantics).
**How to avoid:** Check `note.dynamic is not None` before looking up index. For crescendo, assign dynamics to all Notes regardless. For humanize, skip None-dynamic notes per CONTEXT.md spec.
**Warning signs:** KeyError in batch operations when processing real CN-parsed phrases.

### Pitfall 3: Articulation Tuple Immutability
**What goes wrong:** Trying to `.append()` or modify `note.articulations` which is a `tuple[str, ...]`.
**Why it happens:** Tuples are immutable; batch articulation operations need to create new tuples.
**How to avoid:** Use `replace(note, articulations=note.articulations + (new_art,))` for adding, tuple comprehension for removing.
**Warning signs:** AttributeError on tuple.append or TypeError on tuple concatenation with string.

### Pitfall 4: Motif Detection Combinatorial Explosion
**What goes wrong:** Naive O(n^3) or worse motif detection on long phrases causes performance issues.
**Why it happens:** Checking all possible substrings of all lengths against all positions.
**How to avoid:** Limit search to `min_length` through `len(phrase)//2`. Use pitch-class + duration fingerprinting for fast comparison before deep equality check. Consider suffix-array-inspired approaches for long phrases.
**Warning signs:** Tests pass on short phrases but hang on phrases with 100+ notes.

### Pitfall 5: Windowed Transform Tail Truncation
**What goes wrong:** Events at the end of a phrase get silently dropped when phrase length isn't divisible by window_size.
**Why it happens:** `range(0, len(phrase), step)` stops before the tail if `len(phrase) % step != 0`.
**How to avoid:** Per CONTEXT.md spec: always include the partial tail window. Slice `phrase[i:i+window_size]` naturally handles this (Python slicing doesn't raise on overrun).
**Warning signs:** `sum(len(w) for w in windows) < len(phrase)` when it should equal.

### Pitfall 6: Phrase Equality for Motif Matching
**What goes wrong:** Two musically identical motifs don't match because Pitch spelling differs (Eb vs D#).
**Why it happens:** `Pitch` equality is spelling-sensitive (CORE-02).
**How to avoid:** For motif detection, compare by MIDI number + duration fraction, not by object equality. This is a design decision: motifs should match by sound, not spelling.
**Warning signs:** Motifs with enharmonic equivalents not detected.

## Code Examples

### Crescendo Implementation Pattern
```python
# Source: CONTEXT.md decisions + established patterns
from dataclasses import replace

DYNAMICS: tuple[str, ...] = ("ppp", "pp", "p", "mp", "mf", "f", "ff", "fff")
DYNAMIC_INDEX: dict[str, int] = {d: i for i, d in enumerate(DYNAMICS)}

def crescendo(phrase: Phrase, start: str, end: str) -> Phrase:
    if DYNAMIC_INDEX[start] >= DYNAMIC_INDEX[end]:
        raise ValueError(f"crescendo requires start < end: {start} >= {end}")

    notes = [(i, e) for i, e in enumerate(phrase) if isinstance(e, Note)]
    if not notes:
        return phrase

    start_idx = DYNAMIC_INDEX[start]
    end_idx = DYNAMIC_INDEX[end]
    n_notes = len(notes)

    result = list(phrase)
    for pos, (event_idx, note) in enumerate(notes):
        # Proportional mapping: linearly interpolate dynamic index
        if n_notes == 1:
            dyn_idx = end_idx
        else:
            dyn_idx = round(start_idx + (end_idx - start_idx) * pos / (n_notes - 1))
        result[event_idx] = replace(note, dynamic=DYNAMICS[dyn_idx])

    return tuple(result)
```

### Humanize Implementation Pattern
```python
import random
from dataclasses import replace

def humanize(phrase: Phrase, seed: int | None = None) -> Phrase:
    rng = random.Random(seed)
    result: list[Event] = []
    for event in phrase:
        if isinstance(event, Note) and event.dynamic is not None:
            idx = DYNAMIC_INDEX[event.dynamic]
            shift = rng.choice([-1, 0, 1])
            new_idx = max(0, min(len(DYNAMICS) - 1, idx + shift))
            result.append(replace(event, dynamic=DYNAMICS[new_idx]))
        else:
            result.append(event)
    return tuple(result)
```

### Windowed Transform Pattern
```python
def apply_windowed(
    phrase: Phrase,
    fn: Callable[[Phrase], Phrase],
    window_size: int,
    step: int | None = None,
) -> Phrase:
    if step is None:
        step = window_size
    if window_size < 1 or step < 1:
        raise ValueError("window_size and step must be >= 1")

    result: list[Event] = []
    i = 0
    while i < len(phrase):
        window = phrase[i:i + window_size]
        transformed = fn(window)
        result.extend(transformed)
        i += step
    return tuple(result)
```

### Melodic Contour Pattern
```python
def melodic_contour(phrase: Phrase) -> list[str]:
    notes = _extract_notes(phrase)
    contour: list[str] = []
    for i in range(1, len(notes)):
        prev_midi = notes[i - 1].pitch.midi_number
        curr_midi = notes[i].pitch.midi_number
        if curr_midi > prev_midi:
            contour.append('U')
        elif curr_midi < prev_midi:
            contour.append('D')
        else:
            contour.append('S')
    return contour
```

### Phrase Similarity Pattern
```python
def phrase_similarity(phrase1: Phrase, phrase2: Phrase) -> float:
    # Pitch similarity: compare MIDI sequences using edit-distance-like metric
    # Rhythm similarity: compare duration fraction sequences
    # Contour similarity: compare contour symbol sequences
    # Combine: average of three sub-scores
    pitch_score = _pitch_similarity(phrase1, phrase2)
    rhythm_score = _rhythm_similarity(phrase1, phrase2)
    contour_score = _contour_similarity(phrase1, phrase2)
    return (pitch_score + rhythm_score + contour_score) / 3.0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Global `random.seed()` | `random.Random(seed)` instance | Python 3.x best practice | Thread-safe, no global state pollution |
| Mutable list-based phrases | Frozen dataclass + tuple[Event, ...] | Project design decision | All operations return new objects |

**No deprecated patterns apply** -- this phase uses only stdlib and established project patterns.

## Open Questions

1. **Motif matching: sound-based or spelling-based equality?**
   - What we know: `Pitch.__eq__` is spelling-sensitive (Eb != D#). For motif detection, musical identity should probably use sound (MIDI number + duration).
   - What's unclear: Whether the user expects spelling-sensitive motif matching.
   - Recommendation: Use MIDI-number + duration-fraction comparison for motif matching (sound-based). This is musically correct -- a motif transposed enharmonically is still the same motif.

2. **SequenceMatch return type for ANAL-09**
   - What we know: CONTEXT.md says "exact imitation, transposed imitation, or both; Claude decides."
   - What's unclear: Return type not specified in CONTEXT.md.
   - Recommendation: Return a frozen dataclass `SequenceMatch(match_type: str, offset: int, transposition: Interval | None)` where match_type is "exact" or "transposed", offset is position in phrase1 where phrase2 matches, and transposition is the interval if transposed.

3. **BATCH-05 relationship to RHYT-08**
   - What we know: RHYT-08 `quantize()` already exists in `transforms.rhythm`. BATCH-05 says "Quantize all note lengths to a given grid."
   - What's unclear: Is BATCH-05 identical to RHYT-08 or does it add something?
   - Recommendation: BATCH-05 should delegate to or re-export `rhythm.quantize()`. If there's a distinction (e.g., BATCH-05 only quantizes Notes, not Rests), implement as a thin wrapper.

4. **BATCH-04 beat-position predicate**
   - What we know: Requirement says "all notes on beat 1" as example predicate.
   - What's unclear: Computing beat position requires tracking cumulative onset time, which depends on time signature context not stored in Phrase.
   - Recommendation: Accept any `Callable[[Event], bool]` predicate. Provide helper functions or documentation for onset-based predicates separately. The batch function itself should be predicate-agnostic.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `.venv/bin/pytest tests/batch/ tests/analysis/test_phrases.py -x -q` |
| Full suite command | `.venv/bin/pytest -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BATCH-01 | Set articulation every Nth note | unit | `.venv/bin/pytest tests/batch/test_mutations.py::test_set_articulation_nth -x` | Wave 0 |
| BATCH-02 | Set dynamic every Nth note | unit | `.venv/bin/pytest tests/batch/test_mutations.py::test_set_dynamic_nth -x` | Wave 0 |
| BATCH-03 | Crescendo/decrescendo | unit | `.venv/bin/pytest tests/batch/test_mutations.py::test_crescendo -x` | Wave 0 |
| BATCH-04 | Add/remove articulation by predicate | unit | `.venv/bin/pytest tests/batch/test_mutations.py::test_articulation_predicate -x` | Wave 0 |
| BATCH-05 | Quantize note lengths | unit | `.venv/bin/pytest tests/batch/test_rhythm_ops.py::test_quantize_lengths -x` | Wave 0 |
| BATCH-06 | Humanize dynamics | unit | `.venv/bin/pytest tests/batch/test_humanize.py::test_humanize -x` | Wave 0 |
| BATCH-07 | Replace pitch/pitch class | unit | `.venv/bin/pytest tests/batch/test_pitch_ops.py::test_replace_pitch -x` | Wave 0 |
| BATCH-08 | Filter phrase by predicate | unit | `.venv/bin/pytest tests/batch/test_pitch_ops.py::test_filter_phrase -x` | Wave 0 |
| BATCH-09 | Windowed transform | unit | `.venv/bin/pytest tests/batch/test_windowed.py::test_apply_windowed -x` | Wave 0 |
| ANAL-01 | Ambitus | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_ambitus -x` | Wave 0 |
| ANAL-02 | Melodic contour | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_melodic_contour -x` | Wave 0 |
| ANAL-03 | Interval sequence | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_interval_sequence -x` | Wave 0 |
| ANAL-04 | Pitch class histogram | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_pitch_class_histogram -x` | Wave 0 |
| ANAL-05 | Rhythmic density | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_rhythmic_density -x` | Wave 0 |
| ANAL-06 | Complexity score | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_complexity_score -x` | Wave 0 |
| ANAL-07 | Find motifs | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_find_motifs -x` | Wave 0 |
| ANAL-08 | Phrase similarity | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_phrase_similarity -x` | Wave 0 |
| ANAL-09 | Detect sequence | unit | `.venv/bin/pytest tests/analysis/test_phrases.py::test_detect_sequence -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/pytest tests/batch/ tests/analysis/test_phrases.py -x -q`
- **Per wave merge:** `.venv/bin/pytest -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/batch/__init__.py` -- new test package
- [ ] `tests/batch/test_mutations.py` -- covers BATCH-01, BATCH-02, BATCH-03, BATCH-04
- [ ] `tests/batch/test_pitch_ops.py` -- covers BATCH-07, BATCH-08
- [ ] `tests/batch/test_rhythm_ops.py` -- covers BATCH-05
- [ ] `tests/batch/test_humanize.py` -- covers BATCH-06
- [ ] `tests/batch/test_windowed.py` -- covers BATCH-09
- [ ] `tests/analysis/test_phrases.py` -- covers ANAL-01 through ANAL-09
- [ ] `src/cadenza/batch/__init__.py` -- new source package

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `src/cadenza/transforms/melodic.py` -- `omit`, `pitch_map` patterns
- Codebase inspection: `src/cadenza/transforms/rhythm.py` -- `_map_durations`, `quantize` patterns
- Codebase inspection: `src/cadenza/transforms/pitch.py` -- `_map_pitches` helper
- Codebase inspection: `src/cadenza/analysis/chords.py` -- `ChordMatch` frozen dataclass pattern
- Codebase inspection: `src/cadenza/analysis/keys.py` -- `KeyResult`, `_pitch_class_histogram` patterns
- Codebase inspection: `src/cadenza/core/note.py` -- `Note` fields (pitch, duration, dynamic, articulations)
- Codebase inspection: `src/cadenza/core/interval.py` -- `Interval.between()` API
- CONTEXT.md: All locked decisions for BATCH-03, BATCH-06, return types

### Secondary (MEDIUM confidence)
- None needed -- all research is based on existing codebase patterns and locked decisions

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - zero external deps, all stdlib, pattern fully understood from codebase
- Architecture: HIGH - follows established package/module patterns from transforms and analysis
- Pitfalls: HIGH - identified from direct codebase inspection of Note fields and existing edge cases

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable -- no external dependency changes possible)
