# Phase 2: Transforms - Research

**Researched:** 2026-03-19
**Domain:** Musical pitch, rhythm, and melodic transformations (pure Python, zero dependencies)
**Confidence:** HIGH

## Summary

Phase 2 implements 29 transform functions across three modules (`pitch.py`, `rhythm.py`, `melodic.py`) under `cadenza/transforms/`. All functions are pure (no mutation), accept `Phrase` (or related core types), and return new `Phrase` objects. The Phase 1 foundation provides all necessary types: `Pitch`, `Duration`, `Interval`, `Note`, `Rest`, `Event`, and `Phrase`.

The primary technical challenge is **chromatic transposition with correct enharmonic spelling**. The `Pitch` type stores letter name + accidental + octave (not MIDI), so transposing requires computing a new letter name from the interval's generic number, wrapping octaves, and deriving the correct accidental. The `Interval` type already provides `semitones` and `between()`, which are the building blocks. All other transforms are structurally simpler -- they reorganize, filter, or map over phrase elements.

**Primary recommendation:** Implement a `_transpose_pitch(pitch: Pitch, interval: Interval) -> Pitch` helper first, as it underpins `chromatic_transpose`, `invert`, and indirectly `retrograde-inversion`. All other transforms are tuple-manipulation functions with straightforward logic.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Two transposition modes, two functions: `chromatic_transpose(phrase, interval: Interval) -> Phrase` and `diatonic_transpose(phrase, n: int, scale) -> Phrase`
- Enharmonic spelling for chromatic transposition follows interval direction (augmented -> sharps, diminished/minor -> flats for downward). Deterministic, no caller config.
- Two retrograde flavors: `pitch_retrograde(phrase) -> Phrase` (reverse pitches only) and `full_retrograde(phrase) -> Phrase` (reverse entire events)
- MELO-01 maps to `pitch_retrograde`, MELO-02 = `pitch_retrograde` then `invert`
- `invert(phrase, axis: Pitch | None = None) -> Phrase` with default axis = first note. Chromatic inversion (intervals reflected exactly).
- Module layout: `cadenza/transforms/pitch.py`, `cadenza/transforms/rhythm.py`, `cadenza/transforms/melodic.py` with `__init__.py` re-exporting all
- Diatonic transpose stub: `raise NotImplementedError("Diatonic transpose requires Phase 3 scale library")`
- Rotation direction: positive N = rotate left, negative N = rotate right
- Augmentation/diminution ratio: accept `fractions.Fraction | int | float` (convert float to Fraction internally)
- Quantization grid: accept `Duration` objects or OMN duration strings

### Claude's Discretion
- Module layout details (decided above -- follow as given)
- Diatonic transpose stub behavior (decided above)
- Rotation direction convention (decided above)
- Augmentation/diminution ratio type (decided above)
- Quantization grid type (decided above)

### Deferred Ideas (OUT OF SCOPE)
- Diatonic transposition full implementation -- deferred to Phase 3 (Scale library)
- Interpolation rules (chromatic vs diatonic passing notes) -- use chromatic as default
- Omission predicates (lambda vs named conditions) -- implement both
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PTCH-01 | Transpose note/phrase by interval (diatonic and chromatic) | `chromatic_transpose` + `diatonic_transpose` stub; `_transpose_pitch` helper algorithm detailed below |
| PTCH-02 | Invert phrase around pitch axis | `invert` function using interval reflection; algorithm in Architecture Patterns |
| PTCH-03 | Compute interval between two pitches | Already implemented as `Interval.between()` in Phase 1 -- re-export or wrap |
| PTCH-04 | Enharmonic respelling | `enharmonic_respell(pitch) -> Pitch` using MIDI-to-pitch lookup table |
| PTCH-05 | Pitch class reduction | `pitch_class(pitch) -> int` -- already a property on `Pitch`, wrap as function |
| PTCH-06 | MIDI to/from Pitch conversion | `from_midi(n, prefer_sharps=True) -> Pitch` and existing `Pitch.midi_number` |
| PTCH-07 | Frequency to/from Pitch (A440) | `from_frequency(hz) -> Pitch` and `to_frequency(pitch) -> float` using A440 reference |
| PTCH-08 | Pitch membership in scale/chord | Stub that raises `NotImplementedError` -- needs Phase 3 Scale/Chord types |
| PTCH-09 | Nearest pitch in scale | Stub that raises `NotImplementedError` -- needs Phase 3 Scale type |
| RHYT-01 | Rhythmic retrograde | Reverse duration sequence, keep pitch order |
| RHYT-02 | Rhythmic augmentation | Multiply all durations by ratio |
| RHYT-03 | Rhythmic diminution | Divide all durations by ratio |
| RHYT-04 | Rhythmic rotation | Cyclic shift of durations only |
| RHYT-05 | Metric modulation | Reinterpret duration unit as new tempo reference |
| RHYT-07 | Rhythmic pattern extraction | Extract duration sequence from phrase |
| RHYT-08 | Quantize to rhythmic grid | Snap durations to nearest grid value |
| RHYT-09 | Total duration of phrase | Sum all event durations |
| MELO-01 | Melodic retrograde | `pitch_retrograde` -- reverse pitch sequence, keep rhythm |
| MELO-02 | Retrograde-inversion | `pitch_retrograde` then `invert` |
| MELO-03 | Rotation | Cyclic permutation of entire events |
| MELO-04 | Permutation | Reorder events by index list |
| MELO-05 | Interpolation | Insert chromatic passing notes between existing notes |
| MELO-06 | Omission | Remove every Nth note or notes matching predicate |
| MELO-07 | Repetition | Repeat phrase N times with optional variation callback |
| MELO-08 | Mirror (palindrome) | Phrase + retrograde of phrase |
| MELO-09 | Fragmentation | Split phrase into sub-phrases of given lengths |
| MELO-10 | Concatenation | Join phrases |
| MELO-11 | Interleave | Alternate events from two phrases |
| MELO-12 | Apply pitch mapping function | Map callable over every note's pitch |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `fractions` | 3.11+ | Duration arithmetic | Already used in Phase 1; exact rational arithmetic |
| Python stdlib `math` | 3.11+ | Frequency conversion (log2, pow) | A440 Hz calculations |
| Python stdlib `functools` | 3.11+ | Potential `reduce` for concatenation | Clean functional style |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | >=8.0 | Test framework | All tests |
| hypothesis | >=6.100 | Property-based testing | Roundtrip properties (transpose then transpose back) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom transpose logic | music21 library | music21 is a massive dependency; Cadenza is zero-dep by design |
| Hand-built frequency table | numpy | Unnecessary; `2 ** ((midi - 69) / 12) * 440` is one line |

**Installation:**
```bash
# No new dependencies -- all stdlib. Dev deps already installed from Phase 1.
pip install -e ".[dev]"
```

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/
    transforms/
        __init__.py        # Re-exports all public functions
        pitch.py           # PTCH-01..09 functions
        rhythm.py          # RHYT-01..05, 07..09 functions
        melodic.py         # MELO-01..12 functions
tests/
    transforms/
        __init__.py
        test_pitch_transforms.py
        test_rhythm_transforms.py
        test_melodic_transforms.py
        conftest.py        # Shared phrase fixtures for transforms
```

### Pattern 1: Pure Transform Function
**What:** Every transform is a module-level function that takes a Phrase (and parameters) and returns a new Phrase. No classes, no methods, no state.
**When to use:** Every transform in this phase.
**Example:**
```python
from cadenza.core.note import Note, Rest, Event
from cadenza.core.phrase import Phrase

def full_retrograde(phrase: Phrase) -> Phrase:
    """Reverse entire event sequence (classical retrograde)."""
    return phrase[::-1]
```

### Pattern 2: Event-Preserving Map
**What:** When transforming only pitches (or only durations), reconstruct Notes with changed field but preserve all other fields (dynamic, articulations). Use `dataclasses.replace()` for frozen dataclass field replacement.
**When to use:** Any transform that modifies one aspect while preserving others.
**Example:**
```python
from dataclasses import replace

def _map_pitches(phrase: Phrase, fn: Callable[[Pitch], Pitch]) -> Phrase:
    """Apply a pitch transformation to all Notes in a phrase, preserving Rests."""
    events: list[Event] = []
    for event in phrase:
        if isinstance(event, Note):
            events.append(replace(event, pitch=fn(event.pitch)))
        else:
            events.append(event)  # Rest passes through
    return tuple(events)
```

### Pattern 3: Transpose Pitch Algorithm
**What:** The core algorithm for chromatic transposition. Given a Pitch and an Interval, compute the new Pitch with correct spelling.
**When to use:** `chromatic_transpose`, `invert` (which computes intervals from axis then reflects them).
**Algorithm:**
```python
from cadenza.core.pitch import Pitch, STEP_INDEX, STEP_SEMITONES, ACCIDENTAL_SEMITONES

# Reverse maps for lookup
_INDEX_TO_STEP = {v: k for k, v in STEP_INDEX.items()}

def _transpose_pitch(pitch: Pitch, interval: Interval) -> Pitch:
    """Transpose a single pitch by an interval, preserving correct spelling."""
    # 1. Compute target letter name from generic interval number
    source_idx = STEP_INDEX[pitch.step]
    # interval.number is 1-based: unison=1, second=2, etc.
    generic_steps = interval.number - 1  # 0 for unison, 1 for second, etc.
    target_idx = (source_idx + interval.direction * generic_steps) % 7
    target_step = _INDEX_TO_STEP[target_idx]

    # 2. Compute target MIDI number
    target_midi = pitch.midi_number + interval.semitones

    # 3. Compute target octave
    # The octave is determined by the target MIDI and target step
    # target_midi = (octave + 1) * 12 + STEP_SEMITONES[target_step] + acc_semitones
    # We need to find octave and accidental such that they produce target_midi
    base_midi_at_oct0 = 12 + STEP_SEMITONES[target_step]  # octave 0
    # Find octave: target_midi should be near base_midi_at_oct0 + octave * 12
    raw_octave = (target_midi - STEP_SEMITONES[target_step]) / 12 - 1
    # Round to nearest integer, but verify
    octave = round(raw_octave)

    # 4. Compute required accidental
    natural_midi = (octave + 1) * 12 + STEP_SEMITONES[target_step]
    acc_semitones = target_midi - natural_midi

    # Map back to accidental string
    _SEMITONES_TO_ACC = {v: k for k, v in ACCIDENTAL_SEMITONES.items()}
    if acc_semitones not in _SEMITONES_TO_ACC:
        raise ValueError(f"Transposition produces out-of-range accidental: {acc_semitones}")
    accidental = _SEMITONES_TO_ACC[acc_semitones]

    return Pitch(step=target_step, accidental=accidental, octave=octave)
```

### Pattern 4: Duration Scaling
**What:** For augmentation/diminution, scale the Duration's fraction while preserving or recomputing OMN metadata.
**When to use:** RHYT-02, RHYT-03
**Key insight:** After scaling, the `base`/`dots`/`tuplet` metadata may no longer match the fraction. Two approaches: (a) store only the new fraction with a generic base, or (b) try to find the best OMN representation. Approach (a) is simpler and correct; OMN serialization can be handled by a future "best-fit" function.
```python
def _scale_duration(dur: Duration, ratio: Fraction) -> Duration:
    """Scale a duration by a ratio, returning new Duration."""
    new_fraction = dur.fraction * ratio
    # Use the original base/dots/tuplet if they still match, otherwise default
    return Duration(fraction=new_fraction, base=dur.base, dots=dur.dots, tuplet=dur.tuplet)
```

### Pattern 5: Rest Handling
**What:** Every transform must decide what to do with Rests in the phrase.
**Rules:**
- Pitch transforms: Rests pass through unchanged (no pitch to transform)
- Duration/rhythm transforms: Rests ARE affected (they have durations)
- Full retrograde: Rests reverse with everything else
- Pitch retrograde: Rests keep their position (only note pitches are reversed among notes)
- Omission: Rests can be omitted if they match the predicate
- Interleave/concatenation: Rests interleave/concatenate normally

### Anti-Patterns to Avoid
- **Mutating Events:** Never modify a Note/Rest in-place. Always use `dataclasses.replace()` or construct new instances.
- **Losing metadata:** When mapping pitches, do not construct new Notes without carrying over `dynamic` and `articulations`.
- **Float duration arithmetic:** Never use float for duration math. Always `Fraction`. The CONTEXT.md says to convert float inputs to Fraction immediately.
- **Ignoring Rests in pitch transforms:** A Phrase can contain Rests interspersed with Notes. The `_map_pitches` pattern handles this correctly by checking `isinstance`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interval semitone computation | Manual semitone tables | `Interval.semitones` property | Already implemented, tested, handles compound intervals |
| Interval between pitches | Manual letter/octave math | `Interval.between(p1, p2)` | Already implemented, handles all edge cases |
| Duration fraction computation | Manual dot/tuplet math | `Duration.from_omn()` | Already handles dots and tuplets correctly |
| Frozen dataclass field update | Manual constructor calls | `dataclasses.replace()` | Built-in, preserves all unspecified fields |

**Key insight:** Phase 1 did the hard work of encoding music theory into types. Phase 2 transforms should leverage `Interval`, `Pitch.midi_number`, and `Duration.fraction` rather than reimplementing any of that logic.

## Common Pitfalls

### Pitfall 1: Octave Boundary in Transposition
**What goes wrong:** Transposing B4 up a minor second should give C5, not C4. The letter wraps from B to C, which crosses an octave boundary.
**Why it happens:** Octave numbers in scientific pitch notation increment at C, not at the start of the alphabet.
**How to avoid:** When computing the target octave, account for the fact that going from B (index 6) to C (index 0) means +1 octave. Use MIDI number as the source of truth for the target pitch, then derive octave from it.
**Warning signs:** Tests with B->C or Cb->B transitions failing.

### Pitfall 2: Enharmonic Spelling in Inversion
**What goes wrong:** Inverting C-E (major 3rd up) around C should produce C-Ab (major 3rd down), not C-G#. The CONTEXT.md says inversion is chromatic with exact interval reflection.
**Why it happens:** Naive MIDI subtraction doesn't preserve interval spelling.
**How to avoid:** Compute the interval from axis to each note using `Interval.between()`, then apply the interval in the opposite direction. The interval carries its own quality/spelling.
**Warning signs:** Inverted phrases with sharps where flats are expected.

### Pitfall 3: Pitch Retrograde with Rests
**What goes wrong:** If a phrase is [C4, Rest, E4, G4], pitch retrograde should reverse only the note pitches: [G4, Rest, E4, C4] -- but a naive implementation might try to reverse all events or skip the rest position.
**Why it happens:** Rests have no pitch but occupy a position in the phrase.
**How to avoid:** Extract note pitches only, reverse them, then redistribute back into note positions while leaving rests in place.
**Warning signs:** IndexError or rests appearing at wrong positions.

### Pitfall 4: Duration Metadata Mismatch After Scaling
**What goes wrong:** After augmenting a quarter note (1/4) by 3x, the fraction is 3/4 but the `base` is still "q" and `dots` is 0. The OMN metadata no longer matches.
**Why it happens:** There is no standard OMN representation for 3/4 of a whole note (it would need a dotted half).
**How to avoid:** Accept that after scaling, OMN metadata may be approximate. The `fraction` field is always correct. A future "best-fit OMN" function can reconstruct metadata. For now, keep original metadata as a hint.
**Warning signs:** OMN round-trip tests failing after augmentation/diminution.

### Pitfall 5: Empty Phrase Edge Cases
**What goes wrong:** Calling any transform on an empty phrase `()` should return `()`, not raise an error.
**Why it happens:** Index access, first-note axis defaults, and zip operations fail on empty sequences.
**How to avoid:** Guard every function: `if not phrase: return ()`. For `invert` with default axis, require at least one Note or raise ValueError.
**Warning signs:** IndexError on empty input.

### Pitfall 6: Accidental Out of Range
**What goes wrong:** Transposing Dbb up by an augmented second would require a triple sharp, which is outside the supported accidental range (bb, b, n, s, ss).
**Why it happens:** The Pitch type only supports double-sharp/double-flat maximum.
**How to avoid:** Raise a clear ValueError when the required accidental exceeds the supported range. This is a legitimate musical edge case -- the caller should respell first.
**Warning signs:** KeyError in the accidental lookup table.

## Code Examples

### Chromatic Transpose (PTCH-01)
```python
def chromatic_transpose(phrase: Phrase, interval: Interval) -> Phrase:
    """Transpose all notes by the given interval. Rests pass through."""
    return _map_pitches(phrase, lambda p: _transpose_pitch(p, interval))
```

### Melodic Inversion (PTCH-02)
```python
def invert(phrase: Phrase, axis: Pitch | None = None) -> Phrase:
    """Invert phrase around axis pitch. Default axis = first note's pitch."""
    if not phrase:
        return ()
    if axis is None:
        first_note = next((e for e in phrase if isinstance(e, Note)), None)
        if first_note is None:
            return phrase  # all rests, nothing to invert
        axis = first_note.pitch

    def _invert_pitch(p: Pitch) -> Pitch:
        iv = Interval.between(axis, p)
        # Reflect: flip direction
        reflected = Interval(quality=iv.quality, number=iv.number, direction=-iv.direction)
        return _transpose_pitch(axis, reflected)

    return _map_pitches(phrase, _invert_pitch)
```

### Pitch Retrograde (MELO-01)
```python
def pitch_retrograde(phrase: Phrase) -> Phrase:
    """Reverse pitch sequence, keep original durations and positions."""
    note_indices = [i for i, e in enumerate(phrase) if isinstance(e, Note)]
    pitches = [phrase[i].pitch for i in note_indices]  # type: ignore
    pitches.reverse()

    events = list(phrase)
    for idx, pitch in zip(note_indices, pitches):
        events[idx] = replace(events[idx], pitch=pitch)  # type: ignore
    return tuple(events)
```

### Rhythmic Augmentation (RHYT-02)
```python
def augment(phrase: Phrase, ratio: Fraction | int | float) -> Phrase:
    """Multiply all durations by ratio."""
    if isinstance(ratio, float):
        ratio = Fraction(ratio).limit_denominator(1000)
    ratio = Fraction(ratio)

    return tuple(
        replace(event, duration=_scale_duration(event.duration, ratio))
        for event in phrase
    )
```

### Rotation (MELO-03)
```python
def rotate(phrase: Phrase, n: int) -> Phrase:
    """Cyclic rotation. Positive n = rotate left (first n move to end)."""
    if not phrase:
        return ()
    n = n % len(phrase)
    return phrase[n:] + phrase[:n]
```

### Total Duration (RHYT-09)
```python
def total_duration(phrase: Phrase) -> Fraction:
    """Sum of all event durations."""
    return sum((event.duration.fraction for event in phrase), Fraction(0))
```

### Frequency Conversion (PTCH-07)
```python
import math

def to_frequency(pitch: Pitch, a4_hz: float = 440.0) -> float:
    """Convert pitch to frequency in Hz. A4 = 440 Hz by default."""
    return a4_hz * (2 ** ((pitch.midi_number - 69) / 12))

def from_frequency(hz: float, a4_hz: float = 440.0, prefer_sharps: bool = True) -> Pitch:
    """Convert frequency to nearest pitch."""
    midi = round(12 * math.log2(hz / a4_hz) + 69)
    return from_midi(midi, prefer_sharps=prefer_sharps)
```

### MIDI Conversion (PTCH-06)
```python
_MIDI_TO_PITCH_SHARP: list[tuple[str, str]] = [
    ("c", "n"), ("c", "s"), ("d", "n"), ("d", "s"), ("e", "n"), ("f", "n"),
    ("f", "s"), ("g", "n"), ("g", "s"), ("a", "n"), ("a", "s"), ("b", "n"),
]
_MIDI_TO_PITCH_FLAT: list[tuple[str, str]] = [
    ("c", "n"), ("d", "b"), ("d", "n"), ("e", "b"), ("e", "n"), ("f", "n"),
    ("g", "b"), ("g", "n"), ("a", "b"), ("a", "n"), ("b", "b"), ("b", "n"),
]

def from_midi(midi_number: int, prefer_sharps: bool = True) -> Pitch:
    """Convert MIDI number to Pitch. Default prefers sharps for black keys."""
    table = _MIDI_TO_PITCH_SHARP if prefer_sharps else _MIDI_TO_PITCH_FLAT
    octave = (midi_number // 12) - 1
    pc = midi_number % 12
    step, acc = table[pc]
    return Pitch(step=step, accidental=acc, octave=octave)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Mutable note objects | Frozen dataclasses with `replace()` | Phase 1 design | All transforms return new objects; no side effects |
| Class methods for transforms | Module-level pure functions | Phase 1 decision | Transforms are composable: `invert(pitch_retrograde(phrase))` |
| Float-based duration | Fraction-based duration | Phase 1 design | Exact arithmetic; no rounding errors in augmentation/diminution |

**Note on this domain:** Musical transformations are well-defined by centuries of music theory. There are no "recent changes" -- retrograde, inversion, transposition, and augmentation are the same operations they were in the 18th century. The implementation challenge is purely in correct data modeling, which Phase 1 has already solved.

## Open Questions

1. **Duration metadata after scaling**
   - What we know: `Duration.fraction` is always exact after scaling. But `base`/`dots`/`tuplet` may not match.
   - What's unclear: Should we attempt to find the best-fit OMN representation, or leave metadata as-is?
   - Recommendation: Leave metadata as-is for now. The fraction is the source of truth. A "best-fit OMN" function is a separate concern (could be added in a later phase or as a utility).

2. **PTCH-08 and PTCH-09 scope**
   - What we know: These require Scale/Chord types that don't exist until Phase 3.
   - What's unclear: Should we create stubs or skip entirely?
   - Recommendation: Create function stubs with `NotImplementedError`, matching the `diatonic_transpose` pattern. This establishes the API surface early.

3. **RHYT-05 Metric Modulation semantics**
   - What we know: Metric modulation reinterprets a duration unit as a new tempo reference. For example, "dotted quarter = new quarter" means the old dotted quarter duration becomes the new beat unit.
   - What's unclear: The exact API signature. This is more of a tempo/beat concept than a phrase-level transform.
   - Recommendation: Implement as `metric_modulation(phrase: Phrase, old_unit: Duration, new_unit: Duration) -> Phrase` which scales all durations by `new_unit.fraction / old_unit.fraction`. This is mathematically equivalent to augmentation with a specific ratio.

4. **MELO-05 Interpolation passing notes**
   - What we know: CONTEXT.md defers the chromatic vs diatonic question and says use chromatic as default.
   - What's unclear: How many passing notes to insert (just one, or fill chromatically)?
   - Recommendation: Insert a single chromatic passing note between each pair of notes. Accept an optional `steps` parameter for how many interpolation notes. Duration of inserted notes should be evenly subdivided from the first note's duration.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=8.0 + hypothesis >=6.100 |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `python -m pytest tests/transforms/ -x -q` |
| Full suite command | `python -m pytest tests/ -v --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PTCH-01 | Chromatic transpose, diatonic stub | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_chromatic_transpose -x` | No - Wave 0 |
| PTCH-02 | Melodic inversion | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_invert -x` | No - Wave 0 |
| PTCH-03 | Interval between pitches | unit | `python -m pytest tests/core/test_interval.py -x` | Yes (Phase 1) |
| PTCH-04 | Enharmonic respelling | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_enharmonic_respell -x` | No - Wave 0 |
| PTCH-05 | Pitch class reduction | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_pitch_class -x` | No - Wave 0 |
| PTCH-06 | MIDI conversion | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_midi_conversion -x` | No - Wave 0 |
| PTCH-07 | Frequency conversion | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_frequency_conversion -x` | No - Wave 0 |
| PTCH-08 | Scale membership (stub) | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_scale_membership_stub -x` | No - Wave 0 |
| PTCH-09 | Nearest in scale (stub) | unit | `python -m pytest tests/transforms/test_pitch_transforms.py::test_nearest_in_scale_stub -x` | No - Wave 0 |
| RHYT-01 | Rhythmic retrograde | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_rhythmic_retrograde -x` | No - Wave 0 |
| RHYT-02 | Rhythmic augmentation | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_augment -x` | No - Wave 0 |
| RHYT-03 | Rhythmic diminution | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_diminish -x` | No - Wave 0 |
| RHYT-04 | Rhythmic rotation | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_rhythmic_rotation -x` | No - Wave 0 |
| RHYT-05 | Metric modulation | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_metric_modulation -x` | No - Wave 0 |
| RHYT-07 | Pattern extraction | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_pattern_extraction -x` | No - Wave 0 |
| RHYT-08 | Quantize to grid | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_quantize -x` | No - Wave 0 |
| RHYT-09 | Total duration | unit | `python -m pytest tests/transforms/test_rhythm_transforms.py::test_total_duration -x` | No - Wave 0 |
| MELO-01 | Pitch retrograde | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_pitch_retrograde -x` | No - Wave 0 |
| MELO-02 | Retrograde-inversion | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_retrograde_inversion -x` | No - Wave 0 |
| MELO-03 | Rotation | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_rotate -x` | No - Wave 0 |
| MELO-04 | Permutation | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_permute -x` | No - Wave 0 |
| MELO-05 | Interpolation | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_interpolate -x` | No - Wave 0 |
| MELO-06 | Omission | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_omit -x` | No - Wave 0 |
| MELO-07 | Repetition | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_repeat -x` | No - Wave 0 |
| MELO-08 | Mirror | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_mirror -x` | No - Wave 0 |
| MELO-09 | Fragmentation | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_fragment -x` | No - Wave 0 |
| MELO-10 | Concatenation | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_concatenate -x` | No - Wave 0 |
| MELO-11 | Interleave | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_interleave -x` | No - Wave 0 |
| MELO-12 | Pitch map function | unit | `python -m pytest tests/transforms/test_melodic_transforms.py::test_pitch_map -x` | No - Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/transforms/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/transforms/__init__.py` -- empty init for test package
- [ ] `tests/transforms/conftest.py` -- shared phrase fixtures (C major scale phrase, simple 4-note phrase, phrase with rests)
- [ ] `tests/transforms/test_pitch_transforms.py` -- all PTCH-01..09 tests
- [ ] `tests/transforms/test_rhythm_transforms.py` -- all RHYT-01..05, 07..09 tests
- [ ] `tests/transforms/test_melodic_transforms.py` -- all MELO-01..12 tests
- [ ] `src/cadenza/transforms/__init__.py` -- package init with re-exports
- [ ] `src/cadenza/transforms/pitch.py` -- pitch transform functions
- [ ] `src/cadenza/transforms/rhythm.py` -- rhythm transform functions
- [ ] `src/cadenza/transforms/melodic.py` -- melodic transform functions

### Key Test Cases (Canonical)
- **Transpose C major up m3:** `[C4,D4,E4,F4,G4,A4,B4]` -> `[Eb4,F4,G4,Ab4,Bb4,C5,D5]` (all flats, not sharps)
- **Invert C-E-G around C4:** intervals M3 up, P5 up become M3 down, P5 down -> `[C4, Ab3, F3]`
- **Retrograde of [C4,D4,E4] with durations [q,e,h]:** pitch retrograde -> pitches [E4,D4,C4] with durations [q,e,h]; full retrograde -> [E4(h), D4(e), C4(q)]
- **Augment by 2:** quarter -> half, eighth -> quarter
- **Empty phrase for all transforms:** should return `()`

## Sources

### Primary (HIGH confidence)
- `src/cadenza/core/pitch.py` -- Pitch type API, STEP_INDEX, STEP_SEMITONES, ACCIDENTAL_SEMITONES maps
- `src/cadenza/core/interval.py` -- Interval type, `between()`, `semitones` property, MAJOR_SCALE_SEMITONES
- `src/cadenza/core/duration.py` -- Duration type, `from_omn()`, Fraction arithmetic
- `src/cadenza/core/note.py` -- Note, Rest, Event type alias
- `src/cadenza/core/phrase.py` -- Phrase type alias (tuple[Event, ...])
- `.planning/phases/02-transforms/02-CONTEXT.md` -- All locked implementation decisions

### Secondary (MEDIUM confidence)
- Standard music theory references for transform definitions (retrograde, inversion, augmentation, etc.) -- these are centuries-old, well-defined operations

### Tertiary (LOW confidence)
- None -- this phase is pure algorithmic implementation on well-defined types with no external dependencies

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero external deps, all stdlib + existing types
- Architecture: HIGH -- follows Phase 1 patterns exactly, all decisions locked in CONTEXT.md
- Pitfalls: HIGH -- derived from direct analysis of the Pitch/Interval/Duration type implementations
- Code examples: MEDIUM -- algorithm for `_transpose_pitch` needs validation through testing; the octave computation has known edge cases at B/C boundary

**Research date:** 2026-03-19
**Valid until:** Indefinitely -- this is foundational music theory + Python stdlib; nothing will become stale
