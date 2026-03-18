# Phase 1: Foundation - Research

**Researched:** 2026-03-19
**Domain:** Core music data model, OMN notation parsing/serialization, project scaffolding
**Confidence:** HIGH

## Summary

Phase 1 establishes the immutable data model (Pitch, Duration, Interval, Note, Rest, Phrase, Score), a hand-written recursive descent OMN parser with sticky parameter resolution, an OMN serializer for compact output, and lossless JSON round-trip serialization. All core types are frozen dataclasses with zero runtime dependencies beyond the Python standard library.

The critical design constraint is that Eb3 != D#3 by default -- pitch must be a compound type preserving spelling. Duration must use `fractions.Fraction` exclusively. The parser must handle OMN's sticky parameter carry-forward (duration, dynamic, articulation inherit from previous note when omitted) and resolve all values to fully-explicit internal representation at parse time.

**Primary recommendation:** Build from the bottom up: Pitch -> Duration -> Interval -> Note/Rest -> Phrase -> Score -> OMN tokenizer -> OMN parser (with sticky state machine) -> OMN serializer -> JSON codec -> pyproject.toml scaffolding. Each layer gets its own test suite before the next layer begins.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Full sticky support: parser inherits duration, dynamic, and articulation from the previous note when omitted
- Matches Opusmodus convention exactly: `(e c4 pp stacc d4 e4)` -> d4 and e4 inherit `e`, `pp`, `stacc`
- Internal representation is always fully explicit -- stickiness is resolved at parse time, not stored
- Serializer outputs compact OMN (only writes values that differ from the previous note)
- Middle C = C4 (Scientific Pitch Notation / SPN standard)
- This diverges from Opusmodus (which uses C3 for middle C) -- document this difference prominently
- Negative duration convention: `-e` = eighth rest, `-q` = quarter rest, `-h` = half rest
- Rest is modeled as a distinct `Rest` type (not a Note with a null pitch), but serializes as negative duration
- Score stores voices as a named dict: `{'soprano': Phrase, 'alto': Phrase, ...}`
- Any string key is valid (not limited to SATB names)
- Voice order within the dict is preserved (Python 3.7+ dict ordering)
- Supported articulations (Phase 1): `stacc`, `ten`, `acc`, `leg`, `marc`, `fermata`, `trill`, `pizz`, `arco`
- Unknown articulation tokens produce a clear parse warning (not a hard error)

### Claude's Discretion
- Internal data structure for pitch accidentals: use string "b", "s", "bb", "ss", "n" for readability
- Fraction internal representation for duration: use `fractions.Fraction` throughout, never float
- Python version target: 3.11+ (for match statements and performance)
- Project package name: `cadenza` with submodules `cadenza.core`, `cadenza.omn`
- Testing framework: pytest with property-based tests via hypothesis for round-trip validation
- Packaging: pyproject.toml with uv/pip installable structure
- Core types: frozen dataclasses (not Pydantic) -- zero runtime dependencies

### Deferred Ideas (OUT OF SCOPE)
- Tie notation (`~` suffix) -- deferred; likely Phase 2
- Grace notes (acciaccatura, appoggiatura) -- deferred; Phase 2 or later
- Dynamic hairpin span events -- deferred to Phase 6
- Extended articulations (sul-pont, snap-pizz, flutter, harmonics) -- deferred to later phase
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CORE-01 | Pitch type is compound immutable value (letter A-G, accidental, octave integer) | Data Model Design: Pitch class with `step`, `accidental`, `octave` fields |
| CORE-02 | Pitch equality is spelling-sensitive: Eb3 != D#3; explicit `enharmonic_equal()` | Data Model Design: `__eq__` compares all fields; `enharmonic_equal()` compares MIDI numbers |
| CORE-03 | Duration type uses `fractions.Fraction` internally | Data Model Design: Duration class with `fraction` field of type `Fraction` |
| CORE-04 | Interval type encodes quality + number | Data Model Design: Interval class with `quality`, `number`, `direction` fields |
| CORE-05 | Note type combines Pitch + Duration + Dynamic + Articulation as frozen dataclass | Data Model Design: Note frozen dataclass |
| CORE-06 | Rest type is distinct from Note | Data Model Design: Rest frozen dataclass with duration only |
| CORE-07 | Phrase is ordered immutable sequence of Notes and Rests | Data Model Design: Phrase as tuple wrapper |
| CORE-08 | Score supports multiple simultaneous Phrases | Data Model Design: Score as named dict of Phrases |
| CORE-09 | All core types serializable to/from JSON without info loss | JSON Serialization section |
| CORE-10 | All core types support equality comparison and hashing | Frozen dataclass `__hash__`/`__eq__` section |
| NOTA-01 | Parse OMN strings into internal event objects | Parser Architecture section |
| NOTA-02 | Serialize internal objects back to OMN (round-trip lossless) | Parser Architecture: serializer design |
| NOTA-03 | Handle all duration values: w, h, q, e, s, t, x, with dots and ties | OMN Grammar & Vocabulary: duration tokens |
| NOTA-04 | Handle rests (negative durations) | OMN Grammar: rest token `-` prefix |
| NOTA-05 | Handle tuplets (triplets, quintuplets, etc.) | OMN Grammar: tuplet prefix syntax |
| NOTA-06 | Handle all dynamic markings: ppp..fff | OMN Grammar: dynamics vocabulary |
| NOTA-07 | Handle articulation markings | OMN Grammar: Phase 1 articulation set |
| NOTA-12 | Parser provides clear error messages with position info | Parser Architecture: error handling design |
</phase_requirements>

## Data Model Design

### Pitch (CORE-01, CORE-02, CORE-10)

**Confidence: HIGH** -- music theory is a stable domain; frozen dataclass behavior is well-documented.

```python
from dataclasses import dataclass
from typing import ClassVar

# Use string constants for accidentals -- matches OMN token vocabulary
# "n" = natural, "s" = sharp, "b" = flat, "ss" = double-sharp, "bb" = double-flat
ACCIDENTAL_SEMITONES: dict[str, int] = {
    "bb": -2, "b": -1, "n": 0, "s": 1, "ss": 2,
}

# Letter -> semitones above C within one octave
STEP_SEMITONES: dict[str, int] = {
    "c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11,
}

# Letter -> diatonic index (0-6) for interval computation
STEP_INDEX: dict[str, int] = {
    "c": 0, "d": 1, "e": 2, "f": 3, "g": 4, "a": 5, "b": 6,
}

@dataclass(frozen=True, order=False)
class Pitch:
    step: str          # "c", "d", "e", "f", "g", "a", "b" (lowercase)
    accidental: str    # "n", "s", "b", "ss", "bb"
    octave: int        # SPN: middle C = C4, range -1..10

    def __post_init__(self) -> None:
        if self.step not in STEP_SEMITONES:
            raise ValueError(f"Invalid step: {self.step!r}")
        if self.accidental not in ACCIDENTAL_SEMITONES:
            raise ValueError(f"Invalid accidental: {self.accidental!r}")
        if not (-1 <= self.octave <= 10):
            raise ValueError(f"Octave out of range: {self.octave}")

    @property
    def midi_number(self) -> int:
        """MIDI note number. C4 = 60."""
        return (self.octave + 1) * 12 + STEP_SEMITONES[self.step] + ACCIDENTAL_SEMITONES[self.accidental]

    @property
    def pitch_class(self) -> int:
        """Pitch class 0-11 (C=0)."""
        return self.midi_number % 12

    def enharmonic_equal(self, other: "Pitch") -> bool:
        """True if same sounding pitch (same MIDI number)."""
        return self.midi_number == other.midi_number

    def __lt__(self, other: "Pitch") -> bool:
        """Order by MIDI number, then by step for enharmonic equivalents."""
        if not isinstance(other, Pitch):
            return NotImplemented
        if self.midi_number != other.midi_number:
            return self.midi_number < other.midi_number
        return STEP_INDEX[self.step] < STEP_INDEX[other.step]

    def __le__(self, other: "Pitch") -> bool:
        return self == other or self < other

    def __gt__(self, other: "Pitch") -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return other < self

    def __ge__(self, other: "Pitch") -> bool:
        return self == other or self > other
```

**Key decisions:**
- `frozen=True` gives us `__hash__` and `__eq__` for free (compares ALL fields -- so Eb3 != D#3 automatically).
- `order=False` because we define custom `__lt__` that orders by MIDI number (musical ordering) not field-lexicographic ordering.
- `__post_init__` validates fields at construction time (no invalid Pitch can exist).
- `midi_number` and `pitch_class` are derived properties, never stored.
- Accidentals as strings ("s", "b", "ss", "bb", "n") match OMN tokens directly, reducing parser complexity.

### Duration (CORE-03)

**Confidence: HIGH**

```python
from fractions import Fraction

# OMN base duration -> fraction of whole note
BASE_DURATIONS: dict[str, Fraction] = {
    "w": Fraction(1, 1),       # whole
    "h": Fraction(1, 2),       # half
    "q": Fraction(1, 4),       # quarter
    "e": Fraction(1, 8),       # eighth
    "s": Fraction(1, 16),      # sixteenth
    "t": Fraction(1, 32),      # thirty-second
    "x": Fraction(1, 64),      # sixty-fourth
}

@dataclass(frozen=True, order=False)
class Duration:
    fraction: Fraction    # Duration as fraction of whole note. q = 1/4, e. = 3/16

    # These fields are metadata for OMN round-trip fidelity:
    base: str = "q"       # OMN base symbol: "w", "h", "q", "e", "s", "t", "x"
    dots: int = 0         # 0, 1, 2, or 3
    tuplet: int | None = None  # tuplet ratio numerator: 3 = triplet, 5 = quintuplet, None = no tuplet

    def __post_init__(self) -> None:
        if self.base not in BASE_DURATIONS:
            raise ValueError(f"Invalid base duration: {self.base!r}")
        if not (0 <= self.dots <= 3):
            raise ValueError(f"Dots out of range: {self.dots}")
        if self.fraction <= 0:
            raise ValueError("Duration fraction must be positive")

    def __lt__(self, other: "Duration") -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction < other.fraction

    def __le__(self, other: "Duration") -> bool:
        return self == other or self < other

    def __gt__(self, other: "Duration") -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.fraction > other.fraction

    def __ge__(self, other: "Duration") -> bool:
        return self == other or self > other

    @staticmethod
    def from_omn(base: str, dots: int = 0, tuplet: int | None = None) -> "Duration":
        """Construct Duration from OMN components, computing the fraction."""
        base_val = BASE_DURATIONS[base]
        # Apply dots: each dot adds half the previous increment
        frac = base_val
        increment = base_val
        for _ in range(dots):
            increment = increment / 2
            frac = frac + increment
        # Apply tuplet: e.g., triplet = play 3 in the time of 2
        if tuplet is not None:
            # Standard tuplet: n notes in the time of the next lower power-of-2
            # Triplet (3): 3 in 2 -> multiply by 2/3
            # Quintuplet (5): 5 in 4 -> multiply by 4/5
            import math
            normal = 2 ** (math.ceil(math.log2(tuplet)) - 1) if tuplet > 1 else 1
            frac = frac * Fraction(normal, tuplet)
        return Duration(fraction=frac, base=base, dots=dots, tuplet=tuplet)
```

**Key decisions:**
- The `fraction` field is the canonical value -- arithmetic uses this.
- `base`, `dots`, `tuplet` are metadata for OMN serialization fidelity (so `Duration.from_omn("q", dots=1)` round-trips to `"q."` not `"e+s"`).
- `__eq__` from frozen dataclass compares ALL fields. Two Durations with the same fraction but different base/dots are NOT equal (they represent different notational choices). If you need pure time-value comparison, compare `.fraction` directly.
- Tuplet computation: triplet quarter = `Fraction(1, 4) * Fraction(2, 3) = Fraction(1, 6)`.

### Interval (CORE-04)

**Confidence: HIGH** -- interval theory is centuries-old and well-formalized.

```python
@dataclass(frozen=True)
class Interval:
    quality: str    # "P", "M", "m", "A", "d", "AA", "dd"
    number: int     # 1=unison, 2=second, ..., 8=octave, 9=ninth (compound)
    direction: int  # +1 ascending, -1 descending

    # Lookup: (generic_interval_class, semitone_offset_from_major_or_perfect) -> quality
    # This is computed, not stored
    _PERFECT_INTERVALS: ClassVar[set[int]] = {1, 4, 5, 8}  # unison, fourth, fifth, octave

    @staticmethod
    def between(lower: Pitch, upper: Pitch) -> "Interval":
        """Compute the interval from lower to upper pitch.

        Algorithm:
        1. Compute generic interval from letter distance: (upper.step_index - lower.step_index) % 7 + 1
        2. Compute expected semitones for the generic interval in major scale
        3. Compute actual semitones between the two pitches
        4. Derive quality from the difference
        """
        # Step 1: generic interval (1-based)
        lower_idx = STEP_INDEX[lower.step]
        upper_idx = STEP_INDEX[upper.step]
        generic = (upper_idx - lower_idx) % 7 + 1

        # Account for octave span
        octave_span = upper.octave - lower.octave
        if upper_idx < lower_idx:
            octave_span -= 1
        number = generic + 7 * octave_span

        # Step 2: actual semitone distance
        semitones = upper.midi_number - lower.midi_number
        direction = 1 if semitones >= 0 else -1

        # Step 3: expected semitones for this generic interval (in C major, no accidentals)
        # ... quality derivation from semitone difference
        # (implementation details in code examples below)

        return Interval(quality=quality, number=abs(number), direction=direction)
```

**Critical algorithm for interval quality derivation:**

| Generic interval mod 7 | Perfect/Major baseline semitones |
|------------------------|----------------------------------|
| 1 (unison) | 0 (Perfect) |
| 2 (second) | 2 (Major) |
| 3 (third) | 4 (Major) |
| 4 (fourth) | 5 (Perfect) |
| 5 (fifth) | 7 (Perfect) |
| 6 (sixth) | 9 (Major) |
| 7 (seventh) | 11 (Major) |

For perfect intervals: actual == expected -> P, +1 -> A, -1 -> d, +2 -> AA, -2 -> dd
For major intervals: actual == expected -> M, -1 -> m, +1 -> A, -2 -> d, +2 -> AA

### Note (CORE-05), Rest (CORE-06)

```python
@dataclass(frozen=True)
class Note:
    pitch: Pitch
    duration: Duration
    dynamic: str | None = None           # "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", or None
    articulations: tuple[str, ...] = ()   # ("stacc", "trill"), etc.

@dataclass(frozen=True)
class Rest:
    duration: Duration
```

**Key decisions:**
- `dynamic` is `str | None` not an enum. This avoids import coupling and allows the parser to accept unknown dynamics with a warning (future-proofing).
- `articulations` is `tuple[str, ...]` not a frozenset -- order matters for OMN serialization fidelity.
- Both Note and Rest inherit `__hash__` and `__eq__` from frozen dataclass.
- No common base class needed. Use `Event = Note | Rest` union type.

### Phrase (CORE-07) and Score (CORE-08)

```python
# Phrase is a type alias, not a wrapper class (keeps it simple)
Event = Note | Rest
Phrase = tuple[Event, ...]

@dataclass(frozen=True)
class Score:
    voices: dict[str, Phrase]   # preserves insertion order (Python 3.7+)
    # Note: dict is mutable, but frozen dataclass prevents reassignment.
    # For true immutability, use MappingProxyType or validate in __post_init__.

    def __post_init__(self) -> None:
        # Convert to ensure immutability of the dict itself
        # Option: store as tuple of (name, phrase) pairs
        pass
```

**Important note on Score immutability:** A frozen dataclass with a `dict` field prevents attribute reassignment but the dict itself is mutable. Two approaches:

1. **Store as `tuple[tuple[str, Phrase], ...]`** internally, expose dict-like access via properties. Truly immutable and hashable.
2. **Use `types.MappingProxyType`** wrapper. Prevents mutation but MappingProxyType is not hashable.

**Recommendation:** Store as `tuple[tuple[str, Phrase], ...]` for true immutability and hashability (satisfies CORE-10). Provide a `voices` property that returns a dict view for convenience.

```python
@dataclass(frozen=True)
class Score:
    _voices: tuple[tuple[str, Phrase], ...] = ()

    @staticmethod
    def from_dict(voices: dict[str, Phrase]) -> "Score":
        return Score(_voices=tuple(voices.items()))

    @property
    def voices(self) -> dict[str, Phrase]:
        return dict(self._voices)

    @property
    def voice_names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self._voices)

    def __getitem__(self, voice_name: str) -> Phrase:
        for name, phrase in self._voices:
            if name == voice_name:
                return phrase
        raise KeyError(voice_name)
```

## OMN Grammar & Vocabulary

**Confidence: HIGH** for core vocabulary, MEDIUM for edge cases (compound durations, ratio notation).

Source: [Opusmodus OMN documentation](https://opusmodus.com/forums/omn-the-language/)

### Duration Tokens

| Token | Name | Fraction of whole |
|-------|------|-------------------|
| `w` | whole | 1/1 |
| `h` | half | 1/2 |
| `q` | quarter | 1/4 |
| `e` | eighth | 1/8 |
| `s` | sixteenth | 1/16 |
| `t` | thirty-second | 1/32 |
| `x` | sixty-fourth | 1/64 |

**Dots:** `.` = +50%, `..` = +75%, `...` = +87.5%. Appended to base: `q.`, `e..`

**Tuplet prefix:** digit before base duration. `3q` = triplet quarter, `5e` = quintuplet eighth, `7s` = septuplet sixteenth. Range: 2-9+ (but 2-9 covers all practical cases).

**Rests:** Negative duration prefix: `-w`, `-h`, `-q`, `-e`, `-s`, `-t`, `-x`. Also `-q.` for dotted quarter rest.

### Pitch Tokens

Format: `[letter][accidental?][octave]`

| Component | Values |
|-----------|--------|
| Letter | `c`, `d`, `e`, `f`, `g`, `a`, `b` (lowercase) |
| Accidental | `s` (sharp), `b` (flat), `ss` (double sharp), `bb` (double flat), `n` (explicit natural) -- optional, default natural |
| Octave | `0` through `10` (integer) |

Examples: `c4`, `eb3`, `fs5`, `bb2`, `css4`, `dbb3`

**Chord syntax:** pitches concatenated without spaces: `c4e4g4` = C major triad. Parser must detect multi-pitch tokens by identifying repeated `[letter][acc?][oct]` patterns within a single whitespace-delimited token.

**IMPORTANT: Opusmodus uses C3 for middle C. Cadenza uses C4 (SPN standard).** When parsing Opusmodus-sourced OMN strings, an octave offset of +1 is needed. This should be a parameter on the parser, NOT a default.

### Dynamic Tokens

Full set (12 levels):
`ppppp`, `pppp`, `ppp`, `pp`, `p`, `mp`, `mf`, `f`, `ff`, `fff`, `ffff`, `fffff`

Phase 1 minimum: `ppp`, `pp`, `p`, `mp`, `mf`, `f`, `ff`, `fff` (8 standard levels).
Accept the full 12 but the 8 are most common.

Special dynamics (OUT OF SCOPE for Phase 1): `sfz`, `sf`, `sff`, `sfp`, `fp`, `pf`, `pfp`, `fz`, `rfz`, `rf`, `cresc`, `dim`, and hairpin suffixes (`<`, `>`).

### Articulation Tokens (Phase 1 Set)

| Token | Meaning |
|-------|---------|
| `stacc` | staccato |
| `ten` | tenuto |
| `acc` | accent |
| `leg` | legato |
| `marc` | marcato |
| `fermata` | fermata |
| `trill` | trill |
| `pizz` | pizzicato |
| `arco` | arco |

**Unknown tokens:** Produce a `ParseWarning` (not an error). Store them as-is in the `articulations` tuple for round-trip fidelity.

### Sticky Parameter Behavior

In OMN, parameters carry forward from the previous note when omitted:

```
e c4 pp stacc d4 e4 q f4 mf
```

Means:
- `e c4 pp stacc` -- eighth, C4, pp, staccato
- `d4` -- inherits `e`, `pp`, `stacc` from previous
- `e4` -- inherits `e`, `pp`, `stacc` from previous
- `q f4 mf` -- quarter (new), F4, mf (new), no articulation (reset -- articulation does NOT carry forward when a new duration or dynamic is specified? -- VERIFY)

**Resolution strategy:**
- Duration: sticky. Carries forward until a new duration token appears.
- Dynamic: sticky. Carries forward until a new dynamic token appears.
- Articulation: sticky. Carries forward until a new articulation token appears OR an explicit empty articulation reset.

**Phase 1 rule:** All three are sticky. The internal representation stores fully-resolved values (every Note has explicit duration, dynamic, articulations). The serializer detects which values changed and only emits differences.

### Token Disambiguation

**The `f` / `b` / `e` / `s` ambiguity problem:**

| Token | Could be... | Resolution |
|-------|-------------|------------|
| `f` | pitch F or dynamic forte | If followed by a digit (octave), it is a pitch. If standalone or in dynamic position, it is dynamic. |
| `b` | pitch B or flat accidental suffix | If followed by a digit, it is pitch B. As suffix after another letter (`eb`), it is flat. |
| `e` | pitch E or duration eighth | If followed by a digit (octave), it is pitch E. If at start of token group or in duration position, it is duration. |
| `s` | pitch S? (no) / duration sixteenth / sharp suffix | `s` alone in duration position = sixteenth. As suffix after a letter (`cs`) = sharp. No pitch starts with `s`. |

**Parser strategy:** Tokenize positionally. First token in a group is duration (if it matches duration pattern). Subsequent tokens are pitch (if letter+digit), dynamic (if matches dynamic set), or articulation (if matches articulation set or is unknown text).

## Parser Architecture

**Confidence: HIGH** -- hand-written recursive descent is a well-understood technique, and the OMN grammar is simple enough for LL(1) parsing.

Decision: **Hand-written recursive descent parser** (not Lark). This was explicitly decided in STATE.md: "Hand-written recursive descent OMN parser (not Lark) for better error messages."

### Tokenizer Design

The tokenizer breaks an OMN string into a flat stream of typed tokens.

```python
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    DURATION = auto()       # "q", "e.", "3q", "q.."
    REST = auto()           # "-q", "-e.", "-3q"
    PITCH = auto()          # "c4", "eb3", "fs5", "c4e4g4" (chord)
    DYNAMIC = auto()        # "pp", "mf", "fff"
    ARTICULATION = auto()   # "stacc", "ten", "acc"
    LPAREN = auto()         # "("
    RPAREN = auto()         # ")"
    EOF = auto()

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int    # character offset in source string (for error messages)
    line: int        # line number (for multi-line OMN)
    column: int      # column number
```

**Tokenizer rules (ordered by priority):**

1. Skip whitespace, track position.
2. `(` -> LPAREN, `)` -> RPAREN
3. `-` followed by duration pattern -> REST
4. Digit `2-9` followed by duration letter -> DURATION (tuplet)
5. Duration letter (`w`, `h`, `q`, `e`, `s`, `t`, `x`) optionally followed by dots -> DURATION
   - **Disambiguation:** `e` alone could be duration eighth or pitch E. If followed by a digit, it is pitch E. If followed by a dot, another duration letter, whitespace, or end, it is duration eighth.
6. Pitch letter (`c`, `d`, `e`, `f`, `g`, `a`, `b`) followed by optional accidental + octave digit -> PITCH
   - Chord: if immediately followed by another pitch pattern (no space), keep accumulating into a single PITCH token with chord flag.
7. Dynamic pattern (longest match first: `fffff` before `ffff` before `fff` ... before `f`) -> DYNAMIC
8. Known articulation -> ARTICULATION
9. Unknown alphabetic token -> ARTICULATION with warning

### Parser Structure (Recursive Descent)

```python
class OmnParser:
    def __init__(self, source: str):
        self._tokenizer = OmnTokenizer(source)
        self._tokens: list[Token] = self._tokenizer.tokenize()
        self._pos = 0
        self._warnings: list[ParseWarning] = []

        # Sticky state
        self._current_duration: Duration | None = None
        self._current_dynamic: str | None = None
        self._current_articulations: tuple[str, ...] = ()

    def parse(self) -> tuple[Phrase, list[ParseWarning]]:
        """Parse the full OMN string, return (Phrase, warnings)."""
        events: list[Event] = []
        while not self._at_end():
            if self._check(TokenType.LPAREN):
                events.extend(self._parse_group())
            else:
                events.append(self._parse_event())
        return tuple(events), self._warnings

    def _parse_event(self) -> Event:
        """Parse a single note or rest event."""
        # Consume optional duration token -> update sticky state
        if self._check(TokenType.DURATION):
            self._current_duration = self._parse_duration_token()

        # Rest?
        if self._check(TokenType.REST):
            return self._parse_rest()

        # Must have a pitch
        pitch_token = self._expect(TokenType.PITCH)
        pitches = self._parse_pitch_token(pitch_token)

        # Consume optional dynamic -> update sticky state
        if self._check(TokenType.DYNAMIC):
            self._current_dynamic = self._advance().value

        # Consume optional articulations -> update sticky state
        arts: list[str] = []
        while self._check(TokenType.ARTICULATION):
            arts.append(self._advance().value)
        if arts:
            self._current_articulations = tuple(arts)

        duration = self._current_duration or Duration.from_omn("q")  # default quarter

        if len(pitches) > 1:
            # Chord -- deferred to later phase, but parser recognizes it
            pass

        return Note(
            pitch=pitches[0],
            duration=duration,
            dynamic=self._current_dynamic,
            articulations=self._current_articulations,
        )

    def _parse_group(self) -> list[Event]:
        """Parse a parenthesized group: (e c4 pp stacc d4 e4)"""
        self._expect(TokenType.LPAREN)
        events = []
        while not self._check(TokenType.RPAREN):
            events.append(self._parse_event())
        self._expect(TokenType.RPAREN)
        return events
```

### Sticky Parameter State Machine

```
State: {duration: Duration?, dynamic: str?, articulations: tuple[str, ...]}

On each event:
  1. If DURATION token present: state.duration = parse(token)
  2. If REST token: emit Rest(duration=state.duration or parse rest duration)
  3. Parse PITCH token(s)
  4. If DYNAMIC token present: state.dynamic = token.value
  5. If ARTICULATION token(s) present: state.articulations = tuple(tokens)
  6. Emit Note(pitch, state.duration, state.dynamic, state.articulations)

Reset conditions:
  - At start of parsing: all state = None/empty
  - Parenthesized groups: state carries across group boundaries (per OMN spec)
  - Articulations: sticky until replaced by new articulation(s). If a note has
    no articulation tokens but previous note did, the previous articulations carry forward.
```

### Error Reporting (NOTA-12)

```python
@dataclass(frozen=True)
class ParseError(Exception):
    message: str
    position: int
    line: int
    column: int
    source_snippet: str  # surrounding context from source string

    def __str__(self) -> str:
        return f"OMN parse error at line {self.line}, column {self.column}: {self.message}\n  {self.source_snippet}"

@dataclass
class ParseWarning:
    message: str
    position: int
    line: int
    column: int
```

Error messages must include:
- Line and column number
- The problematic token
- A snippet of surrounding source text
- A clear description of what was expected

### OMN Serializer

The serializer converts `Phrase -> str` producing compact OMN with sticky optimization.

```python
def to_omn(phrase: Phrase) -> str:
    """Serialize a Phrase to compact OMN string."""
    parts: list[str] = []
    prev_duration: Duration | None = None
    prev_dynamic: str | None = None
    prev_articulations: tuple[str, ...] = ()

    for event in phrase:
        tokens: list[str] = []

        if isinstance(event, Rest):
            # Always emit rest duration with - prefix
            tokens.append(f"-{_duration_to_omn(event.duration)}")
        elif isinstance(event, Note):
            # Emit duration only if changed
            if event.duration != prev_duration:
                tokens.append(_duration_to_omn(event.duration))
                prev_duration = event.duration

            # Always emit pitch
            tokens.append(_pitch_to_omn(event.pitch))

            # Emit dynamic only if changed
            if event.dynamic != prev_dynamic:
                if event.dynamic is not None:
                    tokens.append(event.dynamic)
                prev_dynamic = event.dynamic

            # Emit articulations only if changed
            if event.articulations != prev_articulations:
                tokens.extend(event.articulations)
                prev_articulations = event.articulations

        parts.append(" ".join(tokens))

    return " ".join(parts)
```

## JSON Serialization (CORE-09)

**Confidence: HIGH** -- standard Python techniques.

Strategy: Custom `json.JSONEncoder` subclass + `from_dict` class methods. No Pydantic in core.

### Design

```python
import json
import dataclasses
from fractions import Fraction

class CadenzaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Fraction):
            return {"_type": "Fraction", "numerator": obj.numerator, "denominator": obj.denominator}
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return {"_type": type(obj).__name__, **dataclasses.asdict(obj)}
        return super().default(obj)

def cadenza_decoder(dct: dict):
    """Object hook for json.loads."""
    if "_type" not in dct:
        return dct
    type_name = dct.pop("_type")
    if type_name == "Fraction":
        return Fraction(dct["numerator"], dct["denominator"])
    if type_name == "Pitch":
        return Pitch(**dct)
    if type_name == "Duration":
        dct["fraction"] = cadenza_decoder(dct["fraction"])  # nested Fraction
        return Duration(**dct)
    if type_name == "Note":
        dct["pitch"] = cadenza_decoder(dct["pitch"])
        dct["duration"] = cadenza_decoder(dct["duration"])
        dct["articulations"] = tuple(dct["articulations"])
        return Note(**dct)
    if type_name == "Rest":
        dct["duration"] = cadenza_decoder(dct["duration"])
        return Rest(**dct)
    # ... Score, Phrase handled similarly
    return dct

# Public API:
def to_json(obj) -> str:
    return json.dumps(obj, cls=CadenzaEncoder, indent=2)

def from_json(s: str):
    return json.loads(s, object_hook=cadenza_decoder)
```

**Key decisions:**
- `_type` discriminator field for polymorphic deserialization.
- `Fraction` serialized as `{"_type": "Fraction", "numerator": N, "denominator": D}` -- lossless.
- `tuple` fields (`articulations`, `_voices`) become JSON arrays; decoder converts back to tuples.
- `Phrase` (a tuple of Events) serialized as JSON array with each element having its `_type`.
- Validation happens in the dataclass `__post_init__`, so `from_json` will reject invalid data.

## Project Scaffolding

**Confidence: HIGH**

### Package Layout

```
cadenza/
  pyproject.toml
  src/
    cadenza/
      __init__.py           # version, top-level re-exports
      core/
        __init__.py          # re-export Pitch, Duration, Interval, Note, Rest, Phrase, Score, Event
        pitch.py             # Pitch, STEP_SEMITONES, ACCIDENTAL_SEMITONES, STEP_INDEX
        duration.py          # Duration, BASE_DURATIONS
        interval.py          # Interval
        note.py              # Note, Rest, Event type alias
        phrase.py            # Phrase type alias
        score.py             # Score
        json_codec.py        # CadenzaEncoder, cadenza_decoder, to_json, from_json
      omn/
        __init__.py          # re-export parse_omn, to_omn
        tokenizer.py         # OmnTokenizer, Token, TokenType
        parser.py            # OmnParser, parse_omn
        serializer.py        # to_omn
        errors.py            # ParseError, ParseWarning
  tests/
    __init__.py
    conftest.py              # shared fixtures, hypothesis strategies
    core/
      __init__.py
      test_pitch.py
      test_duration.py
      test_interval.py
      test_note.py
      test_phrase.py
      test_score.py
      test_json_codec.py
    omn/
      __init__.py
      test_tokenizer.py
      test_parser.py
      test_serializer.py
      test_round_trip.py     # property-based OMN -> parse -> serialize -> parse round-trip
    strategies.py            # hypothesis custom strategies
```

### pyproject.toml

```toml
[project]
name = "cadenza"
version = "0.1.0"
description = "Music analysis, transformation, and generation library"
requires-python = ">=3.11"
license = {text = "MIT"}

# ZERO runtime dependencies for core
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "hypothesis>=6.100",
    "ruff>=0.8",
    "mypy>=1.10",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cadenza"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "TCH"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**Key decisions:**
- ZERO runtime dependencies. Only stdlib (`fractions`, `dataclasses`, `json`, `enum`, `typing`).
- `hatchling` as build backend (simple, modern, no legacy baggage).
- `src/` layout prevents accidental imports from the project root.
- Python 3.11+ for `match` statements, `ExceptionGroup`, and performance improvements.

## Testing Strategy

**Confidence: HIGH**

### Hypothesis Custom Strategies

```python
# tests/strategies.py
from hypothesis import strategies as st
from hypothesis.strategies import composite
from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest

STEPS = ["c", "d", "e", "f", "g", "a", "b"]
ACCIDENTALS = ["n", "s", "b", "ss", "bb"]
DYNAMICS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", None]
ARTICULATIONS = ["stacc", "ten", "acc", "leg", "marc", "fermata", "trill", "pizz", "arco"]
BASES = ["w", "h", "q", "e", "s", "t"]

@composite
def pitch_strategy(draw):
    step = draw(st.sampled_from(STEPS))
    acc = draw(st.sampled_from(ACCIDENTALS))
    octave = draw(st.integers(min_value=0, max_value=9))
    # Filter out pitches with invalid MIDI numbers
    p = Pitch(step=step, accidental=acc, octave=octave)
    # Ensure MIDI number is in valid range
    if not (0 <= p.midi_number <= 127):
        from hypothesis import assume
        assume(False)
    return p

@composite
def duration_strategy(draw):
    base = draw(st.sampled_from(BASES))
    dots = draw(st.integers(min_value=0, max_value=2))
    use_tuplet = draw(st.booleans())
    tuplet = draw(st.integers(min_value=3, max_value=7)) if use_tuplet else None
    return Duration.from_omn(base, dots=dots, tuplet=tuplet)

@composite
def note_strategy(draw):
    return Note(
        pitch=draw(pitch_strategy()),
        duration=draw(duration_strategy()),
        dynamic=draw(st.sampled_from(DYNAMICS)),
        articulations=draw(st.tuples(*[st.sampled_from(ARTICULATIONS)] * draw(st.integers(0, 2)))),
    )

@composite
def rest_strategy(draw):
    return Rest(duration=draw(duration_strategy()))

@composite
def event_strategy(draw):
    return draw(st.one_of(note_strategy(), rest_strategy()))

@composite
def phrase_strategy(draw):
    events = draw(st.lists(event_strategy(), min_size=1, max_size=20))
    return tuple(events)
```

### Property-Based Round-Trip Tests

```python
from hypothesis import given

@given(phrase=phrase_strategy())
def test_omn_round_trip(phrase):
    """parse(to_omn(phrase)) == phrase -- lossless round-trip."""
    omn_string = to_omn(phrase)
    parsed, warnings = parse_omn(omn_string)
    assert parsed == phrase, f"Round-trip failed:\n  Original: {phrase}\n  OMN: {omn_string}\n  Parsed: {parsed}"

@given(phrase=phrase_strategy())
def test_json_round_trip(phrase):
    """from_json(to_json(phrase)) == phrase -- lossless round-trip."""
    json_string = to_json(phrase)
    parsed = from_json(json_string)
    assert parsed == phrase

@given(p=pitch_strategy())
def test_pitch_hash_consistency(p):
    """Equal pitches have equal hashes."""
    p2 = Pitch(step=p.step, accidental=p.accidental, octave=p.octave)
    assert p == p2
    assert hash(p) == hash(p2)

@given(p=pitch_strategy())
def test_midi_number_range(p):
    """All valid pitches have MIDI numbers in [0, 127]."""
    assert 0 <= p.midi_number <= 127

@given(lower=pitch_strategy(), upper=pitch_strategy())
def test_interval_between_consistency(lower, upper):
    """Interval.between computes correct semitone distance."""
    interval = Interval.between(lower, upper)
    # The interval's semitone value should match MIDI difference
    # (sign-aware)
    expected_semitones = upper.midi_number - lower.midi_number
    assert interval.semitones == expected_semitones
```

### Deterministic Unit Tests (Critical Cases)

```python
def test_eb3_not_equal_ds3():
    eb3 = Pitch(step="e", accidental="b", octave=3)
    ds3 = Pitch(step="d", accidental="ss", octave=3)
    assert eb3 != ds3                         # Spelling-sensitive equality
    assert eb3.enharmonic_equal(ds3)          # Same MIDI number
    assert eb3.midi_number == ds3.midi_number == 51

def test_sticky_parameters():
    phrase, _ = parse_omn("e c4 pp stacc d4 e4")
    assert len(phrase) == 3
    # All three notes should have the same duration, dynamic, articulation
    for note in phrase:
        assert note.duration == Duration.from_omn("e")
        assert note.dynamic == "pp"
        assert note.articulations == ("stacc",)
    assert phrase[0].pitch == Pitch("c", "n", 4)
    assert phrase[1].pitch == Pitch("d", "n", 4)
    assert phrase[2].pitch == Pitch("e", "n", 4)

def test_duration_fraction_arithmetic():
    q = Duration.from_omn("q")
    assert q.fraction == Fraction(1, 4)
    q_dot = Duration.from_omn("q", dots=1)
    assert q_dot.fraction == Fraction(3, 8)
    triplet_q = Duration.from_omn("q", tuplet=3)
    assert triplet_q.fraction == Fraction(1, 6)
```

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.x + hypothesis 6.x |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/ -x --timeout=30` |
| Full suite command | `pytest tests/ -v --cov=cadenza --cov-report=term-missing` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-01 | Pitch is compound immutable value | unit | `pytest tests/core/test_pitch.py -x` | Wave 0 |
| CORE-02 | Eb3 != D#3, enharmonic_equal works | unit | `pytest tests/core/test_pitch.py::test_enharmonic -x` | Wave 0 |
| CORE-03 | Duration uses Fraction | unit | `pytest tests/core/test_duration.py -x` | Wave 0 |
| CORE-04 | Interval quality + number | unit | `pytest tests/core/test_interval.py -x` | Wave 0 |
| CORE-05 | Note frozen dataclass | unit | `pytest tests/core/test_note.py -x` | Wave 0 |
| CORE-06 | Rest distinct type | unit | `pytest tests/core/test_note.py::test_rest -x` | Wave 0 |
| CORE-07 | Phrase is immutable sequence | unit | `pytest tests/core/test_phrase.py -x` | Wave 0 |
| CORE-08 | Score multi-voice | unit | `pytest tests/core/test_score.py -x` | Wave 0 |
| CORE-09 | JSON round-trip lossless | unit+property | `pytest tests/core/test_json_codec.py -x` | Wave 0 |
| CORE-10 | Equality + hashing | unit+property | `pytest tests/core/test_pitch.py::test_hash -x` | Wave 0 |
| NOTA-01 | Parse OMN -> events | unit+property | `pytest tests/omn/test_parser.py -x` | Wave 0 |
| NOTA-02 | Serialize events -> OMN (round-trip) | property | `pytest tests/omn/test_round_trip.py -x` | Wave 0 |
| NOTA-03 | All duration values w/dots/ties | unit | `pytest tests/omn/test_tokenizer.py::test_durations -x` | Wave 0 |
| NOTA-04 | Rests (negative durations) | unit | `pytest tests/omn/test_parser.py::test_rests -x` | Wave 0 |
| NOTA-05 | Tuplets | unit | `pytest tests/omn/test_parser.py::test_tuplets -x` | Wave 0 |
| NOTA-06 | Dynamic markings | unit | `pytest tests/omn/test_parser.py::test_dynamics -x` | Wave 0 |
| NOTA-07 | Articulation markings | unit | `pytest tests/omn/test_parser.py::test_articulations -x` | Wave 0 |
| NOTA-12 | Clear error messages with position | unit | `pytest tests/omn/test_parser.py::test_error_messages -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/ -x --timeout=30`
- **Per wave merge:** `pytest tests/ -v --cov=cadenza --cov-report=term-missing`
- **Phase gate:** Full suite green + all property tests pass (no shrunk counterexamples)

### Wave 0 Gaps

All test infrastructure must be created from scratch (greenfield project):

- [ ] `pyproject.toml` -- project configuration with pytest/hypothesis/ruff/mypy deps
- [ ] `tests/conftest.py` -- shared fixtures
- [ ] `tests/strategies.py` -- hypothesis custom strategies for Pitch, Duration, Note, Rest, Phrase
- [ ] `tests/core/test_pitch.py` -- covers CORE-01, CORE-02, CORE-10
- [ ] `tests/core/test_duration.py` -- covers CORE-03
- [ ] `tests/core/test_interval.py` -- covers CORE-04
- [ ] `tests/core/test_note.py` -- covers CORE-05, CORE-06
- [ ] `tests/core/test_phrase.py` -- covers CORE-07
- [ ] `tests/core/test_score.py` -- covers CORE-08
- [ ] `tests/core/test_json_codec.py` -- covers CORE-09
- [ ] `tests/omn/test_tokenizer.py` -- covers NOTA-03, NOTA-04, NOTA-05
- [ ] `tests/omn/test_parser.py` -- covers NOTA-01, NOTA-04, NOTA-05, NOTA-06, NOTA-07, NOTA-12
- [ ] `tests/omn/test_serializer.py` -- covers NOTA-02
- [ ] `tests/omn/test_round_trip.py` -- covers NOTA-02 (property-based)

## Critical Pitfalls for This Phase

### Pitfall 1: Pitch as Integer (CATASTROPHIC)

**Source:** PITFALLS.md Pitfall #1
**Applies to:** CORE-01, CORE-02

If any code path constructs a Pitch from a single integer without spelling context, the entire model is broken. Eb4 and D#4 produce different musical results in every downstream operation.

**Prevention:** Pitch constructor requires `(step, accidental, octave)`. No `Pitch.from_midi()` without a key/spelling context parameter. The `midi_number` property is read-only and derived.

### Pitfall 2: Context-Free Interval Naming (SEVERE)

**Source:** PITFALLS.md Pitfall #2
**Applies to:** CORE-04

Computing intervals from semitone distance alone makes dim5 and aug4 indistinguishable.

**Prevention:** `Interval.between(p1, p2)` computes from letter distance (generic interval) first, then derives quality from the semitone difference vs. expected semitones for that generic interval.

### Pitfall 3: Duration as Float (SEVERE)

**Source:** PITFALLS.md Pitfall #3
**Applies to:** CORE-03

Float arithmetic causes measures that don't sum correctly. A dotted quarter in float = 0.375, which accumulates rounding errors in long phrases.

**Prevention:** `fractions.Fraction` for ALL duration arithmetic. Duration constructor rejects float inputs. The `Fraction` type is exact for all musical durations.

### Pitfall 4: OMN Token Disambiguation (MODERATE)

**Source:** PITFALLS.md Pitfall #13
**Applies to:** NOTA-01, NOTA-03

`f` is both pitch F and dynamic forte. `e` is both pitch E and duration eighth. `b` is both pitch B and flat accidental.

**Prevention:** Positional tokenization. The tokenizer uses context (position within event, what follows the character) to disambiguate. Test extensively with ambiguous sequences: `e e4 f ff`, `q b4 f`, `s fs4 sf`.

### Pitfall 5: Sticky State Edge Cases (MODERATE)

**Source:** PITFALLS.md Pitfall #7
**Applies to:** NOTA-01, NOTA-02

What happens when the first event has no duration? What happens when sticky state crosses parenthesized groups?

**Prevention:**
- First event with no duration: default to `q` (quarter note) with a warning.
- Sticky state DOES cross parenthesized group boundaries (per OMN convention).
- Test: `"c4 d4 e4"` (no duration at all -- all default to q).
- Test: `"(e c4) (d4)"` (d4 inherits `e` from previous group).

### Pitfall 6: Score Dict Mutability (MODERATE)

**Applies to:** CORE-08, CORE-10

A frozen dataclass with a `dict` field is NOT truly immutable -- the dict can be mutated after construction.

**Prevention:** Store voices as `tuple[tuple[str, Phrase], ...]` internally. The `voices` property returns a fresh dict copy.

### Pitfall 7: Articulation Tuple Ordering (MINOR)

**Applies to:** NOTA-02, NOTA-07

If articulations are stored as a frozenset, OMN serialization order becomes nondeterministic. Round-trip tests will fail intermittently.

**Prevention:** Use `tuple[str, ...]` not `frozenset`. Preserve insertion order from the OMN source.

## Standard Stack

### Core (Zero Dependencies)

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| Python stdlib `fractions` | 3.11+ | Duration arithmetic | Exact rational arithmetic, no float errors |
| Python stdlib `dataclasses` | 3.11+ | Immutable type definitions | Frozen dataclasses give __hash__/__eq__ for free |
| Python stdlib `json` | 3.11+ | JSON serialization | Custom encoder/decoder, no external deps |
| Python stdlib `enum` | 3.11+ | TokenType enum | Clean token classification |
| Python stdlib `re` | 3.11+ | Tokenizer regex patterns | Token matching |
| Python stdlib `warnings` | 3.11+ | Parse warnings | Non-fatal parse issues |

### Dev Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.0 | Test runner |
| hypothesis | >=6.100 | Property-based testing |
| pytest-cov | >=5.0 | Coverage reporting |
| ruff | >=0.8 | Linting + formatting |
| mypy | >=1.10 | Static type checking |

**Installation:**
```bash
uv init cadenza
cd cadenza
uv add --dev pytest hypothesis pytest-cov ruff mypy
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rational arithmetic | Custom fraction class | `fractions.Fraction` (stdlib) | Battle-tested, handles edge cases, exact |
| Enum/constants | String constants scattered | `enum.Enum` or module-level dicts | Type safety, IDE support, discoverable |
| JSON encoding | Manual string concatenation | `json.JSONEncoder` subclass | Handles escaping, nesting, unicode correctly |
| Regex tokenization | Character-by-character loop | `re.compile` with named groups | Faster, more maintainable, less buggy |
| Test data generation | Manual test fixtures | Hypothesis strategies | Finds edge cases humans miss |

## Open Questions

1. **Articulation stickiness reset behavior:**
   - What we know: Duration and dynamic are clearly sticky in OMN.
   - What's unclear: Do articulations reset when a new event has no articulation tokens, or do they carry forward indefinitely? Opusmodus documentation is ambiguous on this point.
   - Recommendation: Implement as sticky (carry forward until replaced). Add a parser option `sticky_articulations=True` (default) to allow toggling.

2. **Chord support in Phase 1:**
   - What we know: OMN chord syntax is `c4e4g4` (pitches concatenated). CORE requirements mention Note and Rest but not Chord as a Phase 1 type.
   - What's unclear: Should the parser recognize chords in Phase 1, or defer to later?
   - Recommendation: The tokenizer should recognize chord tokens (multi-pitch). The parser should produce a Note with the first pitch and issue a warning about chord support being incomplete. This prevents parse failures on real-world OMN strings.

3. **Tuplet "normal notes" calculation:**
   - What we know: Triplet = 3 in the time of 2. Quintuplet = 5 in the time of 4.
   - What's unclear: The "normal notes" value for tuplets like 6 (could be 4 or 6-in-4?) and 9 (could be 8 or 6?).
   - Recommendation: Use the formula `normal = 2^(ceil(log2(n)) - 1)` which gives: 3->2, 4->2, 5->4, 6->4, 7->4, 8->4, 9->8. This matches standard music notation convention.

## Sources

### Primary (HIGH confidence)
- [Opusmodus OMN documentation](https://opusmodus.com/forums/omn-the-language/) -- OMN syntax, vocabulary, sticky parameter behavior
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) -- frozen=True behavior, __hash__, __eq__, order
- [Python fractions documentation](https://docs.python.org/3/library/fractions.html) -- Fraction arithmetic
- `.planning/research/PITFALLS.md` -- domain pitfalls specific to this project
- `.planning/research/ARCHITECTURE.md` -- architectural patterns
- `.planning/research/STACK.md` -- technology decisions

### Secondary (MEDIUM confidence)
- [Modelling Music: Calculating interval names](https://modelling-music.com/calculating-interval-names/) -- interval computation algorithm
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/) -- custom strategy patterns
- [Scientific Pitch Notation (Wikipedia)](https://en.wikipedia.org/wiki/Scientific_pitch_notation) -- octave numbering standard

### Tertiary (LOW confidence)
- OMN PDF specification was not readable via WebFetch (binary PDF). OMN vocabulary was verified against the forum documentation page instead. The full articulation vocabulary beyond Phase 1's core set may be incomplete.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero dependencies, all stdlib
- Architecture: HIGH -- frozen dataclasses and recursive descent parsing are well-understood
- Data model: HIGH -- music theory is a stable domain with centuries of formalization
- OMN grammar: HIGH for core tokens, MEDIUM for edge cases (compound durations, ratio notation, microtonality)
- Pitfalls: HIGH -- well-documented in project research

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain, no external dependencies to go stale)
