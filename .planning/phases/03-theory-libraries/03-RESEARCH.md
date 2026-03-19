# Phase 3: Theory Libraries - Research

**Researched:** 2026-03-19
**Domain:** Music theory scale/chord construction, registry pattern, enharmonic pitch spelling
**Confidence:** HIGH

## Summary

Phase 3 builds two parallel subsystems -- a Scale library and a Chord library -- as a new `cadenza.theory` package. Both are pure Python with zero dependencies, following the frozen-dataclass and module-level-function patterns established in Phases 1-2. The core challenge is not algorithmic complexity but **enharmonic correctness**: every pitch in every scale and chord must be spelled according to music theory conventions (D Dorian returns F-natural, not E-sharp; Bb major returns Bb and Eb, not A# and D#).

The Scale type (`Scale` frozen dataclass) is the critical artifact: it unblocks three Phase 2 stubs (`diatonic_transpose`, `pitch_in_scale`, `nearest_in_scale`). The chord library builds on scales for diatonic chord construction and secondary dominants. Both libraries use a registry pattern (dict mapping name to interval pattern) with user extensibility via `register_scale`/`register_chord`.

**Primary recommendation:** Build scales first (Scale type + registry + `get_scale`), then chords (which depend on scales for diatonic chords and secondary dominants), then complete the Phase 2 stubs, then add the query functions (SCAL-10, SCAL-11, SCAL-12).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Scale API:** `get_scale(root: Pitch, name: str) -> Scale` where Scale is `Scale(root: Pitch, name: str, pitches: tuple[Pitch, ...], intervals: tuple[int, ...])`
- **Scale name vocabulary:** lowercase, case-sensitive. Aliases resolve to canonical names (e.g., "natural minor" / "aeolian" / "minor" all resolve to one canonical)
- **User-extensible registry:** `register_scale(name: str, intervals: list[int]) -> None`
- **SCAL-09 return type:** Scale object containing `pitches: tuple[Pitch, ...]` within a single octave ascending
- **Non-Western scope:** ~15-20 curated scales in 12-TET approximation (Hijaz, Hijaz Kar, Rast, Bayati, Hungarian minor, Romanian, Ukrainian Dorian, Neapolitan major/minor, Persian, Phrygian dominant, Double harmonic, others at discretion)
- **Chord API:** `get_chord(root: Pitch, symbol: str, inversion: int = 0) -> tuple[Pitch, ...]` with lead-sheet symbols
- **'7' = dominant seventh** (universal lead-sheet convention, no ambiguity)
- **Chord symbols:** `'maj'`, `'m'`/`'min'`, `'dim'`, `'aug'`, `'7'`, `'maj7'`, `'m7'`, `'m7b5'`, `'dim7'`, `'mM7'`, `'aug7'`, `'9'`, `'maj9'`, `'m9'`, `'11'`, `'maj11'`, `'13'`, `'maj13'`, `'add9'`, `'add11'`, `'sus2'`, `'sus4'`
- **Secondary dominants:** `secondary_dominant(degree: int, key_root: Pitch, key_name: str) -> tuple[Pitch, ...]`
- **Augmented sixth chords:** `aug6_chord(aug6_type: str, key_root: Pitch, key_name: str) -> tuple[Pitch, ...]` where aug6_type is 'italian', 'french', or 'german'
- **Neapolitan chord:** `neapolitan_chord(key_root: Pitch, key_name: str) -> tuple[Pitch, ...]`
- **Diatonic chords:** `diatonic_chords(scale_root: Pitch, scale_name: str, quality: str = 'triad') -> tuple[tuple[Pitch, ...], ...]`

### Claude's Discretion
- Internal registry data structure (dict of name -> interval pattern)
- Chord registry architecture (similar to scale registry)
- Exact alias mappings within the registry
- Which additional non-Western scales to include to reach ~15-20
- Module layout: `cadenza/theory/scales.py`, `cadenza/theory/chords.py`, `cadenza/theory/__init__.py`

### Deferred Ideas (OUT OF SCOPE)
- Full Arabic maqam system with quarter-tones (requires microtonal pitch model)
- Chord symbol parsing from combined string like "Cmaj7" (separate-args API is sufficient)
- Scale-aware pitch spelling correction (deferred to Phase 5)
- Chord progressions as first-class objects (Phase 3 returns individual chords only)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAL-01 | Common Western scales: major, natural/harmonic/melodic minor | Scale registry with interval patterns; pitch-building algorithm |
| SCAL-02 | All church modes: Ionian through Locrian | Seven mode interval patterns in registry |
| SCAL-03 | Pentatonic scales (major, minor, blues pentatonic) | 5-note interval patterns |
| SCAL-04 | Blues scale (hexatonic) | 6-note interval pattern |
| SCAL-05 | Symmetric scales: whole tone, diminished (octatonic), augmented | Special interval patterns (equal divisions); note spelling conventions |
| SCAL-06 | Bebop scales (dominant, major, minor) | 8-note interval patterns |
| SCAL-07 | Non-Western scales: Arabic maqam modes, Hungarian minor, etc. | Curated ~15-20 scale set as 12-TET approximations |
| SCAL-08 | User-defined scale from interval pattern | `register_scale()` function |
| SCAL-09 | Given root + scale name, return all pitches (single octave) | `get_scale()` returning Scale object |
| SCAL-10 | Determine what scale(s) a set of pitches belongs to | Pitch-class set matching against registry |
| SCAL-11 | Scale degree of a pitch within a scale | Pitch-to-degree lookup within Scale.pitches |
| SCAL-12 | Relative and parallel major/minor | Interval relationships between scale roots |
| CHRD-01 | All triads: major, minor, diminished, augmented | Chord registry with interval stacks |
| CHRD-02 | All seventh chords: maj7, dom7, min7, half-dim7, dim7, min-maj7, aug7 | Extended interval stacks |
| CHRD-03 | Extended chords: 9th, 11th, 13th | Continuing interval stacks above the 7th |
| CHRD-04 | Added-note and suspended chords: add9, add11, sus2, sus4 | Modified triad interval stacks |
| CHRD-05 | All inversions of any chord | Rotation of pitch tuple + octave adjustment |
| CHRD-06 | Diatonic chords of a scale | Build chords on each scale degree using scale pitches |
| CHRD-07 | Secondary dominants (V/ii, V/iii, etc.) | Tonicize target degree, return its V7 |
| CHRD-08 | Neapolitan and augmented sixth chords | Key-context functions with specific interval formulas |
| CHRD-09 | User-defined chord from interval stack | `register_chord()` function |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib only | 3.11+ | Everything | Zero runtime deps constraint; `dataclasses`, `typing` |

### Supporting
No external libraries. This phase uses only:
- `dataclasses` (frozen dataclass for Scale type)
- `typing` (type annotations)
- `copy` (not needed -- frozen dataclasses use `dataclasses.replace()`)

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-built registry | music21 Scale classes | music21 is a massive dependency (~100MB); violates zero-deps constraint |
| Manual interval patterns | mingus or pytheory | Small libraries but still external deps; our patterns are straightforward |

**Installation:**
```bash
# No new dependencies needed
```

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/theory/
    __init__.py          # Public API re-exports
    scales.py            # Scale dataclass, registry, get_scale, query functions
    chords.py            # Chord registry, get_chord, diatonic_chords, special chords
```

```
tests/theory/
    __init__.py
    conftest.py          # Shared fixtures (common Pitch objects, scales)
    test_scales.py       # Scale registry, get_scale, SCAL-01..12
    test_chords.py       # Chord registry, get_chord, CHRD-01..09
```

### Pattern 1: Interval-Pattern Registry

**What:** Scales and chords are defined as tuples of semitone intervals from the root. A registry (module-level dict) maps canonical names to interval patterns. Lookup functions build Pitch objects on demand from root + pattern.

**When to use:** Always -- this is the core data structure.

**Example:**
```python
# Scale registry: name -> tuple of semitone offsets from root
# (0 = root always implicit or explicit)
_SCALE_REGISTRY: dict[str, tuple[int, ...]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor": (0, 2, 3, 5, 7, 9, 11),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    # ...
}

# Alias registry: alias -> canonical name
_SCALE_ALIASES: dict[str, str] = {
    "ionian": "major",
    "aeolian": "natural_minor",
    "minor": "natural_minor",
    # ...
}
```

### Pattern 2: Pitch Building from Root + Semitone Offset

**What:** Given a root Pitch and a semitone offset, compute the correctly-spelled target pitch by stepping through letter names diatonically, then adjusting the accidental.

**When to use:** Every time `get_scale` or `get_chord` constructs pitches.

**This is the hardest part of the phase.** The algorithm must:
1. Know how many letter-name steps correspond to each scale degree
2. Compute the target letter name by stepping from the root
3. Compute the target MIDI number from root MIDI + semitone offset
4. Derive the accidental from the difference between the target letter's natural MIDI and the target MIDI

**Example:**
```python
# For a 7-note scale, the generic intervals are always:
# degree 1->2->3->4->5->6->7 = step through 7 letter names
# For a major scale starting on D4:
#   D4(root) -> E4(+2st) -> F#4(+4st) -> G4(+5st) -> A4(+7st) -> B4(+9st) -> C#5(+11st)
#
# The letter names advance: d->e->f->g->a->b->c
# The accidentals adjust: n->n->s->n->n->n->s

_INDEX_TO_STEP = {0: "c", 1: "d", 2: "e", 3: "f", 4: "g", 5: "a", 6: "b"}

def _build_scale_pitches(root: Pitch, semitone_pattern: tuple[int, ...]) -> tuple[Pitch, ...]:
    """Build correctly-spelled scale pitches from root and semitone offsets."""
    root_step_idx = STEP_INDEX[root.step]
    pitches = []
    for degree_idx, semitones in enumerate(semitone_pattern):
        # Target letter name: advance by degree_idx steps from root
        target_step_idx = (root_step_idx + degree_idx) % 7
        target_step = _INDEX_TO_STEP[target_step_idx]
        # Target MIDI
        target_midi = root.midi_number + semitones
        # Derive octave and accidental
        natural_midi_at_root_octave = (root.octave + 1) * 12 + STEP_SEMITONES[target_step]
        # Adjust octave if needed (letter wrapped past B->C)
        if target_step_idx < root_step_idx:
            natural_midi_at_root_octave += 12  # next octave
        acc_diff = target_midi - natural_midi_at_root_octave
        # Map acc_diff to accidental string
        octave = (target_midi - STEP_SEMITONES[target_step]) // 12 - 1
        # ... (handle edge cases)
    return tuple(pitches)
```

### Pattern 3: Inversion via Pitch Rotation + Octave Bump

**What:** Chord inversions rotate the bottom N pitches up by one octave.

**Example:**
```python
def _apply_inversion(pitches: tuple[Pitch, ...], inversion: int) -> tuple[Pitch, ...]:
    """Rotate chord pitches for inversion, bumping rotated notes up an octave."""
    result = list(pitches)
    for _ in range(inversion):
        p = result.pop(0)
        # Bump up one octave
        result.append(Pitch(step=p.step, accidental=p.accidental, octave=p.octave + 1))
    return tuple(result)
```

### Pattern 4: Diatonic Chord Construction

**What:** Build chords on each degree of a scale by stacking thirds from the scale's own pitches.

**Example:**
```python
def diatonic_chords(scale_root, scale_name, quality='triad'):
    scale = get_scale(scale_root, scale_name)
    pitches = scale.pitches  # 7 pitches, one octave
    # Extend to two octaves for stacking
    extended = pitches + tuple(
        Pitch(p.step, p.accidental, p.octave + 1) for p in pitches
    )
    chords = []
    stack_size = 3 if quality == 'triad' else 4
    for degree in range(7):
        chord = tuple(extended[degree + i * 2] for i in range(stack_size))
        # Every other note = stacking thirds (indices 0, 2, 4, [6])
        chords.append(chord)
    return tuple(chords)
```

### Anti-Patterns to Avoid

- **MIDI-first spelling:** Never build pitches by computing MIDI number and then guessing the spelling. Always determine the letter name first (from scale degree position), then compute the accidental. MIDI-first leads to wrong enharmonics (Gb spelled as F#).
- **Mutable registry without copy:** If the registry dict is exposed directly, callers can corrupt it. Use `_SCALE_REGISTRY.copy()` or keep it private with accessor functions.
- **Hardcoding all pitches:** Do not store pre-computed pitch tuples for every root. Store interval patterns and compute pitches on demand from any root.
- **Forgetting octave wrap:** When building scale pitches, the 7th degree often crosses into the next octave (e.g., C major: C4..B4, but D major: D4..C#5). The algorithm must handle the B->C octave boundary correctly.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scale interval data | Research and derive patterns | Standard music theory reference tables | Error-prone to derive; well-established in every theory textbook |
| Chord interval stacks | Trial-and-error | Standard lead-sheet interval definitions | One wrong semitone ruins the whole chord |
| Enharmonic spelling in scales | Ad-hoc "prefer sharps/flats" | Letter-name-first algorithm (Pattern 2 above) | The correct spelling depends on scale context, not a global preference |

**Key insight:** The interval patterns are trivial data (a few dozen tuples of small integers). The hard part is the pitch-building algorithm that turns `root + semitone_offset + degree_position` into a correctly-spelled Pitch. Get this algorithm right once and every scale/chord inherits correct spelling.

## Common Pitfalls

### Pitfall 1: Wrong Enharmonic Spelling in Scales
**What goes wrong:** D Dorian returns `(D4, E4, E#4, G4, ...)` instead of `(D4, E4, F4, G4, ...)` because the algorithm uses MIDI-to-pitch lookup instead of diatonic letter advancement.
**Why it happens:** Using `from_midi()` with prefer_sharps/prefer_flats instead of computing the correct letter name from the scale degree.
**How to avoid:** Always advance the letter name by one step per scale degree for 7-note scales. The letter sequence for any 7-note scale starting on D is always D-E-F-G-A-B-C. The accidental adjusts.
**Warning signs:** Tests passing for C major (no accidentals) but failing for other roots.

### Pitfall 2: Octave Boundary at B/C
**What goes wrong:** Scale pitches that cross the B-C boundary end up in the wrong octave. E.g., A major: A4-B4-C#5 -- the C# must be octave 5, not 4.
**Why it happens:** The MIDI-to-octave calculation doesn't account for the fact that C is the start of a new octave in SPN (C4 = MIDI 60, B3 = MIDI 59).
**How to avoid:** Compute octave from target_midi directly: `octave = (target_midi - STEP_SEMITONES[target_step]) // 12 - 1`. This naturally handles the B/C boundary.
**Warning signs:** Off-by-one octave errors only in scales whose pitches cross B->C.

### Pitfall 3: Symmetric Scale Spelling Ambiguity
**What goes wrong:** Whole-tone scale (6 notes over 12 semitones) and diminished scale (8 notes) don't fit the standard 7-letter-name system. Spelling becomes ambiguous.
**Why it happens:** A whole-tone scale starting on C would be C-D-E-F#-G#-A# (6 notes, skipping B) -- but starting on Db it might be Db-Eb-F-G-A-B. There's no single "correct" spelling for all roots.
**How to avoid:** For non-7-note scales, use a predefined letter-name sequence for each scale type, or use a "step pattern" that maps each degree to a specific letter offset. For whole-tone: advance by one letter each degree (C-D-E-F#-G#-A# or Db-Eb-F-G-A-B). For diminished (8-note): alternate whole and half steps with appropriate letter advancement.
**Warning signs:** Double-sharps or double-flats appearing in scales where they shouldn't.

### Pitfall 4: Secondary Dominant Spelling
**What goes wrong:** The V7/vi in C major should be E7 (E-G#-B-D), but if you build it by transposing a generic dominant-7th template to the pitch a P5 above the target degree, you might get wrong spelling.
**Why it happens:** The secondary dominant must be built relative to the *temporary tonicization* of the target degree. V7/vi in C means "the dominant 7th chord in the key of A minor."
**How to avoid:** 1) Find the target degree's pitch from the scale. 2) Determine the temporary key (that degree as a tonic). 3) Build a dominant 7th chord on the 5th degree of that temporary key. This ensures correct spelling.
**Warning signs:** Wrong accidentals on secondary dominant chord tones.

### Pitfall 5: Augmented Sixth Chord Spelling
**What goes wrong:** The augmented sixth interval (e.g., Ab to F# in C major) is spelled as a diminished 7th or some other interval because the algorithm doesn't preserve the #4 / b6 spelling.
**Why it happens:** These chords are defined by specific scale-degree spellings (b6 in the bass, #4 on top), not by root-position interval stacking.
**How to avoid:** Build augmented sixth chords from scale degrees, not from interval stacking. Italian: b6-1-#4. French: b6-1-2-#4. German: b6-1-b3-#4. All relative to the key.
**Warning signs:** Enharmonic confusion in the augmented sixth interval.

### Pitfall 6: Melodic Minor Ascending vs Descending
**What goes wrong:** Melodic minor traditionally has different ascending (raised 6th and 7th) and descending (natural minor) forms.
**Why it happens:** The CONTEXT.md specifies single-octave ascending pitches, so this is a design question.
**How to avoid:** Per CONTEXT.md, `get_scale` returns ascending pitches only. Store the ascending melodic minor pattern `(0,2,3,5,7,9,11)`. If descending form is needed later, it can be a separate scale name or a future enhancement.

## Code Examples

### Building a Scale from Root + Interval Pattern
```python
from dataclasses import dataclass
from cadenza.core.pitch import Pitch, STEP_INDEX, STEP_SEMITONES, ACCIDENTAL_SEMITONES

_INDEX_TO_STEP = {v: k for k, v in STEP_INDEX.items()}
_SEMITONES_TO_ACC = {v: k for k, v in ACCIDENTAL_SEMITONES.items()}

@dataclass(frozen=True, slots=True)
class Scale:
    root: Pitch
    name: str
    pitches: tuple[Pitch, ...]
    intervals: tuple[int, ...]

def _build_pitch(root: Pitch, degree_offset: int, semitone_offset: int) -> Pitch:
    """Build a single correctly-spelled pitch from root, letter offset, and semitone offset."""
    target_step_idx = (STEP_INDEX[root.step] + degree_offset) % 7
    target_step = _INDEX_TO_STEP[target_step_idx]
    target_midi = root.midi_number + semitone_offset
    # Compute octave from MIDI and target step
    # MIDI = (octave + 1) * 12 + STEP_SEMITONES[step] + acc
    # We need to find octave such that acc is in range [-2, 2]
    base_pc = STEP_SEMITONES[target_step]
    octave = (target_midi - base_pc) // 12 - 1
    # Verify: natural_midi = (octave + 1) * 12 + base_pc
    natural_midi = (octave + 1) * 12 + base_pc
    acc_semitones = target_midi - natural_midi
    if acc_semitones not in _SEMITONES_TO_ACC:
        raise ValueError(f"Cannot spell pitch: acc offset {acc_semitones}")
    return Pitch(step=target_step, accidental=_SEMITONES_TO_ACC[acc_semitones], octave=octave)
```

### Chord Inversion
```python
def _apply_inversion(pitches: tuple[Pitch, ...], inversion: int) -> tuple[Pitch, ...]:
    if inversion < 0 or inversion >= len(pitches):
        raise ValueError(f"Inversion {inversion} out of range for {len(pitches)}-note chord")
    result = list(pitches)
    for _ in range(inversion):
        p = result.pop(0)
        result.append(Pitch(step=p.step, accidental=p.accidental, octave=p.octave + 1))
    return tuple(result)
```

### Secondary Dominant Construction
```python
def secondary_dominant(degree: int, key_root: Pitch, key_name: str) -> tuple[Pitch, ...]:
    """V7 of the given scale degree."""
    if degree < 2 or degree > 7:
        raise ValueError(f"Degree must be 2-7, got {degree}")
    # Get the target pitch (the scale degree being tonicized)
    key_scale = get_scale(key_root, key_name)
    target_root = key_scale.pitches[degree - 1]
    # Build dominant 7th on the 5th degree above the target
    # i.e., get the pitch a P5 above target_root, then build a dom7 chord
    # Simpler: build dom7 chord whose root is a P5 above target
    fifth_above = _build_pitch(target_root, 4, 7)  # P5 = 4 letter steps, 7 semitones
    return get_chord(fifth_above, '7')
```

### Completing Phase 2 Stubs
```python
# In src/cadenza/transforms/pitch.py, replace the stubs:

def pitch_in_scale(pitch: Pitch, scale: Scale) -> bool:
    """Check if pitch's pitch class matches any scale pitch's pitch class."""
    scale_pcs = {p.pitch_class for p in scale.pitches}
    return pitch.pitch_class in scale_pcs

def nearest_in_scale(pitch: Pitch, scale: Scale) -> Pitch:
    """Find the nearest scale pitch by MIDI distance, preserving octave context."""
    # Build scale pitches in the pitch's octave neighborhood
    candidates = []
    for sp in scale.pitches:
        for oct_offset in (-1, 0, 1):
            candidates.append(Pitch(sp.step, sp.accidental, pitch.octave + oct_offset))
    # Filter valid octave range and find nearest by MIDI distance
    valid = [c for c in candidates if -1 <= c.octave <= 10]
    return min(valid, key=lambda c: abs(c.midi_number - pitch.midi_number))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| music21 Scale/Chord classes (heavy OOP) | Frozen dataclass + pure functions | Project convention | Lighter, immutable, hashable |
| Float-based interval computation | Integer semitone offsets | Always for 12-TET | No floating point issues |
| Mutable scale objects | Frozen `Scale` dataclass | Project convention | Safe to use as dict keys, in sets |

**Not applicable:**
- No external libraries are used, so version currency is not a concern
- All music theory knowledge is stable (scale/chord definitions don't change)

## Complete Scale Registry Reference

The following interval patterns should be included. Intervals are semitone offsets from root.

### Western Scales (SCAL-01 through SCAL-06)
```
major:              (0, 2, 4, 5, 7, 9, 11)
natural_minor:      (0, 2, 3, 5, 7, 8, 10)
harmonic_minor:     (0, 2, 3, 5, 7, 8, 11)
melodic_minor:      (0, 2, 3, 5, 7, 9, 11)   # ascending form

# Church modes (SCAL-02)
ionian:             alias -> major
dorian:             (0, 2, 3, 5, 7, 9, 10)
phrygian:           (0, 1, 3, 5, 7, 8, 10)
lydian:             (0, 2, 4, 6, 7, 9, 11)
mixolydian:         (0, 2, 4, 5, 7, 9, 10)
aeolian:            alias -> natural_minor
locrian:            (0, 1, 3, 5, 6, 8, 10)

# Pentatonic (SCAL-03)
major_pentatonic:   (0, 2, 4, 7, 9)
minor_pentatonic:   (0, 3, 5, 7, 10)

# Blues (SCAL-04)
blues:              (0, 3, 5, 6, 7, 10)

# Symmetric (SCAL-05)
whole_tone:         (0, 2, 4, 6, 8, 10)
diminished:         (0, 2, 3, 5, 6, 8, 9, 11)      # whole-half diminished
diminished_whole_half: alias -> diminished
diminished_half_whole: (0, 1, 3, 4, 6, 7, 9, 10)   # half-whole diminished
augmented:          (0, 3, 4, 7, 8, 11)

# Bebop (SCAL-06)
bebop_dominant:     (0, 2, 4, 5, 7, 9, 10, 11)
bebop_major:        (0, 2, 4, 5, 7, 8, 9, 11)
bebop_minor:        (0, 2, 3, 5, 7, 8, 9, 10)       # aka bebop dorian
```

### Non-Western Scales (SCAL-07, ~15-20 total)
```
# Arabic/Maqam-approximated
hijaz:              (0, 1, 4, 5, 7, 8, 10)    # Hijaz tetrachord + upper
hijaz_kar:          (0, 1, 4, 5, 7, 8, 11)    # Hijaz + harmonic upper
rast:               (0, 2, 4, 5, 7, 9, 10)    # 12-TET approx (true Rast uses 3/4 tones)
bayati:             (0, 1, 3, 5, 7, 8, 10)    # 12-TET approx

# Eastern European
hungarian_minor:    (0, 2, 3, 6, 7, 8, 11)
romanian:           (0, 2, 3, 6, 7, 9, 10)    # Romanian minor
ukrainian_dorian:   (0, 2, 3, 6, 7, 9, 10)    # Same as Romanian minor; alias

# Neapolitan
neapolitan_major:   (0, 1, 3, 5, 7, 9, 11)
neapolitan_minor:   (0, 1, 3, 5, 7, 8, 11)

# Other
persian:            (0, 1, 4, 5, 6, 8, 11)
phrygian_dominant:  (0, 1, 4, 5, 7, 8, 10)
double_harmonic:    (0, 1, 4, 5, 7, 8, 11)    # aka Byzantine
enigmatic:          (0, 1, 4, 6, 8, 10, 11)
hirajoshi:          (0, 2, 3, 7, 8)            # Japanese pentatonic
in_sen:             (0, 1, 5, 7, 10)           # Japanese In scale
iwato:              (0, 1, 5, 6, 10)           # Japanese
yo:                 (0, 2, 5, 7, 9)            # Japanese Yo scale
```

### Chord Interval Stacks Reference
```
# Triads (CHRD-01) - semitone intervals from root
maj:    (0, 4, 7)
m:      (0, 3, 7)
dim:    (0, 3, 6)
aug:    (0, 4, 8)

# Seventh chords (CHRD-02)
7:      (0, 4, 7, 10)    # dominant 7th
maj7:   (0, 4, 7, 11)
m7:     (0, 3, 7, 10)
m7b5:   (0, 3, 6, 10)    # half-diminished
dim7:   (0, 3, 6, 9)
mM7:    (0, 3, 7, 11)    # minor-major 7th
aug7:   (0, 4, 8, 10)    # augmented dominant

# Extended (CHRD-03)
9:      (0, 4, 7, 10, 14)
maj9:   (0, 4, 7, 11, 14)
m9:     (0, 3, 7, 10, 14)
11:     (0, 4, 7, 10, 14, 17)
maj11:  (0, 4, 7, 11, 14, 17)
13:     (0, 4, 7, 10, 14, 17, 21)    # often voiced without 11th
maj13:  (0, 4, 7, 11, 14, 17, 21)

# Added/Suspended (CHRD-04)
add9:   (0, 4, 7, 14)
add11:  (0, 4, 7, 17)
sus2:   (0, 2, 7)
sus4:   (0, 5, 7)
```

### Chord Letter-Name Steps Reference
For correct spelling, each chord type needs a letter-name step pattern (degree offsets from root):
```
# Triads: root, 3rd, 5th -> letter steps: 0, 2, 4
# Sevenths: root, 3rd, 5th, 7th -> letter steps: 0, 2, 4, 6
# 9ths: 0, 2, 4, 6, 8 (= 1 in next octave)
# 11ths: 0, 2, 4, 6, 8, 10 (= 3 in next octave)
# 13ths: 0, 2, 4, 6, 8, 10, 12 (= 5 in next octave)
# sus2: root, 2nd, 5th -> letter steps: 0, 1, 4
# sus4: root, 4th, 5th -> letter steps: 0, 3, 4
# add9: root, 3rd, 5th, 9th -> letter steps: 0, 2, 4, 8
# add11: root, 3rd, 5th, 11th -> letter steps: 0, 2, 4, 10
```

## Special Considerations

### Non-7-Note Scale Spelling

For scales that are not 7 notes (pentatonic = 5, blues = 6, whole-tone = 6, diminished = 8, augmented = 6, bebop = 8), the "advance one letter per degree" rule breaks down. Two approaches:

**Approach A -- Predefined letter-step sequences per scale type:**
Each non-7-note scale gets a hardcoded letter-step pattern. E.g., major pentatonic from C: C-D-E-G-A (steps: 0,1,2,4,5). Blues from C: C-Eb-F-Gb-G-Bb (steps: 0,2,3,3,4,6 -- note Gb and G share the letter-name area).

**Approach B -- Derive from parent scale:**
Major pentatonic is degrees 1-2-3-5-6 of the major scale. Build the full major scale, pick those degrees. This ensures correct spelling automatically.

**Recommendation:** Use Approach B where possible (pentatonic, blues, bebop are subsets/supersets of standard scales). Use Approach A for truly novel patterns (augmented, diminished) where no clear parent exists.

For diminished and augmented scales, define explicit degree-step mappings:
```python
# Whole-half diminished (8 notes): uses all 7 letters + one repeated with different accidental
# C diminished (W-H): C-D-Eb-F-Gb-Ab-A-B -> steps: c,d,e,f,g,a,a,b
# This requires a per-scale "degree_steps" override

# Whole tone (6 notes): C-D-E-F#-G#-A# -> steps: c,d,e,f,g,a
# Or Db-Eb-F-G-A-B -> steps: d,e,f,g,a,b
```

### SCAL-10: Scale Detection Algorithm

Given a set of pitches, find which scales contain all those pitch classes:
1. Extract pitch classes from input set
2. For each scale in registry, for each possible root (0-11), compute the pitch class set
3. Return all (root, scale_name) pairs where input pitch classes are a subset of the scale's pitch classes

This is O(registry_size * 12 * input_size) which is perfectly fast for ~40 scales.

### SCAL-12: Relative and Parallel Major/Minor

- **Parallel:** Same root, different quality. C major -> C minor (parallel minor). A minor -> A major (parallel major).
- **Relative:** Different root, same key signature. C major -> A minor (relative minor, root = 6th degree). A minor -> C major (relative major, root = b3 above or 3 semitones up).

Implementation: For any scale, compute the relative minor/major by finding the appropriate degree and building a new scale on that root.

## Open Questions

1. **Diminished/augmented scale spelling for all 12 roots**
   - What we know: These scales don't map cleanly to 7 letter names. Some roots will require double-sharps or double-flats.
   - What's unclear: Whether to allow double-sharps/double-flats or respell certain degrees for readability.
   - Recommendation: Allow double-sharps/double-flats when they arise naturally from the algorithm. The `Pitch` type supports `ss` and `bb`. Document specific cases in tests.

2. **Melodic minor ascending only vs both forms**
   - What we know: CONTEXT.md says single-octave ascending. Standard theory uses different ascending and descending forms.
   - What's unclear: Whether a separate "melodic_minor_descending" entry is needed.
   - Recommendation: Store ascending form as "melodic_minor". If needed later, add "melodic_minor_desc" as alias for natural_minor. This is consistent with jazz convention where melodic minor is always the ascending form.

3. **Bebop scale spelling (8 notes in 7 letter names)**
   - What we know: Bebop scales add a chromatic passing tone, creating 8 notes that must use 7 letter names (one repeated).
   - What's unclear: Which letter name gets repeated.
   - Recommendation: Derive from parent scale + chromatic passing tone. E.g., bebop dominant = mixolydian + natural 7th: C-D-E-F-G-A-Bb-B. The B letter appears twice (Bb and B-natural).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 8.0 + hypothesis >= 6.100 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/theory/ -x -q` |
| Full suite command | `python -m pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAL-01 | Major, natural/harmonic/melodic minor scales | unit | `python -m pytest tests/theory/test_scales.py::test_western_scales -x` | No -- Wave 0 |
| SCAL-02 | Church modes (7 modes) | unit | `python -m pytest tests/theory/test_scales.py::test_church_modes -x` | No -- Wave 0 |
| SCAL-03 | Pentatonic scales | unit | `python -m pytest tests/theory/test_scales.py::test_pentatonic -x` | No -- Wave 0 |
| SCAL-04 | Blues scale | unit | `python -m pytest tests/theory/test_scales.py::test_blues -x` | No -- Wave 0 |
| SCAL-05 | Symmetric scales | unit | `python -m pytest tests/theory/test_scales.py::test_symmetric -x` | No -- Wave 0 |
| SCAL-06 | Bebop scales | unit | `python -m pytest tests/theory/test_scales.py::test_bebop -x` | No -- Wave 0 |
| SCAL-07 | Non-Western scales | unit | `python -m pytest tests/theory/test_scales.py::test_non_western -x` | No -- Wave 0 |
| SCAL-08 | User-defined scale | unit | `python -m pytest tests/theory/test_scales.py::test_register_scale -x` | No -- Wave 0 |
| SCAL-09 | get_scale returns correct pitches | unit | `python -m pytest tests/theory/test_scales.py::test_get_scale -x` | No -- Wave 0 |
| SCAL-10 | Scale detection from pitches | unit | `python -m pytest tests/theory/test_scales.py::test_scales_for_pitches -x` | No -- Wave 0 |
| SCAL-11 | Scale degree of a pitch | unit | `python -m pytest tests/theory/test_scales.py::test_scale_degree -x` | No -- Wave 0 |
| SCAL-12 | Relative/parallel major/minor | unit | `python -m pytest tests/theory/test_scales.py::test_relative_parallel -x` | No -- Wave 0 |
| CHRD-01 | All triads | unit | `python -m pytest tests/theory/test_chords.py::test_triads -x` | No -- Wave 0 |
| CHRD-02 | All seventh chords | unit | `python -m pytest tests/theory/test_chords.py::test_sevenths -x` | No -- Wave 0 |
| CHRD-03 | Extended chords (9th, 11th, 13th) | unit | `python -m pytest tests/theory/test_chords.py::test_extended -x` | No -- Wave 0 |
| CHRD-04 | Added-note and suspended chords | unit | `python -m pytest tests/theory/test_chords.py::test_added_suspended -x` | No -- Wave 0 |
| CHRD-05 | Chord inversions | unit | `python -m pytest tests/theory/test_chords.py::test_inversions -x` | No -- Wave 0 |
| CHRD-06 | Diatonic chords | unit | `python -m pytest tests/theory/test_chords.py::test_diatonic_chords -x` | No -- Wave 0 |
| CHRD-07 | Secondary dominants | unit | `python -m pytest tests/theory/test_chords.py::test_secondary_dominants -x` | No -- Wave 0 |
| CHRD-08 | Neapolitan and augmented sixths | unit | `python -m pytest tests/theory/test_chords.py::test_special_chords -x` | No -- Wave 0 |
| CHRD-09 | User-defined chord | unit | `python -m pytest tests/theory/test_chords.py::test_register_chord -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/theory/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/theory/__init__.py` -- package init
- [ ] `tests/theory/conftest.py` -- shared Pitch fixtures (C4, D4, Eb4, F#4, etc.)
- [ ] `tests/theory/test_scales.py` -- all SCAL-01..12 tests
- [ ] `tests/theory/test_chords.py` -- all CHRD-01..09 tests
- [ ] `src/cadenza/theory/__init__.py` -- package init
- [ ] `src/cadenza/theory/scales.py` -- Scale type + registry + functions
- [ ] `src/cadenza/theory/chords.py` -- Chord registry + functions

## Sources

### Primary (HIGH confidence)
- Project source code: `src/cadenza/core/pitch.py`, `src/cadenza/core/interval.py` -- actual Pitch/Interval types
- Project source code: `src/cadenza/transforms/pitch.py` -- Phase 2 stubs, `_transpose_pitch` algorithm
- CONTEXT.md decisions -- all API signatures locked by user

### Secondary (MEDIUM confidence)
- Standard music theory: scale interval patterns, chord interval stacks, mode definitions (Aldwell & Schachter, standard jazz theory)
- Lead-sheet chord symbol conventions (universal in jazz/pop notation)

### Tertiary (LOW confidence)
- Non-Western scale 12-TET approximations -- these are inherently approximate; different sources may give slightly different semitone values for maqam-based scales

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero deps, pure Python, no external libraries
- Architecture: HIGH -- registry pattern is straightforward; Pitch building algorithm is well-understood from Phase 2 `_transpose_pitch`
- Pitfalls: HIGH -- enharmonic spelling issues are the primary risk, well-documented above
- Scale/chord data: HIGH for Western scales, MEDIUM for non-Western (12-TET approximations vary by source)

**Research date:** 2026-03-19
**Valid until:** No expiry (music theory is stable; project conventions are internal)
