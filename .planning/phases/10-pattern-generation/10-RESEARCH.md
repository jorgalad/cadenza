# Phase 10: Pattern Generation - Research

**Researched:** 2026-03-20
**Domain:** Algorithmic pattern generation (rhythmic and melodic)
**Confidence:** HIGH

## Summary

Phase 10 implements eight pattern generation functions in a new `src/cadenza/patterns/` package. All functions are pure -- they accept tuples of primitives or `Phrase` objects and return `Phrase` or `Score`. The algorithms are well-established in music theory and computer music literature: Bjorklund's Euclidean rhythm algorithm, medieval isorhythm (talea/color cycling via LCM), binary rhythm encoding, and multi-voice distribution techniques (canon, hocket).

The domain is straightforward because: (1) the core types (`Note`, `Rest`, `Phrase`, `Score`, `Duration`, `Pitch`) are already stable and frozen, (2) all eight functions are pure with no side effects, (3) the algorithms have deterministic outputs with no randomness (except ostinato variation), and (4) the project already has a Score-returning multi-voice pattern from Phase 8's `generate_multi_voice_counterpoint`. No external dependencies are needed -- everything is built on `fractions.Fraction`, `math`, and the existing core types.

**Primary recommendation:** Implement as a `src/cadenza/patterns/` subpackage with three modules: `rhythm.py` (euclidean, binary, apply_rhythm), `melodic.py` (isorhythm, ostinato, accent), and `multivoice.py` (canon, hocket). All functions follow the established pure-function pattern from `cadenza.transforms.rhythm`.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **`euclidean_rhythm(n, m) -> tuple[bool, ...]`** -- hit/rest bitmap of length `m`, with `n` hits distributed as evenly as possible (Bjorklund's algorithm). Duration-agnostic.
- **`binary_rhythm(n) -> tuple[bool, ...]`** -- hit/rest bitmap derived from the binary representation of integer `n`. Same type as `euclidean_rhythm` output.
- **Both are duration-agnostic** -- callers use `apply_rhythm` to bind the bitmap to actual pitches/durations. No slot duration parameter.
- **`rhythmic_canon(phrase, n, offset) -> Score`** -- `n` voices each entering `offset` beats apart. Voice names: `'voice_0'`, `'voice_1'`, ..., `'voice_{n-1}'`.
- **`hocket(phrase, n) -> Score`** -- `n` voices, notes distributed round-robin across voices. Voice names: `'voice_0'`, `'voice_1'`, ..., `'voice_{n-1}'`.
- **Index-based naming** (`'voice_0'`, `'voice_1'`, ...) -- predictable, consistent with Phase 8 patterns.
- **`apply_rhythm(pitches: tuple[int, ...], rhythm: tuple[bool, ...]) -> Phrase`** -- `True` entries produce `Note` with default quarter duration; `False` entries produce `Rest`. Length mismatch: cycle the shorter one.
- **`isorhythm(talea: tuple[Duration, ...], color: tuple[int, ...], n: int) -> Phrase`** -- `n` full LCM cycles. Returns a single `Phrase`.

### Claude's Discretion

- **Ostinato variation (PATT-02)** -- exact variation strategy and `variation` parameter shape.
- **Default quarter duration in `apply_rhythm`** -- whether to use `Duration.from_cn("q")` or accept an optional `duration` parameter.
- **Canon offset unit** -- whether `offset` is a `Duration`, `Fraction` (beat count), or int.
- **Accent pattern (PATT-07)** -- exact articulation string used to mark accented notes.
- **Module location** -- `src/cadenza/patterns/` package (confirmed).

### Deferred Ideas (OUT OF SCOPE)

None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RHYT-06 | Euclidean rhythm generation (distribute N beats over M slots) | Bjorklund's algorithm produces `tuple[bool, ...]` -- well-documented, deterministic |
| PATT-01 | Generate isorhythmic patterns (talea + color) | LCM-based cycling of Duration talea and int color sequences into a single Phrase |
| PATT-02 | Generate ostinato from a phrase (loop with optional variation) | Repetition with optional callable variation function |
| PATT-03 | Apply a rhythmic pattern to a pitch sequence | `apply_rhythm` maps bool bitmap + int pitches to Note/Rest Phrase with cyclic extension |
| PATT-04 | Generate binary rhythm patterns (from integer representation) | Integer-to-binary bitmap conversion, same output type as RHYT-06 |
| PATT-05 | Rhythmic canon generation (phrase + offset voices) | Score-returning function with Rest-padded offset voices |
| PATT-06 | Hocket generation (distribute notes across voices) | Round-robin distribution into Score with Rest placeholders |
| PATT-07 | Generate accent patterns (every Nth note accented) | Add articulation string to every Nth Note's articulations tuple |

</phase_requirements>

## Standard Stack

### Core

No new dependencies. All implementations use only:

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `math` | 3.11+ | `gcd` for LCM computation | Already used throughout project |
| Python stdlib `fractions` | 3.11+ | `Fraction` for duration arithmetic | Project convention: all duration math uses Fraction |
| cadenza.core | 0.1.0 | `Note`, `Rest`, `Duration`, `Pitch`, `Phrase`, `Score` | Existing frozen dataclass types |
| cadenza.transforms.pitch | 0.1.0 | `from_midi()` for MIDI-to-Pitch conversion | Needed by `apply_rhythm` and `isorhythm` to convert int pitch classes to Pitch objects |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `dataclasses.replace` | stdlib | Rebuild frozen dataclasses with modified fields | Accent pattern: replace `articulations` tuple on Notes |
| `itertools.cycle` | stdlib | Cycle shorter sequence in apply_rhythm | Length mismatch handling |

### Alternatives Considered

None -- this phase requires no external libraries. All algorithms are simple enough to implement directly.

## Architecture Patterns

### Recommended Project Structure

```
src/cadenza/patterns/
    __init__.py          # Re-exports all public functions
    rhythm.py            # euclidean_rhythm, binary_rhythm, apply_rhythm
    melodic.py           # isorhythm, ostinato, accent_pattern
    multivoice.py        # rhythmic_canon, hocket
tests/patterns/
    __init__.py
    conftest.py          # Shared fixtures (sample phrases, durations)
    test_rhythm.py       # Tests for euclidean, binary, apply_rhythm
    test_melodic.py      # Tests for isorhythm, ostinato, accent
    test_multivoice.py   # Tests for canon, hocket
```

### Pattern 1: Duration-Agnostic Bitmap

**What:** Euclidean and binary rhythm functions return `tuple[bool, ...]` -- a pure bitmap with no duration information. Callers compose with `apply_rhythm` to create actual musical events.

**When to use:** Separating rhythm structure from duration/pitch assignment.

**Example:**
```python
from cadenza.patterns import euclidean_rhythm, apply_rhythm

bitmap = euclidean_rhythm(3, 8)  # (True, False, False, True, False, False, True, False)
phrase = apply_rhythm(pitches=(60, 64, 67), rhythm=bitmap)
# Notes on True slots (cycling pitches), Rests on False slots
```

### Pattern 2: Score Construction for Multi-Voice

**What:** Functions returning multiple voices build a `Score` using `Score(_voices=tuple(voices))` where `voices` is a list of `(name, Phrase)` tuples.

**When to use:** Canon and hocket -- any function producing named voice parts.

**Example:**
```python
# Follows counterpoint/generation.py line 964 pattern
voices = []
for i in range(n):
    voices.append((f"voice_{i}", phrase_for_voice))
return Score(_voices=tuple(voices))
```

### Pattern 3: Pure Function Convention

**What:** Every function in the patterns package is pure -- accepts immutable inputs, returns new immutable outputs, no side effects.

**When to use:** All eight functions in this phase.

**Example:**
```python
def euclidean_rhythm(n: int, m: int) -> tuple[bool, ...]:
    """Distribute n beats over m slots (Bjorklund's algorithm)."""
    if n < 0 or m <= 0 or n > m:
        raise ValueError(...)
    # ... pure computation ...
    return tuple(result)
```

### Anti-Patterns to Avoid

- **Mutable state in generators:** Do not use class instances or generators with internal state. Every function takes all inputs as parameters and returns the complete result.
- **Float duration arithmetic:** Never use float for duration computation. All duration math must use `Fraction`.
- **Direct Pitch construction in apply_rhythm:** Use `from_midi()` from `cadenza.transforms.pitch` to convert integer pitch values to properly-spelled `Pitch` objects, not raw `Pitch(step=..., accidental=..., octave=...)`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MIDI-to-Pitch conversion | Manual step/accidental/octave calculation | `cadenza.transforms.pitch.from_midi()` | Handles enharmonic spelling, edge cases at octave boundaries |
| Duration creation | Raw `Duration(fraction=...)` | `Duration.from_cn("q")` | Correctly computes fraction from base/dots/tuplet metadata |
| LCM computation | Custom LCM | `math.lcm(a, b)` (Python 3.9+) | Standard library, handles edge cases |
| Sequence cycling | Manual index modulo | `itertools.cycle` + `itertools.islice` | Cleaner, well-tested |
| Score construction | Dict-based Score | `Score(_voices=tuple(pairs))` | Matches established pattern from counterpoint module |

**Key insight:** The core types and transforms already handle all the musical complexity (pitch spelling, duration fractions, immutability). Pattern generation functions should compose these primitives, not reimplement them.

## Common Pitfalls

### Pitfall 1: Bjorklund Off-By-One

**What goes wrong:** Euclidean rhythm produces wrong number of hits or wrong distribution.
**Why it happens:** The Bresenham-style algorithm is easy to get subtly wrong with boundary conditions (n=0, n=m, n=1).
**How to avoid:** Test against known musical patterns: E(3,8) = tresillo [x..x..x.], E(5,8) = cinquillo [x.xx.xx.], E(7,16) = [x.x.xx.x.x.xx.x.]. Count total True values must equal n. Length must equal m.
**Warning signs:** Pattern looks right but has m+1 or m-1 slots.

### Pitfall 2: LCM Cycle Length in Isorhythm

**What goes wrong:** Isorhythm generates wrong number of notes per cycle.
**Why it happens:** Confusing LCM of lengths with LCM of other properties. For talea length T and color length C, one full cycle is LCM(T, C) notes.
**How to avoid:** `total_notes = n * math.lcm(len(talea), len(color))`. Index into talea with `i % len(talea)`, into color with `i % len(color)`.
**Warning signs:** Pattern does not return to starting alignment after one cycle.

### Pitfall 3: Rest Duration in Hocket and Canon

**What goes wrong:** Voices in hocket/canon have wrong total duration because rests are given incorrect durations.
**Why it happens:** When distributing notes, the rests that fill "silent" slots must have the exact same duration as the note they replace.
**How to avoid:** For hocket: each voice gets either the original Note or a Rest with the same duration. For canon: leading rests must sum to exactly `i * offset`.
**Warning signs:** Score voices have different total durations when they should be aligned.

### Pitfall 4: Cyclic Mismatch in apply_rhythm

**What goes wrong:** apply_rhythm produces unexpected pitch cycling when lengths differ.
**Why it happens:** If pitches has 3 elements and rhythm has 8 True slots, the pitch index must cycle using `itertools.cycle` or modular arithmetic.
**How to avoid:** Use `itertools.cycle(pitches)` and consume one pitch per True slot. Rests consume no pitch.
**Warning signs:** Last notes in phrase have unexpected pitches, or IndexError on pitch access.

### Pitfall 5: Accent on Rest

**What goes wrong:** `accent_pattern` tries to add articulation to a Rest, which has no articulations field.
**Why it happens:** Counting "every Nth event" without distinguishing Notes from Rests.
**How to avoid:** Decision needed: count all events or only Notes. Recommend counting only Notes (musically meaningful -- you can't accent silence).
**Warning signs:** TypeError or unexpected Rest modifications.

## Code Examples

### Bjorklund's Algorithm

```python
# Source: Toussaint (2005) "The Euclidean Algorithm Generates Traditional Musical Rhythms"
# Implementation follows the Bresenham/Bjorklund approach
def euclidean_rhythm(n: int, m: int) -> tuple[bool, ...]:
    if n < 0 or m <= 0:
        raise ValueError(f"Invalid parameters: n={n}, m={m}")
    if n > m:
        raise ValueError(f"Cannot place {n} beats in {m} slots")
    if n == 0:
        return tuple(False for _ in range(m))
    if n == m:
        return tuple(True for _ in range(m))

    # Bjorklund's algorithm: distribute n ones among m slots
    groups: list[list[bool]] = [[True] for _ in range(n)] + [[False] for _ in range(m - n)]
    while True:
        remainder = len(groups) - n
        if remainder <= 1:
            break
        new_groups = []
        for i in range(min(n, remainder)):
            new_groups.append(groups[i] + groups[n + i])
        # Remaining unmatched groups
        for i in range(min(n, remainder), n):
            new_groups.append(groups[i])
        if remainder > n:
            for i in range(n + n, len(groups)):
                new_groups.append(groups[i])
        groups = new_groups
        n = min(n, remainder)  # Update for next iteration

    result: list[bool] = []
    for group in groups:
        result.extend(group)
    return tuple(result)
```

### Isorhythm via LCM Cycling

```python
import math
from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.transforms.pitch import from_midi

def isorhythm(
    talea: tuple[Duration, ...],
    color: tuple[int, ...],
    n: int = 1,
) -> Phrase:
    if not talea or not color:
        raise ValueError("talea and color must be non-empty")
    if n < 1:
        raise ValueError("n must be >= 1")

    cycle_len = math.lcm(len(talea), len(color))
    total = n * cycle_len
    events: list[Note] = []
    for i in range(total):
        dur = talea[i % len(talea)]
        pitch = from_midi(color[i % len(color)])
        events.append(Note(pitch=pitch, duration=dur))
    return tuple(events)
```

### Canon with Rest Padding

```python
from fractions import Fraction
from cadenza.core.duration import Duration
from cadenza.core.note import Rest
from cadenza.core.score import Score
from cadenza.core.phrase import Phrase

def rhythmic_canon(phrase: Phrase, n: int, offset: Duration) -> Score:
    if not phrase or n < 1:
        raise ValueError("phrase must be non-empty and n >= 1")

    voices: list[tuple[str, Phrase]] = []
    for i in range(n):
        if i == 0:
            voices.append((f"voice_{i}", phrase))
        else:
            # Leading rest = i * offset duration
            rest_dur = Duration(fraction=offset.fraction * i, base=offset.base)
            leading_rest = (Rest(duration=rest_dur),)
            voices.append((f"voice_{i}", leading_rest + phrase))
    return Score(_voices=tuple(voices))
```

### Hocket Distribution

```python
def hocket(phrase: Phrase, n: int) -> Score:
    if not phrase or n < 1:
        raise ValueError("phrase must be non-empty and n >= 1")

    voice_events: list[list[Event]] = [[] for _ in range(n)]
    for idx, event in enumerate(phrase):
        target = idx % n
        for v in range(n):
            if v == target:
                voice_events[v].append(event)
            else:
                # Silent slot: Rest with same duration
                voice_events[v].append(Rest(duration=event.duration))

    voices = [(f"voice_{v}", tuple(voice_events[v])) for v in range(n)]
    return Score(_voices=tuple(voices))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Euclidean rhythm as list of ints (0/1) | Boolean tuple `tuple[bool, ...]` | Project convention | Type safety, composable with `apply_rhythm` |
| Isorhythm with coupled rhythm+pitch | Separated talea (Duration) + color (int) | Medieval technique, standard in algorithmic composition | Clean separation of concerns |

**Deprecated/outdated:**
- None relevant -- these are classical algorithms with stable interfaces.

## Discretion Recommendations

### Ostinato Variation (PATT-02)

**Recommendation:** Accept an optional `variation: Callable[[Phrase, int], Phrase] | None` parameter where the callable receives the phrase and the repetition index (0-based). Default `None` means exact repetition.

**Rationale:** A callable is the most flexible approach -- callers can implement any variation strategy (pitch substitution, dynamic shift, ornament) without the ostinato function needing to know about them. This matches the project's pure-function philosophy. Example usage:
```python
def add_accent_on_repeat(phrase, i):
    if i > 0:
        return accent_pattern(phrase, n=2)  # Accent every 2nd note on repeats
    return phrase

result = ostinato(phrase, repeats=4, variation=add_accent_on_repeat)
```

### Default Duration in apply_rhythm

**Recommendation:** Use `Duration.from_cn("q")` as default, with an optional `slot_duration: Duration | None = None` parameter. When `None`, use quarter note.

**Rationale:** Quarter note is the most common default in music notation. The optional parameter costs nothing and gives callers control when needed.

### Canon Offset Unit

**Recommendation:** Use `Duration` as the offset type.

**Rationale:** `Duration` is already the established type for time values in the codebase. It carries both the exact `Fraction` value and CN metadata for round-trip fidelity. Using `Fraction` or `int` would lose metadata. Example: `rhythmic_canon(phrase, n=3, offset=Duration.from_cn("h"))` -- a half-note offset is natural and readable.

### Accent Articulation String

**Recommendation:** Use `'accent'` as the articulation string, matching the existing NOTA-07 articulation vocabulary.

**Rationale:** The project's parser/serializer already handles `'accent'` as a recognized articulation marking. Using `'>'` would require mapping logic.

## Open Questions

1. **Ostinato total length control**
   - What we know: Ostinato repeats a phrase N times.
   - What's unclear: Should there be a `total_duration` parameter as an alternative to `repeats` count? (e.g., "loop for 8 bars")
   - Recommendation: Start with `repeats: int` only. Duration-based looping can be added later if needed.

2. **Canon trailing alignment**
   - What we know: Later canon voices start later and therefore extend beyond the first voice.
   - What's unclear: Should trailing rests be added to earlier voices so all voices have equal total duration?
   - Recommendation: Do NOT pad trailing rests. Score already supports unequal voice lengths, and padding adds complexity without musical benefit.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python3 -m pytest tests/patterns/ -x -q` |
| Full suite command | `python3 -m pytest tests/ -v --tb=short` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RHYT-06 | Euclidean rhythm: E(3,8) = tresillo, E(5,8) = cinquillo, edge cases (0,m), (m,m) | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_euclidean_rhythm -x` | No -- Wave 0 |
| PATT-01 | Isorhythm: talea/color cycling, LCM alignment, multi-cycle | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_isorhythm -x` | No -- Wave 0 |
| PATT-02 | Ostinato: exact repeat, with variation callback | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_ostinato -x` | No -- Wave 0 |
| PATT-03 | apply_rhythm: bitmap+pitches, cyclic extension, all-rests | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_apply_rhythm -x` | No -- Wave 0 |
| PATT-04 | Binary rhythm: known integers (e.g., 0b10110 = [T,F,T,T,F]) | unit | `python3 -m pytest tests/patterns/test_rhythm.py::test_binary_rhythm -x` | No -- Wave 0 |
| PATT-05 | Rhythmic canon: offset alignment, voice count, Score structure | unit | `python3 -m pytest tests/patterns/test_multivoice.py::test_rhythmic_canon -x` | No -- Wave 0 |
| PATT-06 | Hocket: round-robin distribution, rest durations, no simultaneous notes | unit | `python3 -m pytest tests/patterns/test_multivoice.py::test_hocket -x` | No -- Wave 0 |
| PATT-07 | Accent pattern: every Nth note accented, skip rests | unit | `python3 -m pytest tests/patterns/test_melodic.py::test_accent_pattern -x` | No -- Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/patterns/ -x -q`
- **Per wave merge:** `python3 -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/patterns/__init__.py` -- empty init for test package
- [ ] `tests/patterns/conftest.py` -- shared fixtures (sample Phrase, Duration tuples)
- [ ] `tests/patterns/test_rhythm.py` -- covers RHYT-06, PATT-03, PATT-04
- [ ] `tests/patterns/test_melodic.py` -- covers PATT-01, PATT-02, PATT-07
- [ ] `tests/patterns/test_multivoice.py` -- covers PATT-05, PATT-06
- [ ] `src/cadenza/patterns/__init__.py` -- subpackage init with re-exports

## Sources

### Primary (HIGH confidence)

- Existing codebase: `src/cadenza/core/note.py`, `score.py`, `duration.py`, `pitch.py`, `phrase.py` -- all core type definitions
- Existing codebase: `src/cadenza/transforms/rhythm.py` -- established pure-function pattern for rhythm operations
- Existing codebase: `src/cadenza/counterpoint/generation.py` line 964 -- `Score(_voices=tuple(voices))` construction pattern
- Existing codebase: `src/cadenza/counterpoint/__init__.py` -- subpackage `__init__` re-export pattern

### Secondary (MEDIUM confidence)

- Toussaint, G. (2005). "The Euclidean Algorithm Generates Traditional Musical Rhythms" -- standard reference for Bjorklund's algorithm. Well-known verified patterns: E(3,8)=tresillo, E(5,8)=cinquillo, E(7,16)
- Medieval isorhythm: talea/color cycling is a standard technique documented in all algorithmic composition textbooks

### Tertiary (LOW confidence)

- None -- all algorithms in this phase are well-established with high-confidence references.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero new dependencies, all stdlib + existing core types
- Architecture: HIGH -- follows established patterns from Phases 2 and 8
- Pitfalls: HIGH -- algorithms are simple and well-documented, pitfalls are known
- Discretion areas: MEDIUM -- recommendations are reasonable but untested; planner should validate

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (stable domain, no fast-moving dependencies)
