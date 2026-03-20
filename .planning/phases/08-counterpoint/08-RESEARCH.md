# Phase 8: Counterpoint - Research

**Researched:** 2026-03-20
**Domain:** Algorithmic counterpoint generation and validation (pure music theory, no external deps)
**Confidence:** HIGH

## Summary

Phase 8 implements species counterpoint generation and validation as pure Python functions operating on existing `Phrase` and `Score` types. This is a self-contained algorithmic domain: no external libraries are needed. The challenge is entirely in encoding music theory rules correctly and choosing a generation algorithm that reliably produces valid counterpoint.

The core problem decomposes into: (1) a rule engine that classifies intervals as consonant/dissonant per species, (2) a backtracking generator that builds note sequences satisfying all constraints, and (3) a validation function that checks an existing counterpoint line against those same rules. The existing `Interval.between()`, `Pitch.midi_number`, and `from_midi()` utilities provide all the building blocks.

**Primary recommendation:** Use depth-first backtracking with constraint propagation for generation. Structure the module as a `src/cadenza/counterpoint/` subpackage with separate files for rules, generation, and validation.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Return type: All generation functions return a plain `Phrase` -- single responsibility, caller runs `check_counterpoint()` separately
- One function per species: `generate_first_species` through `generate_fifth_species`, plus `generate_free_counterpoint`
- `above: bool = True` parameter on all generation functions
- `range: tuple[Pitch, Pitch] | None = None` parameter on all generation functions
- Generation is always strict -- no `rules` param on generation functions
- New dataclass `CounterpointViolation` (frozen=True, slots=True) with fields: rule, species, position, interval, severity
- `check_counterpoint(cf, counterpoint, species, rules=None)` returns `list[CounterpointViolation]` sorted by position
- Default severity assignments: errors (parallel_fifth, parallel_octave, direct_octave, dissonance_on_beat, voice_crossing, unresolved_suspension), warnings (large_leap, repeated_note, voice_overlap), suggestions (augmented_leap, climax_placement)
- `rules: dict[str, str] | None = None` on `check_counterpoint` only -- overrides individual rule severities
- Multi-voice: `generate_multi_voice_counterpoint(cf, n=2, species=1, above=None) -> Score`
- Score naming: CF as `('cf', cf_phrase)`, generated voices as `('cp1', phrase1)` etc., ordered highest to lowest
- ValueError for n > 4 or empty CF only

### Claude's Discretion
- Algorithm choice for generation (backtracking, greedy, weighted random)
- How `above` param works when `n=2` (default: both above CF)
- Additional rule names beyond listed defaults
- Module location: `src/cadenza/counterpoint/` package vs `src/cadenza/analysis/counterpoint.py`

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CPTR-01 | Generate first-species counterpoint (note-against-note) | Consonance rules + backtracking generator; see Architecture Patterns |
| CPTR-02 | Generate second-species counterpoint (two notes against one) | Beat/offbeat consonance/dissonance rules; passing tone handling |
| CPTR-03 | Generate third-species counterpoint (four notes against one) | Expanded passing/neighbor tone rules; cambiata patterns |
| CPTR-04 | Generate fourth-species counterpoint (syncopated, suspensions) | Suspension preparation-dissonance-resolution chain |
| CPTR-05 | Generate fifth-species counterpoint (florid, combining all species) | Mixed-species rhythm selection + all rules combined |
| CPTR-06 | Validate counterpoint line against species rules | Rule engine with configurable severity; `check_counterpoint` function |
| CPTR-07 | Support counterpoint above and below cantus firmus | `above: bool` param; interval direction logic inversion |
| CPTR-08 | Generate two-voice free counterpoint (tonal, not strict species) | Relaxed consonance rules; no strict rhythmic ratios |
| CPTR-09 | Generate 2-4 voice counterpoint from melodic line | Iterative voice generation; inter-voice constraint checking |
| CPTR-10 | Configurable rule severity | `rules` dict override on `check_counterpoint` |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| (none -- pure Python) | 3.11+ | All generation and validation logic | Zero-dep core is a project invariant; counterpoint is algorithmic, not I/O |

### Supporting (existing project dependencies used)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `cadenza.core.pitch.Pitch` | internal | Pitch representation with midi_number | Every interval computation |
| `cadenza.core.interval.Interval` | internal | `Interval.between()` for consonance checks | Beat-by-beat interval classification |
| `cadenza.core.note.Note` | internal | Building output Phrase events | Generation output construction |
| `cadenza.core.duration.Duration` | internal | Duration values for species rhythms | Assigning durations per species rules |
| `cadenza.core.score.Score` | internal | Multi-voice return type | CPTR-09 multi-voice generation |
| `cadenza.transforms.pitch.from_midi` | internal | MIDI number to Pitch conversion | Generation candidate pitch construction |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Backtracking search | Greedy/random | Greedy may fail to find valid solutions; backtracking guarantees completeness |
| Backtracking search | Constraint solver (python-constraint) | External dep violates zero-dep policy; overkill for 8-15 note sequences |
| Custom rule engine | music21 counterpoint module | External dep; music21 is 50MB+ and does far more than needed |

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/counterpoint/
    __init__.py          # Re-exports: CounterpointViolation, check_counterpoint, all generate_* functions
    rules.py             # Consonance tables, rule definitions, interval classification helpers
    validation.py        # check_counterpoint() and species-specific rule checkers
    generation.py        # All generate_*_species() functions + backtracking engine
    _engine.py           # Internal backtracking search engine (shared by all species)
```

**Rationale for subpackage over single file:** Seven generation functions + validation + rule engine + shared helpers will be 600-1000 lines. A subpackage keeps files focused (200-300 lines each), matching the project's `cadenza.analysis`, `cadenza.theory`, `cadenza.transforms` patterns.

### Pattern 1: Interval Classification (Consonance/Dissonance)

**What:** Classify intervals between two pitches as perfect consonance, imperfect consonance, or dissonance.
**When to use:** Every beat of every species.

```python
# Consonance classification by semitones mod 12
PERFECT_CONSONANCES = {0, 7}        # unison, P5 (P8 handled via mod 12 = 0)
IMPERFECT_CONSONANCES = {3, 4, 8, 9}  # m3, M3, m6, M6
DISSONANCES = {1, 2, 5, 6, 10, 11}   # m2, M2, P4, tritone, m7, M7

# Note: P4 (5 semitones) is dissonant in two-voice counterpoint (against bass)
# but consonant in three+ voice contexts. For species counterpoint, treat as dissonant.

def classify_interval(semitones_mod12: int) -> str:
    """Return 'perfect', 'imperfect', or 'dissonant'."""
    if semitones_mod12 in PERFECT_CONSONANCES:
        return "perfect"
    if semitones_mod12 in IMPERFECT_CONSONANCES:
        return "imperfect"
    return "dissonant"
```

### Pattern 2: Backtracking Generator

**What:** Depth-first search with constraint pruning to build a valid counterpoint line note by note.
**When to use:** All species generation functions delegate to this engine with species-specific constraints.

```python
def _backtrack(
    cf_pitches: list[Pitch],
    candidates_fn: Callable[[int, list[Pitch], Pitch], list[Pitch]],
    validate_fn: Callable[[int, list[Pitch], Pitch, Pitch], bool],
    position: int,
    partial: list[Pitch],
) -> list[Pitch] | None:
    """Recursive backtracking search.

    candidates_fn(position, partial, cf_pitch) -> list of candidate pitches
    validate_fn(position, partial, candidate, cf_pitch) -> bool
    """
    if position == len(cf_pitches):
        return partial  # complete solution

    cf_pitch = cf_pitches[position]
    candidates = candidates_fn(position, partial, cf_pitch)
    random.shuffle(candidates)  # variety in output

    for candidate in candidates:
        if validate_fn(position, partial, candidate, cf_pitch):
            partial.append(candidate)
            result = _backtrack(cf_pitches, candidates_fn, validate_fn, position + 1, partial)
            if result is not None:
                return result
            partial.pop()

    return None  # dead end, backtrack
```

**Key design points:**
- `candidates_fn` generates legal pitches per species (within range, appropriate duration)
- `validate_fn` checks all rules: consonance, no parallel 5ths/8ths, stepwise motion preference, etc.
- `random.shuffle` provides variety -- multiple calls yield different valid counterpoints
- For species II-V, candidates include duration information (not just pitch)

### Pattern 3: Species-Specific Rule Sets

**What:** Each species has distinct rhythmic and melodic constraints.
**When to use:** Passed as parameters to the backtracking engine.

| Species | CF:CP Ratio | Beat Consonance | Off-Beat Rules | Special |
|---------|-------------|-----------------|----------------|---------|
| 1st | 1:1 | All consonant | N/A | Begin/end on P1/P5/P8; penultimate = step to final |
| 2nd | 1:2 | Downbeat consonant | Passing tones, neighbor tones OK | Must begin with rest or consonance on first half |
| 3rd | 1:4 | Downbeat consonant | More passing/neighbor freedom | Cambiata pattern allowed |
| 4th | 1:1 syncopated | Tied-over note creates dissonance | Suspension must resolve stepwise down | Preparation (consonant) -> suspension (dissonant) -> resolution (consonant) |
| 5th | Mixed | Follows species of current beat | Combines all species rules | Rhythm selection is part of generation |

### Pattern 4: Validation as Rule Composition

**What:** `check_counterpoint` runs a list of rule-checker functions, each returning violations.
**When to use:** CPTR-06 and CPTR-10.

```python
def check_counterpoint(
    cf: Phrase,
    counterpoint: Phrase,
    species: int,
    rules: dict[str, str] | None = None,
) -> list[CounterpointViolation]:
    # Build effective severity map
    severity_map = dict(DEFAULT_SEVERITIES)
    if rules:
        severity_map.update(rules)

    violations: list[CounterpointViolation] = []

    # Run each rule checker
    for checker in _get_checkers(species):
        raw = checker(cf, counterpoint, species)
        for v in raw:
            # Apply configured severity
            effective_severity = severity_map.get(v.rule, v.severity)
            violations.append(CounterpointViolation(
                rule=v.rule, species=v.species,
                position=v.position, interval=v.interval,
                severity=effective_severity,
            ))

    violations.sort(key=lambda v: v.position)
    return violations
```

### Anti-Patterns to Avoid
- **Monolithic species functions:** Do NOT duplicate the entire backtracking algorithm in each species function. Extract the shared engine; species differ only in candidate generation and constraint functions.
- **Float arithmetic for durations:** ALWAYS use `Fraction` via `Duration.from_cn()`. Never compute `1/3` as float.
- **Hardcoded pitch ranges:** Always respect the `range` parameter; default range should be a 10th above/below the CF range, not a fixed constant.
- **Ignoring the penultimate note:** The leading tone -> tonic cadence at the end is mandatory in all species. Failing to enforce this is the most common counterpoint generator bug.
- **Treating P4 as consonant:** In two-voice species counterpoint, P4 (5 semitones) above the bass is dissonant. This is a frequent error.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interval computation | Custom semitone math | `Interval.between(p1, p2)` | Already handles compound intervals, direction, quality |
| Parallel 5th/8th detection | New parallel checker | Reuse logic pattern from `voiceleading._check_parallels` | Same algorithm, just adapted for two Phrases instead of Score |
| MIDI-to-pitch conversion | Letter/octave math | `from_midi(midi_number)` | Handles all enharmonic spelling correctly |
| Voice crossing detection | Custom crossing check | Pattern from `voiceleading._check_crossing` | Same logic, adapted for Phrase pair |

**Key insight:** The voice leading module (Phase 7) already has the core detection algorithms for parallel motion, crossing, and overlap. The counterpoint module should reuse the same *logic patterns* but operate on `Phrase` pairs rather than `Score` objects. Do NOT import private functions from voiceleading -- instead, implement focused counterpoint-specific versions that are simpler (always exactly 2 voices, known CF vs CP roles).

## Common Pitfalls

### Pitfall 1: P4 Treated as Consonant
**What goes wrong:** Generator produces fourths on strong beats, which are dissonant in two-voice counterpoint.
**Why it happens:** P4 is a "perfect consonance" in general harmony but dissonant above the bass in counterpoint.
**How to avoid:** Consonance classification must treat semitones-mod-12 == 5 as dissonant for all species counterpoint.
**Warning signs:** Generated counterpoint sounds "hollow" with too many fourths.

### Pitfall 2: Missing Cadential Pattern
**What goes wrong:** Counterpoint ends without proper approach to the final note.
**Why it happens:** The penultimate note rule (step to final, leading tone if ascending) is easy to omit from the constraint set.
**How to avoid:** Enforce as a hard constraint in the backtracking engine: position == len(cf) - 2 must produce a note a step away from the final.
**Warning signs:** Counterpoint leaps to the final note or ends on a non-tonic interval.

### Pitfall 3: Backtracking Without Heuristic Ordering
**What goes wrong:** Generator is extremely slow (seconds for 8-note CF) or fails to find solutions.
**Why it happens:** Naive candidate enumeration explores too many dead ends.
**How to avoid:** Order candidates by: (1) stepwise motion from previous note, (2) imperfect consonances preferred over perfect, (3) contrary motion to CF preferred. This prunes the search space dramatically.
**Warning signs:** Generation takes > 100ms for a typical 8-12 note CF.

### Pitfall 4: Suspension Resolution Direction in 4th Species
**What goes wrong:** Suspensions resolve upward instead of downward, violating strict counterpoint rules.
**Why it happens:** The resolution step is implemented as "move by step" without enforcing direction.
**How to avoid:** 4th species: suspension dissonance MUST resolve downward by step (except in specific upper-voice contexts where upward resolution to a 6th is acceptable in later practice).
**Warning signs:** check_counterpoint flags `unresolved_suspension` on generated 4th species.

### Pitfall 5: Off-by-One in Position Indexing
**What goes wrong:** Violations report wrong position; second-species "beat 1" vs "beat 2" confusion.
**Why it happens:** Species II has 2 CP notes per CF note, species III has 4. Position in CF vs position in CP line must be mapped correctly.
**How to avoid:** `CounterpointViolation.position` is defined as 0-based CF note index. For species II-V, map CP note indices back to CF positions via integer division.
**Warning signs:** Violation positions exceed CF length.

### Pitfall 6: Voice Direction Logic for `above=False`
**What goes wrong:** When generating below the CF, parallel detection and consonance checks break.
**Why it happens:** Interval direction matters -- the CF is now the upper voice. `Interval.between(lower, upper)` must be called with the right argument order.
**How to avoid:** Normalize: always compute intervals as `Interval.between(lower_pitch, upper_pitch)` regardless of which is CF and which is CP. Determine upper/lower from MIDI numbers, not from `above` parameter.
**Warning signs:** Counterpoint below CF has different violation patterns than above.

## Code Examples

### Creating a CounterpointViolation
```python
from cadenza.core.interval import Interval

violation = CounterpointViolation(
    rule="parallel_fifth",
    species=1,
    position=3,
    interval=Interval.between(bass_pitch, soprano_pitch),
    severity="error",
)
```

### Building Output Phrases with Correct Durations
```python
from fractions import Fraction
from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.transforms.pitch import from_midi

# Species I: same duration as CF notes
def _build_first_species_phrase(pitches: list[Pitch], cf: Phrase) -> Phrase:
    notes = []
    for pitch, cf_event in zip(pitches, cf):
        notes.append(Note(
            pitch=pitch,
            duration=cf_event.duration,
            dynamic=None,
            articulations=(),
        ))
    return tuple(notes)

# Species II: two notes per CF note, each half the CF duration
HALF = Duration.from_cn("h")
QUARTER = Duration.from_cn("q")
```

### Candidate Generation with Range Constraint
```python
def _candidates_in_range(
    cf_pitch: Pitch,
    above: bool,
    pitch_range: tuple[Pitch, Pitch] | None,
    cf_pitches: list[Pitch],
) -> list[int]:
    """Return candidate MIDI numbers within range and consonant with CF."""
    if pitch_range:
        low_midi = pitch_range[0].midi_number
        high_midi = pitch_range[1].midi_number
    else:
        # Default: 10th above/below CF range
        cf_midis = [p.midi_number for p in cf_pitches]
        if above:
            low_midi = min(cf_midis)
            high_midi = max(cf_midis) + 16  # ~10th above highest CF note
        else:
            low_midi = min(cf_midis) - 16
            high_midi = max(cf_midis)

    return list(range(low_midi, high_midi + 1))
```

### Multi-Voice Score Construction
```python
def generate_multi_voice_counterpoint(
    cf: Phrase, n: int = 2, species: int = 1, above: int | None = None,
) -> Score:
    if not cf:
        raise ValueError("Cantus firmus must not be empty")
    if n > 4:
        raise ValueError(f"Maximum 4 counterpoint voices, got {n}")

    above_count = above if above is not None else n
    voices: list[tuple[str, Phrase]] = []

    # Generate voices above CF
    for i in range(above_count):
        cp = _generate_species(cf, species, above=True, existing_voices=voices)
        voices.append((f"cp{i + 1}", cp))

    # Generate voices below CF
    for i in range(n - above_count):
        cp = _generate_species(cf, species, above=False, existing_voices=voices)
        voices.append((f"cp{above_count + i + 1}", cp))

    # Insert CF, then sort all voices highest to lowest
    all_voices = voices + [("cf", cf)]
    # Sort by average MIDI pitch, highest first
    all_voices.sort(key=lambda v: -_avg_midi(v[1]))

    return Score(_voices=tuple(all_voices))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fux's original 5-species pedagogy | Same 5 species, computer-implemented | N/A -- classical rules unchanged | Rules are well-defined and stable; no "modern" alternative |
| Exhaustive search | Backtracking with heuristic ordering | Standard CS technique | Makes generation tractable for 8-20 note sequences |
| music21 counterpoint module | Custom implementation | Project decision | Zero-dep policy; music21 is 50MB+ overkill |

**This domain is stable.** Counterpoint rules have been codified since Fux (1725) and Jeppesen (1939). There is no "latest framework" -- the rules are the rules. Implementation is pure algorithmic work.

## Open Questions

1. **Fifth species rhythm selection**
   - What we know: Fifth species mixes note values from all other species
   - What's unclear: Exact heuristic for choosing when to use whole, half, quarter, or syncopated notes
   - Recommendation: Use a preference ordering (prefer longer notes at phrase start/end, shorter in middle; prefer suspensions at strong beats). This is Claude's discretion per CONTEXT.md.

2. **Multi-voice inter-voice constraints (CPTR-09)**
   - What we know: Each generated voice must be valid against the CF
   - What's unclear: How strictly to enforce rules between generated voices (CP1 vs CP2)
   - Recommendation: Check each CP voice against CF for species rules; additionally check all voice pairs for parallel 5ths/8ths and crossing. Use iterative generation (generate CP1 first, then CP2 considering both CF and CP1).

3. **Free counterpoint rule set (CPTR-08)**
   - What we know: No strict species rhythmic constraints; tonal voice-leading conventions
   - What's unclear: Exact definition of "tonal voice-leading conventions" beyond no parallel 5ths/8ths
   - Recommendation: Use consonant intervals on strong beats, allow passing tones on weak beats, enforce smooth voice leading (prefer stepwise, resolve leaps), no parallel 5ths/8ths. Essentially "relaxed first species" with rhythmic freedom.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `python3 -m pytest tests/counterpoint/ -x -q` |
| Full suite command | `python3 -m pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CPTR-01 | First species generation produces consonant intervals on every beat | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_first_species -x` | No -- Wave 0 |
| CPTR-02 | Second species: downbeat consonant, offbeat passing tones | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_second_species -x` | No -- Wave 0 |
| CPTR-03 | Third species: 4 notes per CF note, downbeat consonant | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_third_species -x` | No -- Wave 0 |
| CPTR-04 | Fourth species: suspensions resolve downward by step | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_fourth_species -x` | No -- Wave 0 |
| CPTR-05 | Fifth species: mixed rhythms, all rules satisfied | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_fifth_species -x` | No -- Wave 0 |
| CPTR-06 | Validation detects known violations in crafted examples | unit | `python3 -m pytest tests/counterpoint/test_validation.py -x` | No -- Wave 0 |
| CPTR-07 | Generation above and below CF both produce valid results | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_above_below -x` | No -- Wave 0 |
| CPTR-08 | Free counterpoint has no parallel 5ths/8ths, consonant beats | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_free_counterpoint -x` | No -- Wave 0 |
| CPTR-09 | Multi-voice returns Score with correct voice naming and count | unit | `python3 -m pytest tests/counterpoint/test_generation.py::test_multi_voice -x` | No -- Wave 0 |
| CPTR-10 | Custom rules dict overrides default severities | unit | `python3 -m pytest tests/counterpoint/test_validation.py::test_configurable_severity -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/counterpoint/ -x -q`
- **Per wave merge:** `python3 -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/counterpoint/__init__.py` -- package init
- [ ] `tests/counterpoint/test_validation.py` -- covers CPTR-06, CPTR-10
- [ ] `tests/counterpoint/test_generation.py` -- covers CPTR-01 through CPTR-05, CPTR-07, CPTR-08, CPTR-09
- [ ] `tests/counterpoint/conftest.py` -- shared fixtures (standard CF phrases, helper constructors)

## Species Counterpoint Rules Reference

### Universal Rules (All Species)
1. Begin and end on perfect consonance (P1, P5, P8)
2. Penultimate note must approach final by step (leading tone if ascending)
3. No parallel fifths or octaves
4. No direct (hidden) fifths or octaves (both voices move same direction to P5/P8 unless upper voice steps)
5. No voice crossing
6. Prefer contrary or oblique motion over similar motion
7. Prefer imperfect consonances (3rds, 6ths) over perfect
8. No more than 3 consecutive parallel 3rds or 6ths
9. Single climax point preferred
10. Avoid augmented intervals in melodic line

### First Species Specific
- Every note consonant with CF
- Predominantly stepwise motion
- No repeated notes

### Second Species Specific
- Downbeat: consonant
- Offbeat: consonant OR passing tone (stepwise between two consonances) OR neighbor tone
- First note may begin with a half rest followed by consonance
- No repeated notes across barline

### Third Species Specific
- First of four notes: consonant
- Others: passing tones, neighbor tones, cambiata acceptable
- Double neighbor (changing tone) pattern allowed

### Fourth Species Specific
- Syncopated: note begins on weak beat, held through strong beat
- Held-over note on strong beat may be dissonant (suspension)
- Suspension must resolve stepwise downward on next weak beat
- 7-6, 4-3, 9-8 suspensions are standard (above CF)
- 2-3, 5-6 suspensions when below CF

### Fifth Species Specific
- Combines rhythmic patterns from all species
- Must demonstrate variety -- not just one species throughout
- Suspensions, passing tones, neighbor tones all available
- Should show awareness of phrase shape and climax

## Sources

### Primary (HIGH confidence)
- Existing codebase: `cadenza.analysis.voiceleading` -- verified violation detection patterns, `_extract_pitches`, `_check_parallels` logic
- Existing codebase: `cadenza.core.interval.Interval.between()` -- verified interval computation with quality and semitones
- Existing codebase: `cadenza.core.score.Score` -- verified multi-voice container pattern
- Existing codebase: `cadenza.transforms.pitch.from_midi()` -- verified MIDI-to-pitch conversion

### Secondary (MEDIUM confidence)
- Species counterpoint rules: Based on Fux "Gradus ad Parnassum" and Jeppesen "Counterpoint" -- well-established music theory pedagogy, widely standardized across all music theory textbooks
- Backtracking search for constraint satisfaction: standard CS algorithm, well-suited for the problem size (8-20 note sequences)

### Tertiary (LOW confidence)
- Fifth species rhythm selection heuristics -- no single authoritative source; varies by textbook; implementation will need empirical tuning

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- pure Python, no external deps, all building blocks exist in codebase
- Architecture: HIGH -- subpackage pattern established by prior phases; backtracking is textbook algorithm
- Pitfalls: HIGH -- counterpoint rules are well-codified; common implementation errors are well-known
- Species rules: HIGH for I-IV, MEDIUM for V (florid species has more subjective stylistic choices)

**Research date:** 2026-03-20
**Valid until:** Indefinite -- music theory rules do not change; codebase patterns are stable
