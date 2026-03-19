# Phase 5: Harmonic Analysis - Research

**Researched:** 2026-03-19
**Domain:** Music theory -- harmonic analysis, chord identification, key detection, Roman numeral analysis
**Confidence:** HIGH

## Summary

Phase 5 builds a new `cadenza.analysis` subpackage that implements harmonic analysis on top of the existing `cadenza.theory` (chords, scales) and `cadenza.core` (Pitch, Phrase, Note, Rest) infrastructure. The phase is entirely algorithmic -- no external dependencies are needed. All algorithms operate on pitch class sets, Pearson correlation, and brute-force matching against existing registries.

The main technical challenges are: (1) correct chord identification via pitch-class-set matching with inversion detection, (2) accurate Krumhansl-Schmuckler key detection with hardcoded profiles, (3) proper Roman numeral formatting with figuring conventions, and (4) borrowed chord detection via parallel key comparison. All decisions are locked in CONTEXT.md with precise signatures and return types.

**Primary recommendation:** Implement in three files (`analysis/chords.py`, `analysis/keys.py`, `analysis/harmony.py`) using only the existing `cadenza.theory` and `cadenza.core` types. No external libraries needed. Hardcode K-S profiles. Use frozen dataclasses for all result types.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Chord Identification (Area 1):**
- `identify_chord(pitches: tuple[Pitch, ...]) -> ChordMatch` -- brute-force pitch-class match across all roots x all chord types, including inversions. Rank: prefer root position, then simpler types. Single best match only. Raises `ValueError` if no match.
- `ChordMatch(root: Pitch, symbol: str, inversion: int, pitches: tuple[Pitch, ...])` -- frozen dataclass. `symbol` uses registry keys. `inversion` is 0-based.

**Chord Symbol Format (Area 2):**
- `parse_chord_symbol(symbol: str) -> tuple[Pitch, ...]` -- CN pitch root + quality suffix. Aliases: `M`/`Maj`->`maj`, `mi`/`min`/`-`->`m`, degree/`o`->`dim`, `+`->`aug`.
- `chord_symbol(root: Pitch, symbol: str) -> str` -- always includes octave. Round-trip guarantee.

**Key Detection (Area 3):**
- `detect_key(phrase_or_pitches) -> KeyResult` -- Krumhansl-Schmuckler profile matching. Major + natural/harmonic/melodic minor = 48 keys.
- `KeyResult(root: Pitch, mode: str, confidence: float)` -- frozen dataclass. `mode` one of `"major"`, `"natural_minor"`, `"harmonic_minor"`, `"melodic_minor"`. `confidence` is Pearson r normalized to 0.0--1.0.
- `detect_modulations(phrase, window=4) -> list[Modulation]` -- sliding window. `Modulation(position: int, from_key: KeyResult, to_key: KeyResult)`.

**Roman Numeral & Functional Harmony (Area 4):**
- `roman_numeral(chord: ChordMatch, key: KeyResult) -> RomanNumeral` -- standard notation with figured bass inversions.
- `RomanNumeral(numeral: str, function: str, chord: ChordMatch)` -- frozen dataclass. `function` in `{"tonic", "subdominant", "dominant", "predominant", "borrowed", "other"}`.
- `harmonic_rhythm(phrase, key: KeyResult) -> list[HarmonicBeat]` -- `HarmonicBeat(onset: Fraction, duration: Fraction, chord: ChordMatch, numeral: RomanNumeral)`.
- `realize_chord(root, symbol, inversion=0, octave=4) -> tuple[Pitch, ...]` -- thin wrapper over `get_chord`.
- Borrowed chords: check parallel key, prefix `b` or `#` for altered degrees.

**Module Structure:**
- `src/cadenza/analysis/__init__.py`
- `src/cadenza/analysis/chords.py` -- `identify_chord`, `ChordMatch`, `chord_symbol`, `parse_chord_symbol`
- `src/cadenza/analysis/keys.py` -- `detect_key`, `KeyResult`, `detect_modulations`, `Modulation`
- `src/cadenza/analysis/harmony.py` -- `roman_numeral`, `RomanNumeral`, `harmonic_rhythm`, `HarmonicBeat`, `functional_label`, `realize_chord`

### Claude's Discretion

No areas explicitly marked as discretion. All APIs are fully specified.

### Deferred Ideas (OUT OF SCOPE)

None raised during discussion session.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HARM-01 | Identify chord from simultaneous pitches (root, quality, inversion) | Brute-force pitch-class matching against `_CHORD_REGISTRY`; inversion detection via rotation |
| HARM-02 | Roman numeral analysis of a chord within a key context | Scale degree computation via `get_scale` + `scale_degree`; figured bass inversion notation |
| HARM-03 | Key detection from a phrase or score (pitch class frequency analysis) | Krumhansl-Schmuckler profiles hardcoded; Pearson correlation; 48-key search space |
| HARM-04 | Harmonic rhythm analysis (detect chord change points) | Group simultaneous notes by onset; run `identify_chord` on each group |
| HARM-05 | Functional harmony labeling (tonic, dominant, subdominant, etc.) | Degree-to-function mapping table; borrowed chord override |
| HARM-06 | Detect modulation between keys within a phrase | Sliding window `detect_key` with change-detection heuristic |
| HARM-07 | Generate chord symbol string from chord object | CN pitch serializer + registry symbol concatenation |
| HARM-08 | Parse chord symbol string into chord object | Regex parse root + alias-normalized quality; delegate to `get_chord` |
| HARM-09 | Realize a chord as pitches in a given voicing/inversion | Thin wrapper over existing `get_chord(root, symbol, inversion)` |
| HARM-10 | Identify borrowed chords (chords from parallel keys) | Compare chord quality against diatonic expectation; check parallel key via `parallel_key()` |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib only | 3.11+ | All algorithms | Zero-dep core is a project decision; `dataclasses`, `fractions`, `math`, `re` suffice |

### Supporting (existing project dependencies used)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `cadenza.theory.chords` | internal | `get_chord`, `_CHORD_REGISTRY`, `diatonic_chords` | Chord building, registry enumeration, diatonic chord lookup |
| `cadenza.theory.scales` | internal | `get_scale`, `scale_degree`, `parallel_key`, `relative_key` | Key construction, degree computation, borrowed chord detection |
| `cadenza.api.parsing` | internal | `parse_pitch_string` | Parsing CN pitch roots in chord symbol strings |
| `cadenza.core` | internal | `Pitch`, `Phrase`, `Note`, `Rest`, `Duration` | All input/output types |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hardcoded K-S profiles | `music21` library | External dep violates zero-dep core; overkill for profile correlation |
| Brute-force chord ID | Interval-vector lookup | More elegant but harder to rank inversions; brute-force is simpler and CONTEXT.md specifies it |

**Installation:**
```bash
# No new dependencies needed -- pure Python stdlib + existing cadenza internals
```

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/analysis/
    __init__.py            # Re-export public API
    chords.py              # HARM-01, HARM-07, HARM-08, HARM-09: ChordMatch, identify_chord, chord_symbol, parse_chord_symbol, realize_chord
    keys.py                # HARM-03, HARM-06: KeyResult, Modulation, detect_key, detect_modulations
    harmony.py             # HARM-02, HARM-04, HARM-05, HARM-10: RomanNumeral, HarmonicBeat, roman_numeral, harmonic_rhythm
tests/analysis/
    __init__.py
    test_chords.py         # Tests for chord identification, symbol parsing/generation
    test_keys.py           # Tests for key detection, modulation detection
    test_harmony.py        # Tests for Roman numerals, harmonic rhythm, borrowed chords
```

### Pattern 1: Frozen Dataclass Result Types
**What:** All result types (`ChordMatch`, `KeyResult`, `RomanNumeral`, `HarmonicBeat`, `Modulation`) are frozen dataclasses, consistent with the rest of the codebase.
**When to use:** Every public return type in this phase.
**Example:**
```python
from dataclasses import dataclass
from cadenza.core.pitch import Pitch

@dataclass(frozen=True, slots=True)
class ChordMatch:
    root: Pitch
    symbol: str       # Registry key, e.g. "maj7", "m", "7"
    inversion: int    # 0-based: 0 = root position
    pitches: tuple[Pitch, ...]
```

### Pattern 2: Brute-Force Matching with Ranking
**What:** For `identify_chord`, iterate all 12 pitch classes x all chord types x all inversions. Convert input to pitch class set, compare against each candidate's pitch class set. Rank matches by preference.
**When to use:** HARM-01 chord identification.
**Example:**
```python
def identify_chord(pitches: tuple[Pitch, ...]) -> ChordMatch:
    input_pcs = frozenset(p.pitch_class for p in pitches)
    candidates: list[tuple[int, int, Pitch, str, int]] = []

    for root_pc in range(12):
        for symbol, (semitones, _) in _CHORD_REGISTRY.items():
            chord_pcs = frozenset((root_pc + s) % 12 for s in semitones)
            if chord_pcs != input_pcs:
                continue
            # Check all inversions to find which one matches the bass
            for inv in range(len(semitones)):
                # Score: prefer root position (inv=0), prefer fewer notes, prefer triads
                score = (inv, len(semitones), _COMPLEXITY_RANK.get(symbol, 99))
                candidates.append((score[0], score[1], _pc_to_root(root_pc, pitches), symbol, inv))

    if not candidates:
        raise ValueError(f"No chord match for pitch classes {input_pcs}")
    candidates.sort()
    best = candidates[0]
    # ... build ChordMatch from best
```

### Pattern 3: Pearson Correlation for Key Detection
**What:** Build a 12-element pitch class histogram from input, correlate against each of 48 rotated profiles (12 roots x 4 modes). Return the key with highest correlation.
**When to use:** HARM-03 key detection.
**Example:**
```python
import math

def _pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    dx = [xi - mx for xi in x]
    dy = [yi - my for yi in y]
    num = sum(a * b for a, b in zip(dx, dy))
    den = math.sqrt(sum(a * a for a in dx) * sum(b * b for b in dy))
    return num / den if den > 0 else 0.0
```

### Pattern 4: Input Type Flexibility
**What:** `detect_key` accepts `Phrase | tuple[Pitch, ...] | list[Pitch]` as input. Extract pitches from Phrase by filtering Notes (skip Rests).
**When to use:** HARM-03, HARM-06.
**Example:**
```python
from cadenza.core.note import Note, Rest, Event
from cadenza.core.phrase import Phrase

def _extract_pitches(input_data: Phrase | tuple[Pitch, ...] | list[Pitch]) -> list[Pitch]:
    if isinstance(input_data, (list, tuple)) and input_data and isinstance(input_data[0], Pitch):
        return list(input_data)
    # It's a Phrase (tuple of Events)
    return [event.pitch for event in input_data if isinstance(event, Note)]
```

### Anti-Patterns to Avoid
- **Importing private functions across modules:** Don't import `_build_pitch` from `theory/chords.py` or `theory/scales.py`. Use the public `get_chord()` and `get_scale()` APIs. The analysis module should only depend on public interfaces.
- **Float arithmetic for durations:** `HarmonicBeat.onset` and `HarmonicBeat.duration` use `fractions.Fraction`, consistent with the core Duration type.
- **Mutable state:** All result types must be frozen dataclasses. No mutable accumulators exposed in public API.
- **External notation format in function names:** The notation format is CN (Cadenza Notation), never OMN. All references in code, docstrings, and docs must use CN.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chord construction | Custom interval stacking | `get_chord(root, symbol, inversion)` | Already handles all registry types + inversions + spelling |
| Scale lookup | Manual interval computation | `get_scale(root, name)` | 40+ scales with correct spelling |
| Scale degree | Manual pitch-class comparison | `scale_degree(pitch, scale)` | Handles enharmonic edge cases |
| Parallel key | Manual mode toggling | `parallel_key(root, mode)` | Already implemented for major/natural_minor |
| Diatonic chords | Manual third-stacking | `diatonic_chords(root, scale, quality)` | Builds triads/sevenths on all 7 degrees |
| Pitch string parsing | Custom regex | `parse_pitch_string(s)` from `cadenza.api.parsing` | Handles all CN pitch formats |

**Key insight:** Phase 5 is primarily a consumer of Phase 1 and Phase 3 infrastructure. The analysis module should be thin wrappers and algorithms that delegate all pitch/chord/scale construction to existing public APIs.

## Common Pitfalls

### Pitfall 1: Pitch Class Set Matching Ignores Spelling
**What goes wrong:** Two pitches with different spellings (Eb vs D#) have the same pitch class. Chord identification must work on pitch classes, not spelled pitches.
**Why it happens:** The Pitch type is spelling-sensitive (`Eb3 != D#3`).
**How to avoid:** Always reduce to `pitch_class` (0-11) before comparison. Use `frozenset` of pitch classes for set equality.
**Warning signs:** Tests passing for sharp-spelled inputs but failing for flat-spelled inputs of the same chord.

### Pitfall 2: Root Determination for Identified Chords
**What goes wrong:** After matching a pitch class set to a chord type, the root pitch class is known (as an integer 0-11), but we need to return a spelled `Pitch` object. Choosing the wrong spelling (e.g., returning C# when the input used Db) produces musically incorrect results.
**Why it happens:** Pitch class -> Pitch mapping is ambiguous without context.
**How to avoid:** When a chord match is found, find the input pitch whose pitch class matches the root pitch class. Use that pitch's spelling. If the root pitch class is not literally present in the input (inversion), derive spelling from the bass note's context.
**Warning signs:** `identify_chord` returning sharp-spelled roots when input uses flats.

### Pitfall 3: Krumhansl-Schmuckler Minor Profile Applies to Natural Minor Only
**What goes wrong:** The standard K-S minor profile was derived from natural minor contexts. Using it for harmonic and melodic minor detection may produce false positives or low-confidence matches.
**Why it happens:** Published K-S profiles only cover major and (natural) minor. CONTEXT.md requests matching against 48 keys including harmonic and melodic minor.
**How to avoid:** For harmonic and melodic minor, derive synthetic profiles from the scale's pitch class content: weight the scale tones heavily (e.g., 5.0), tonic/dominant extra (e.g., 7.0), non-scale tones low (e.g., 1.0). This is an approximation -- document it clearly and flag confidence as MEDIUM for harmonic/melodic matches.
**Warning signs:** Harmonic minor keys consistently outscoring natural minor for standard tonal music.

### Pitfall 4: Roman Numeral Formatting Edge Cases
**What goes wrong:** Figured bass notation for seventh chord inversions is complex: root position = `7`, first = `6/5`, second = `4/3`, third = `4/2`. Triads: root = none, first = `6`, second = `6/4`. Getting these wrong produces musically illiterate output.
**Why it happens:** The mapping from inversion number to figured bass suffix is non-obvious.
**How to avoid:** Use a lookup table, not computed logic:
```python
_TRIAD_FIGURES = {0: "", 1: "6", 2: "6/4"}
_SEVENTH_FIGURES = {0: "7", 1: "6/5", 2: "4/3", 3: "4/2"}
```
**Warning signs:** First-inversion seventh chords labeled as just `7` instead of `6/5`.

### Pitfall 5: Modulation Detection False Positives
**What goes wrong:** With a window of 4 notes, brief chromatic passages or ornamental notes trigger false modulation detections.
**Why it happens:** Small windows have limited pitch-class data, leading to noisy correlations.
**How to avoid:** Require the new key to "stay changed" for at least `window` consecutive notes (as specified in CONTEXT.md). Also consider requiring a minimum confidence threshold on the new key.
**Warning signs:** Every accidental flagged as a modulation.

### Pitfall 6: Borrowed Chord Detection Scope
**What goes wrong:** `parallel_key()` only supports `major` <-> `natural_minor`. If the detected key is `harmonic_minor` or `melodic_minor`, calling `parallel_key(root, "harmonic_minor")` will raise `ValueError`.
**Why it happens:** `parallel_key` in `scales.py` explicitly only handles `major` and `natural_minor`.
**How to avoid:** For borrowed chord detection, always use the "simplified" parallel: if the key mode contains "minor", compare against `major`; if the key mode is `major`, compare against `natural_minor`. This matches standard harmonic practice (borrowed chords come from the parallel major/minor).
**Warning signs:** `ValueError` when analyzing chords in harmonic minor keys.

### Pitfall 7: Chord Symbol Parsing Ambiguity
**What goes wrong:** The regex for parsing chord symbols like `"fs4m7"` must correctly split into root `fs4` + quality `m7`, not root `fs4m` + quality `7`. Similarly, `"bb4maj7"` must parse as root `bb4` + quality `maj7`.
**Why it happens:** The pitch root includes accidentals (`s`, `b`, `ss`, `bb`) that overlap with quality characters.
**How to avoid:** Use a structured regex that matches the CN pitch pattern first (letter + optional accidental + digits), then captures the remaining string as quality:
```python
_CHORD_SYMBOL_RE = re.compile(r'^([a-g](?:ss|bb|s|b|n)?\d+)(.*)$', re.IGNORECASE)
```
**Warning signs:** `parse_chord_symbol("bb4m7")` failing because `bb` is consumed as both accidental and quality.

## Code Examples

### Krumhansl-Schmuckler Profiles (Verified)

Source: Krumhansl & Kessler (1982), verified via [Humdrum keycor documentation](https://extras.humdrum.org/man/keycor/) and [bmcfee gist](https://gist.github.com/bmcfee/1f66825cef2eb34c839b42dddbad49fd).

```python
# Pitch classes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
```

These are the standard Krumhansl-Kessler profiles. For `natural_minor`, use `MINOR_PROFILE` directly.

### Synthetic Profiles for Harmonic and Melodic Minor

No published K-S profiles exist for harmonic or melodic minor. Construct synthetic profiles from scale membership:

```python
def _make_synthetic_profile(scale_pcs: frozenset[int], tonic_pc: int, dominant_pc: int) -> tuple[float, ...]:
    """Build a synthetic tonal profile from scale pitch classes."""
    profile = []
    for pc in range(12):
        if pc == tonic_pc:
            profile.append(7.0)
        elif pc == dominant_pc:
            profile.append(5.5)
        elif pc in scale_pcs:
            profile.append(3.5)
        else:
            profile.append(1.0)
    return tuple(profile)

# Harmonic minor: 0, 2, 3, 5, 7, 8, 11 (raised 7th)
# Melodic minor: 0, 2, 3, 5, 7, 9, 11 (raised 6th and 7th)
```

### Pearson Correlation

```python
import math

def _pearson_correlation(x: tuple[float, ...], y: tuple[float, ...]) -> float:
    """Compute Pearson correlation coefficient between two equal-length sequences."""
    n = len(x)
    if n == 0:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    dx = tuple(xi - mx for xi in x)
    dy = tuple(yi - my for yi in y)
    numerator = sum(a * b for a, b in zip(dx, dy))
    denom_x = sum(a * a for a in dx)
    denom_y = sum(b * b for b in dy)
    denominator = math.sqrt(denom_x * denom_y)
    if denominator == 0:
        return 0.0
    return numerator / denominator
```

### Pitch Class Histogram

```python
def _pitch_class_histogram(pitches: list[Pitch]) -> tuple[float, ...]:
    """Build a 12-element normalized pitch class frequency histogram."""
    counts = [0] * 12
    for p in pitches:
        counts[p.pitch_class] += 1
    total = sum(counts)
    if total == 0:
        return tuple(0.0 for _ in range(12))
    return tuple(c / total for c in counts)
```

### Figured Bass Lookup Tables

```python
# Triad inversions -> figured bass suffix
_TRIAD_FIGURES: dict[int, str] = {0: "", 1: "6", 2: "6/4"}

# Seventh chord inversions -> figured bass suffix
_SEVENTH_FIGURES: dict[int, str] = {0: "7", 1: "6/5", 2: "4/3", 3: "4/2"}
```

### Degree-to-Function Mapping

```python
# 1-based scale degree -> harmonic function
_DEGREE_FUNCTION: dict[int, str] = {
    1: "tonic",
    2: "predominant",
    3: "tonic",
    4: "subdominant",
    5: "dominant",
    6: "tonic",        # Can also be "subdominant" in some contexts
    7: "dominant",
}
```

### Roman Numeral Degree Labels

```python
_MAJOR_NUMERAL = ("I", "II", "III", "IV", "V", "VI", "VII")
_MINOR_NUMERAL = ("i", "ii", "iii", "iv", "v", "vi", "vii")
```

The case depends on the chord quality: uppercase for major/augmented chords, lowercase for minor/diminished. This is determined by the `ChordMatch.symbol`, not the scale degree.

### Chord Type Complexity Ranking (for brute-force preference)

```python
# Lower = preferred when multiple chord types match the same pitch class set
_COMPLEXITY_RANK: dict[str, int] = {
    # Triads
    "maj": 0, "m": 0, "dim": 0, "aug": 0,
    # Sevenths
    "7": 1, "maj7": 1, "m7": 1, "m7b5": 1, "dim7": 1, "mM7": 1, "aug7": 1,
    # Extended
    "9": 2, "maj9": 2, "m9": 2,
    "11": 3, "maj11": 3,
    "13": 4, "maj13": 4,
    # Suspended/Added
    "sus2": 1, "sus4": 1, "add9": 1, "add11": 1,
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Simple pitch-count key detection | K-S profile correlation | 1990 (Krumhansl) | Standard approach for computational key-finding |
| Manual chord analysis | Pitch class set matching | Long-established | Brute-force is standard for small registries |
| Single major/minor profiles | Multiple profile sets (Aarden, Temperley, Bellman) | 2000s | Alternative profiles may score better on certain repertoire |

**Note on profile choice:** The Krumhansl-Kessler profiles are the most widely cited and tested. Aarden-Essen profiles (derived from statistical analysis of the Essen Folk Song Collection) may perform better on certain repertoire. CONTEXT.md locks in Krumhansl-Schmuckler, so use those.

**Deprecated/outdated:**
- Nothing deprecated in this domain. K-S algorithm has been stable since 1990.

## Open Questions

1. **Harmonic/melodic minor profile accuracy**
   - What we know: No published K-S experimental profiles for harmonic or melodic minor exist. The standard profiles only cover major and natural minor.
   - What's unclear: How well synthetic scale-membership profiles will perform vs. the experimentally-derived major/minor profiles.
   - Recommendation: Use synthetic profiles (scale-tone weighting) for harmonic/melodic minor. Flag these matches with inherently lower confidence in documentation. The approach is reasonable since the characteristic tones (raised 7th in harmonic minor, raised 6th+7th in melodic minor) will drive the correlation correctly.

2. **Confidence normalization for detect_key**
   - What we know: Pearson r ranges from -1.0 to 1.0. CONTEXT.md says "normalized to 0.0-1.0".
   - What's unclear: Whether to use `(r + 1) / 2` (maps full range to 0-1) or `max(0, r)` (clips negative).
   - Recommendation: Use `max(0.0, r)` -- a negative correlation means the pitch distribution is anti-correlated with the profile, which is effectively "no match." This gives more intuitive confidence values where 0.0 = no match and values near 1.0 = strong match.

3. **Handling single-note "chords" in harmonic rhythm**
   - What we know: CONTEXT.md says "single notes analyzed as single-pitch sonorities against the key."
   - What's unclear: A single pitch matches many chord types. Should it return the diatonic chord built on that pitch, or raise an error?
   - Recommendation: For a single pitch, build the diatonic triad on that scale degree. If the pitch is not in the scale, return a best-guess chord with low ranking confidence.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml [tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/analysis/ -x -q` |
| Full suite command | `python -m pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HARM-01 | Identify chord from pitches (major, minor, dim, aug, 7ths, inversions) | unit | `python -m pytest tests/analysis/test_chords.py::test_identify_chord -x` | No -- Wave 0 |
| HARM-02 | Roman numeral in key context (I, ii, V7, bVII etc.) | unit | `python -m pytest tests/analysis/test_harmony.py::test_roman_numeral -x` | No -- Wave 0 |
| HARM-03 | Key detection (C major, A minor, etc.) | unit | `python -m pytest tests/analysis/test_keys.py::test_detect_key -x` | No -- Wave 0 |
| HARM-04 | Harmonic rhythm detection (chord change points) | unit | `python -m pytest tests/analysis/test_harmony.py::test_harmonic_rhythm -x` | No -- Wave 0 |
| HARM-05 | Functional harmony labels (tonic, dominant, etc.) | unit | `python -m pytest tests/analysis/test_harmony.py::test_functional_labels -x` | No -- Wave 0 |
| HARM-06 | Modulation detection (key change points) | unit | `python -m pytest tests/analysis/test_keys.py::test_detect_modulations -x` | No -- Wave 0 |
| HARM-07 | Chord symbol generation (Pitch+symbol -> string) | unit | `python -m pytest tests/analysis/test_chords.py::test_chord_symbol -x` | No -- Wave 0 |
| HARM-08 | Chord symbol parsing (string -> pitches) | unit | `python -m pytest tests/analysis/test_chords.py::test_parse_chord_symbol -x` | No -- Wave 0 |
| HARM-09 | Chord realization (root+symbol -> pitches) | unit | `python -m pytest tests/analysis/test_chords.py::test_realize_chord -x` | No -- Wave 0 |
| HARM-10 | Borrowed chord identification (parallel key check) | unit | `python -m pytest tests/analysis/test_harmony.py::test_borrowed_chords -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/analysis/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/analysis/__init__.py` -- package init
- [ ] `tests/analysis/test_chords.py` -- covers HARM-01, HARM-07, HARM-08, HARM-09
- [ ] `tests/analysis/test_keys.py` -- covers HARM-03, HARM-06
- [ ] `tests/analysis/test_harmony.py` -- covers HARM-02, HARM-04, HARM-05, HARM-10
- [ ] `src/cadenza/analysis/__init__.py` -- package init

## Sources

### Primary (HIGH confidence)
- Krumhansl & Kessler (1982) major/minor profiles -- verified via [Humdrum keycor documentation](https://extras.humdrum.org/man/keycor/)
- [bmcfee K-S gist](https://gist.github.com/bmcfee/1f66825cef2eb34c839b42dddbad49fd) -- exact profile values cross-verified
- [rnhart.net key-finding article](https://rnhart.net/articles/key-finding/) -- algorithm description and profile values
- Existing codebase: `cadenza.theory.chords._CHORD_REGISTRY`, `cadenza.theory.scales._SCALE_REGISTRY`, `cadenza.core.pitch.Pitch` -- direct code inspection

### Secondary (MEDIUM confidence)
- Synthetic harmonic/melodic minor profiles -- no published experimental data; scale-membership weighting is a reasonable approximation used in practice

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no external deps, all algorithms well-understood, existing infrastructure verified by code inspection
- Architecture: HIGH -- module structure and all APIs locked in CONTEXT.md with exact signatures
- Pitfalls: HIGH -- identified from domain knowledge and verified against codebase constraints (e.g., `parallel_key` only supports major/natural_minor)
- K-S profiles (major/minor): HIGH -- cross-verified from multiple authoritative sources
- K-S profiles (harmonic/melodic minor): MEDIUM -- synthetic profiles, no published experimental data

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain -- music theory algorithms do not change)
