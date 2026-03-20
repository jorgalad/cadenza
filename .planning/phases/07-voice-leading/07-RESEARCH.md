# Phase 7: Voice Leading - Research

**Researched:** 2026-03-20
**Domain:** Voice leading analysis and generation (music theory)
**Confidence:** HIGH

## Summary

Phase 7 implements two capabilities: (1) detection of voice leading violations in multi-voice passages, and (2) generation of smooth voice connections. The domain is well-understood classical music theory with deterministic rules -- no external libraries needed. All logic operates on existing `Score`, `Phrase`, `Pitch`, and `Interval` types from the Cadenza core.

The implementation is pure algorithmic music theory: iterating voice pairs, computing intervals at consecutive positions, and flagging specific interval motion patterns. The generation side (VLEAD-05, VLEAD-08) involves combinatorial optimization (permutation search for minimum semitone movement) and greedy beat-by-beat voice assignment. Both are computationally tractable for typical musical passages (4 voices, tens to hundreds of beats).

**Primary recommendation:** Create a single `src/cadenza/analysis/voiceleading.py` module following the frozen-dataclass + pure-function pattern established by `analysis/chords.py` and `analysis/phrases.py`. No external dependencies needed.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Primary input type:** `Score` object (existing `cadenza.core.Score` which holds `tuple[tuple[str, Phrase], ...]`)
- **Voice ordering:** Follows Score tuple order -- caller decides, no auto-detection
- **Position semantics:** 0-based note index within each voice's Phrase
- **Iteration:** Violation-detection functions accept a `Score` and check ALL voice pairs internally
- **VoiceLeadingViolation dataclass:** `(rule: str, voice1: str, voice2: str, position: int, interval: Interval, severity: str)` -- frozen
  - `rule`: snake_case string from: `'parallel_fifth'`, `'parallel_octave'`, `'voice_crossing'`, `'voice_overlap'`, `'large_leap'`, `'augmented_leap'`
  - `severity`: `'error'` / `'warning'` / `'suggestion'`
- **check_voice_leading(score: Score) -> list[VoiceLeadingViolation]** -- returns all violations sorted by position
- **smooth_voice_leading(chord1: tuple[Pitch, ...], chord2: tuple[Pitch, ...]) -> tuple[Pitch, ...]** -- minimizes total semitone movement, raises ValueError on size mismatch
- **generate_inner_voices(soprano: Phrase, bass: Phrase, n: int = 2, ranges: list[tuple[Pitch, Pitch]] | None = None) -> list[Phrase]** -- greedy minimization, no violation checking
- Default SATB ranges: Alto C3-G5, Tenor C2-G4
- No violation checking in smooth_voice_leading or generate_inner_voices (single responsibility)

### Claude's Discretion
- Tie-breaking for smooth_voice_leading when multiple permutations tie
- Whether generate_inner_voices reuses permutation search or uses separate greedy heuristic
- Individual detector function signatures for VLEAD-01..06 (public or private, called through check_voice_leading)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| VLEAD-01 | Detect parallel fifths between any two voices | Interval.between at consecutive positions; check for P5->P5 motion |
| VLEAD-02 | Detect parallel octaves between any two voices | Same pattern as VLEAD-01; check for P8/P1->P8/P1 motion |
| VLEAD-03 | Detect voice crossing (lower voice exceeds upper voice in pitch) | Compare MIDI numbers at each position between adjacent voices |
| VLEAD-04 | Detect voice overlap (voice moves to pitch beyond previous pitch of adjacent voice) | Compare current pitch of one voice to previous pitch of adjacent voice |
| VLEAD-05 | Find smoothest voice leading between two chords | Permutation search minimizing sum of abs(semitone) differences |
| VLEAD-06 | Detect large leaps and augmented/diminished leaps | Single-voice interval analysis; threshold at >12 semitones and A/d quality |
| VLEAD-07 | Check all standard voice leading rules, return violation list | Orchestrate VLEAD-01..06 detectors over all voice pairs |
| VLEAD-08 | Generate smooth inner voice parts given soprano and bass | Greedy beat-by-beat pitch selection within range constraints |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib only | 3.11+ | All voice leading logic | Pure algorithmic music theory; no external deps match project convention |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `itertools` | stdlib | `permutations()` for VLEAD-05 chord voicing search | Finding minimum-movement voice assignments |
| `itertools` | stdlib | `combinations()` for generating voice pairs | Checking all voice pairs in VLEAD-07 |
| `dataclasses` | stdlib | `@dataclass(frozen=True, slots=True)` for VoiceLeadingViolation | Consistent with ChordMatch, MotifMatch patterns |

### Alternatives Considered
None -- this is pure music theory logic with no viable external library. The project is zero-dependency by design.

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/analysis/
    voiceleading.py          # All VLEAD functions + VoiceLeadingViolation dataclass
tests/analysis/
    test_voiceleading.py     # All VLEAD tests
```

Single file is appropriate: the module contains one dataclass, ~6 private detector functions, and 3 public functions. Total estimated size: 250-350 lines. This matches `analysis/phrases.py` (9 ANAL functions in one file) and `analysis/chords.py`.

### Pattern 1: Voice Pair Iteration
**What:** Extract Note events from each voice, zip by position index, compute intervals at consecutive positions.
**When to use:** VLEAD-01, VLEAD-02, VLEAD-03, VLEAD-04 -- any rule checking relationships between two voices.

```python
from itertools import combinations
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.interval import Interval

def _extract_pitches(phrase: Phrase) -> list[Pitch | None]:
    """Extract pitch at each event position (None for rests)."""
    return [e.pitch if isinstance(e, Note) else None for e in phrase]

def _check_parallel_motion(
    pitches_a: list[Pitch | None],
    pitches_b: list[Pitch | None],
    voice_a: str,
    voice_b: str,
    target_semitones: int,  # 7 for fifths, 0/12 for octaves
    rule_name: str,
) -> list[VoiceLeadingViolation]:
    violations = []
    for i in range(1, min(len(pitches_a), len(pitches_b))):
        prev_a, curr_a = pitches_a[i-1], pitches_a[i]
        prev_b, curr_b = pitches_b[i-1], pitches_b[i]
        if any(p is None for p in (prev_a, curr_a, prev_b, curr_b)):
            continue
        prev_interval = Interval.between(prev_b, prev_a)  # lower to upper
        curr_interval = Interval.between(curr_b, curr_a)
        # Check for parallel motion to target interval
        # ...
    return violations
```

### Pattern 2: Permutation-Based Minimum Movement (VLEAD-05)
**What:** For N voices, try all N! permutations of chord2 pitches, pick the one minimizing total absolute semitone distance.
**When to use:** VLEAD-05 smooth_voice_leading.
**Complexity note:** N! is fine for typical chord sizes (3-6 voices: 6-720 permutations). For N>8, this becomes expensive (40320+), but musical chords rarely exceed 6 notes.

```python
from itertools import permutations

def smooth_voice_leading(
    chord1: tuple[Pitch, ...], chord2: tuple[Pitch, ...]
) -> tuple[Pitch, ...]:
    if len(chord1) != len(chord2):
        raise ValueError(...)
    best_perm = None
    best_cost = float('inf')
    for perm in permutations(chord2):
        cost = sum(abs(p1.midi_number - p2.midi_number) for p1, p2 in zip(chord1, perm))
        if cost < best_cost:
            best_cost = cost
            best_perm = perm
    return best_perm  # type: ignore
```

### Pattern 3: Greedy Beat-by-Beat Generation (VLEAD-08)
**What:** For each beat position, select inner voice pitches that minimize movement from the previous beat while staying within range and forming valid harmony.
**When to use:** VLEAD-08 generate_inner_voices.

```python
def generate_inner_voices(
    soprano: Phrase, bass: Phrase, n: int = 2,
    ranges: list[tuple[Pitch, Pitch]] | None = None,
) -> list[Phrase]:
    # For each beat:
    #   1. Get soprano and bass pitches
    #   2. For each inner voice, find all chromatic pitches in range
    #   3. Pick the one closest to previous beat's pitch (or midpoint for first beat)
    # Return n Phrases ordered highest to lowest
    ...
```

### Anti-Patterns to Avoid
- **Checking violations during generation:** VLEAD-05 and VLEAD-08 must NOT check violations -- caller does that (single responsibility, per CONTEXT.md).
- **Auto-detecting voice order by pitch range:** Voice order follows Score tuple order (per CONTEXT.md). Never reorder.
- **Using float for semitone math:** MIDI numbers are integers; `Pitch.midi_number` returns `int`. Keep all arithmetic integer.
- **Assuming voices have equal length:** Phrases in a Score can differ in length. Use `min(len(voice_a), len(voice_b))` when zipping.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Permutations for voice assignment | Custom recursive permutation | `itertools.permutations` | Correct, fast C implementation |
| Voice pair combinations | Nested loops | `itertools.combinations(voice_names, 2)` | Cleaner, no duplicate pairs |
| Interval computation | Raw semitone math | `Interval.between(p1, p2)` | Already handles quality, direction, compound intervals |
| Pitch comparison | Custom MIDI calculation | `Pitch.midi_number` property | Already correct and tested |

**Key insight:** Almost all building blocks exist in the core. The voice leading module is pure orchestration of existing primitives.

## Common Pitfalls

### Pitfall 1: Confusing Parallel Motion with Similar Motion
**What goes wrong:** Flagging intervals that move to a fifth/octave but from a different interval (similar motion, not parallel).
**Why it happens:** Parallel motion requires BOTH the starting and ending intervals to be the same type (P5->P5 or P8->P8). Similar motion to a perfect interval is a different rule (not in scope for Phase 7).
**How to avoid:** Check that both `prev_interval` and `curr_interval` are the target interval type AND that both voices move in the same direction.
**Warning signs:** False positives on contrary motion arriving at a fifth.

### Pitfall 2: Rest Handling in Voice Pairs
**What goes wrong:** Crashing on `None.midi_number` when one voice has a rest at a position.
**Why it happens:** `Phrase` is `tuple[Event, ...]` where `Event = Note | Rest`. Rests have no pitch.
**How to avoid:** Extract pitches as `Pitch | None`, skip positions where either voice has a rest.
**Warning signs:** TypeError on Rest objects.

### Pitfall 3: Unison vs Octave in Parallel Detection
**What goes wrong:** Missing parallel octaves when voices are in unison (0 semitones) vs actual octave (12 semitones), or missing compound intervals (24 semitones = double octave).
**Why it happens:** P1 (unison) and P8 (octave) are both "perfect" intervals at multiples of 12 semitones.
**How to avoid:** For parallel octave detection, check if `abs(interval.semitones) % 12 == 0`. For parallel fifths, check `abs(interval.semitones) % 12 == 7`.
**Warning signs:** Failing to detect parallel octaves at the unison or compound octave.

### Pitfall 4: Voice Overlap vs Voice Crossing
**What goes wrong:** Confusing the two related but distinct rules.
**Why it happens:** Both involve voices "invading" each other's territory, but at different time points.
**How to avoid:**
- **Crossing (VLEAD-03):** At position `i`, voice A's pitch is lower than voice B's pitch (when A should be higher).
- **Overlap (VLEAD-04):** At position `i`, voice A moves to a pitch below voice B's pitch at position `i-1`.
**Warning signs:** Getting one but not both, or flagging the same violation for both rules.

### Pitfall 5: Direction Check for Parallel Motion
**What goes wrong:** Flagging "parallel fifths" when one voice stays stationary (oblique motion to a fifth is not parallel motion).
**Why it happens:** Only checking the interval type without verifying both voices actually moved.
**How to avoid:** Verify both voices changed pitch AND moved in the same direction. If one voice is stationary, it is oblique motion, not parallel.

### Pitfall 6: Voice Pair Ordering for Crossing/Overlap
**What goes wrong:** Incorrect crossing detection because the "expected" upper/lower relationship is ambiguous.
**Why it happens:** Score tuple order defines voice ordering, but which voice is "upper" vs "lower" depends on convention.
**How to avoid:** For pairs from `combinations(voices, 2)`, the first voice in Score order is considered "upper" (soprano before alto before tenor before bass). Check crossing when the "lower" voice has a higher pitch than the "upper" voice. Document this convention clearly.

## Code Examples

### VoiceLeadingViolation Dataclass
```python
# Following ChordMatch and MotifMatch patterns
from dataclasses import dataclass
from cadenza.core.interval import Interval

@dataclass(frozen=True, slots=True)
class VoiceLeadingViolation:
    """A single voice leading rule violation."""
    rule: str          # 'parallel_fifth', 'parallel_octave', etc.
    voice1: str        # voice name from Score
    voice2: str        # voice name from Score
    position: int      # 0-based event index
    interval: Interval # interval at violation point
    severity: str      # 'error', 'warning', 'suggestion'
```

### Extracting Aligned Pitches from Score
```python
def _aligned_pitches(score: Score) -> dict[str, list[Pitch | None]]:
    """Extract pitch sequences from all voices, None for rests."""
    result = {}
    for name, phrase in score._voices:
        result[name] = [
            e.pitch if isinstance(e, Note) else None
            for e in phrase
        ]
    return result
```

### Default SATB Ranges for VLEAD-08
```python
_DEFAULT_ALTO_RANGE = (Pitch("c", "n", 3), Pitch("g", "n", 5))
_DEFAULT_TENOR_RANGE = (Pitch("c", "n", 2), Pitch("g", "n", 4))

# For n > 2, additional voices can interpolate between tenor low and alto high
```

### Greedy Pitch Selection for Inner Voice Generation
```python
def _closest_pitch_in_range(
    target_midi: int,
    low: Pitch,
    high: Pitch,
) -> Pitch:
    """Find the chromatic pitch in [low, high] closest to target_midi."""
    low_midi = low.midi_number
    high_midi = high.midi_number
    best_midi = max(low_midi, min(high_midi, target_midi))
    # Convert MIDI back to Pitch using from_midi utility
    return from_midi(best_midi)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Rule-based only | Still rule-based for explicit checking | Always | Voice leading rules are deterministic music theory |
| Exhaustive search for voicing | Permutation search (small N) | Standard | N! is fine for 3-6 voice chords |
| Constraint programming | Greedy heuristic | Decision | CONTEXT.md specifies greedy for VLEAD-08 |

Voice leading analysis is a stable, well-defined domain. The rules have not changed since common-practice period music theory was codified. No "state of the art" evolution affects implementation.

## Open Questions

1. **Accessing `_voices` directly vs `voices` property**
   - What we know: `Score._voices` is the internal tuple; `Score.voices` creates a new dict each call
   - What's unclear: Whether to access `_voices` directly for iteration (avoids dict overhead) or use the public API
   - Recommendation: Access `_voices` directly in analysis code (same package, performance matters for large scores). The pattern is already used internally.

2. **`from_midi` utility for VLEAD-08 pitch generation**
   - What we know: `transforms/pitch.py` has `from_midi()` for converting MIDI numbers back to Pitch objects
   - What's unclear: Whether it produces reasonable enharmonic spellings for generated inner voices
   - Recommendation: Use `from_midi` and accept its default spelling. Inner voice generation is best-effort per CONTEXT.md.

3. **Compound interval handling in parallel detection**
   - What we know: Two voices could be two octaves apart (P15), which is still an "octave" relationship
   - What's unclear: Whether parallel P15->P15 should count as "parallel octaves"
   - Recommendation: Use `semitones % 12` comparison to catch all compound equivalents. This is the standard music theory interpretation.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `python3 -m pytest tests/analysis/test_voiceleading.py -x` |
| Full suite command | `python3 -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VLEAD-01 | Detect parallel fifths | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_parallel_fifths -x` | Wave 0 |
| VLEAD-02 | Detect parallel octaves | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_parallel_octaves -x` | Wave 0 |
| VLEAD-03 | Detect voice crossing | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_voice_crossing -x` | Wave 0 |
| VLEAD-04 | Detect voice overlap | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_voice_overlap -x` | Wave 0 |
| VLEAD-05 | Smooth voice leading | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_smooth_voice_leading -x` | Wave 0 |
| VLEAD-06 | Detect large/aug/dim leaps | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_large_leaps -x` | Wave 0 |
| VLEAD-07 | Comprehensive check | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_check_voice_leading -x` | Wave 0 |
| VLEAD-08 | Generate inner voices | unit | `python3 -m pytest tests/analysis/test_voiceleading.py::test_generate_inner_voices -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/analysis/test_voiceleading.py -x`
- **Per wave merge:** `python3 -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/analysis/test_voiceleading.py` -- covers VLEAD-01 through VLEAD-08
- No framework install needed -- pytest already configured in pyproject.toml
- No conftest changes needed -- existing test infrastructure sufficient

## Sources

### Primary (HIGH confidence)
- `src/cadenza/core/score.py` -- Score type definition, _voices tuple structure
- `src/cadenza/core/interval.py` -- Interval.between() API, semitones property
- `src/cadenza/core/pitch.py` -- Pitch type, midi_number, pitch_class, ordering
- `src/cadenza/core/note.py` -- Note/Rest/Event types
- `src/cadenza/core/phrase.py` -- Phrase type alias
- `src/cadenza/analysis/chords.py` -- ChordMatch frozen dataclass pattern, identify_chord
- `src/cadenza/analysis/phrases.py` -- MotifMatch pattern, _extract_notes helper pattern
- `.planning/phases/07-voice-leading/07-CONTEXT.md` -- All locked decisions

### Secondary (MEDIUM confidence)
- Standard voice leading rules from common-practice music theory (well-established domain knowledge)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero external deps, all building blocks exist in codebase
- Architecture: HIGH -- follows established analysis module patterns exactly
- Pitfalls: HIGH -- based on direct inspection of core types (Rest handling, interval semantics)
- Voice leading rules: HIGH -- deterministic music theory, well-codified

**Research date:** 2026-03-20
**Valid until:** 2026-06-20 (stable domain, no external dependency drift)
