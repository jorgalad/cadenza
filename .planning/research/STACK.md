# Stack Research -- Cadenza

**Project:** Cadenza -- Music Analysis, Transformation, and Generation Library
**Researched:** 2026-03-18
**Source basis:** Training data (cutoff May 2025). WebSearch/WebFetch/Brave unavailable. Versions marked with (VERIFY) need confirmation against PyPI before use.

---

## Core Music Libraries

### Music21 -- Use as Reference/Interop, NOT as Runtime Dependency

**Version:** 9.x (VERIFY -- was 9.1+ as of early 2025)
**Confidence:** HIGH (well-known, stable library)

Music21 is the most comprehensive Python music theory library. It covers:

| Module Area | Key Modules | What It Does |
|-------------|------------|--------------|
| Pitch/Note | `pitch`, `note`, `chord` | Pitch representation with enharmonic awareness, MIDI number mapping, microtone support |
| Intervals | `interval` | Chromatic/diatonic intervals, interval vectors, transposition |
| Scales/Keys | `scale`, `key` | Major, minor, modal, whole-tone, octatonic, chromatic + key detection |
| Harmony | `roman`, `harmony`, `figuredBass` | Roman numeral analysis, chord symbols, figured bass realization |
| Counterpoint | `counterpoint` | Species counterpoint rules (limited -- only species I-II) |
| Streams | `stream` | Hierarchical container model (Score > Part > Measure > Note) |
| Serial/12-tone | `serial` | Tone rows, matrix operations, row transformations |
| Analysis | `analysis.floatingKey`, `analysis.discrete`, `analysis.windowed` | Key detection (Krumhansl-Schmuckler), ambitus, contour |
| MusicXML | `musicxml` (subpackages: `m21ToXml`, `xmlToM21`) | Full MusicXML 4.0 import/export |
| MIDI | `midi` | MIDI file read/write (basic -- not its strength) |
| Lilypond | `lily` | Lilypond export |
| ABC | `abcFormat` | ABC notation import |
| Corpus | `corpus` | Built-in Bach chorales, classical works for testing |
| Meter | `meter` | Time signatures, beat strength analysis |
| Tempo | `tempo` | MetronomeMark, tempo changes |
| Dynamics | `dynamics` | Dynamic markings (pp through ff) |
| Articulations | `articulations` | Staccato, tenuto, accent, etc. |
| Expressions | `expressions` | Fermata, trill, turn, etc. |
| Duration | `duration` | Duration representation with dots, tuplets, ties |
| Voiceleading | `voiceLeading` | Voice leading analysis, parallel 5ths/8ves detection |

**Why NOT use Music21 as runtime dependency:**

1. **Massive footprint.** Music21 pulls in matplotlib, scipy, and other heavy dependencies. It installs ~200MB+ of corpus data by default.
2. **Mutable object model.** Music21's `Stream` objects are deeply mutable. Cadenza's design calls for immutable data structures (named tuples / frozen dataclasses).
3. **Slow for API use.** Music21 was designed for Jupyter notebooks and academic research, not for sub-100ms API responses. Object creation overhead is significant.
4. **Impedance mismatch with OMN.** Music21 uses its own object hierarchy. Converting OMN <-> Music21 objects on every API call adds unnecessary overhead.
5. **Tight coupling risk.** Building on Music21 internals means inheriting its design decisions and bugs.

**How to use Music21 instead:**

- **Reference implementation.** Validate Cadenza's music theory against Music21's output during testing.
- **MusicXML interop bridge.** Use `music21.converter.parse()` and `music21.musicxml.m21ToXml` as a fallback/validation path for MusicXML I/O.
- **Corpus access.** Use Music21's built-in Bach chorales and other works as test fixtures.
- **Optional integration.** Provide a `cadenza.compat.music21` module that converts between Cadenza's data model and Music21 objects for users who want both.

### mingus -- Do NOT Use

**Confidence:** HIGH

mingus is abandoned. Last meaningful update was years ago. Its music theory model is incomplete (no enharmonic awareness, limited key/scale support). Music21 does everything mingus does, better.

### abjad -- Consider for Lilypond Output Only

**Version:** 3.x (VERIFY)
**Confidence:** MEDIUM

Abjad is a Python library for formalized score control, closely tied to Lilypond. It has excellent notation-level detail. However, it is too opinionated about its own object model to serve as Cadenza's core. Could be useful later if Lilypond output is needed.

---

## REST API Framework

### FastAPI -- Use This

**Version:** 0.115+ (VERIFY -- FastAPI was at 0.110+ in early 2025)
**Confidence:** HIGH

FastAPI is the clear choice. Rationale:

| Criterion | FastAPI | Flask | Django REST | Litestar |
|-----------|---------|-------|-------------|----------|
| Async support | Native (ASGI) | Bolt-on | Bolt-on | Native |
| Pydantic integration | Built-in (v2) | Manual | Serializers | Built-in |
| Auto OpenAPI docs | Yes | No (needs flask-smorest) | Yes (DRF-spectacular) | Yes |
| Performance | High | Low | Medium | High |
| Type safety | Full | None | Partial | Full |
| Ecosystem size | Large | Largest | Large | Small |

**Why FastAPI specifically for Cadenza:**

1. **Pydantic v2 native.** Musical event validation (pitch ranges, duration values, dynamic enums) maps perfectly to Pydantic validators.
2. **Auto-generated OpenAPI spec.** Dorico/Sibelius integration teams can consume the API spec directly.
3. **Async ready.** Long-running operations (batch transformations, counterpoint generation) can be async without blocking.
4. **Dependency injection.** Clean way to inject key context, scale context, etc. into transformation endpoints.

**Supporting packages:**

| Package | Version | Purpose |
|---------|---------|---------|
| `uvicorn` | 0.30+ (VERIFY) | ASGI server |
| `httpx` | 0.27+ (VERIFY) | Async HTTP client for testing |
| `pydantic` | 2.9+ (VERIFY) | Data validation (bundled with FastAPI but pin explicitly) |

**Litestar** is a viable alternative if FastAPI's Starlette dependency causes issues, but FastAPI's ecosystem is significantly larger. No reason to deviate.

---

## Data Modeling (Musical Events)

### Recommendation: Frozen Pydantic v2 Models (NOT named tuples, NOT plain dataclasses)

**Confidence:** HIGH

The PROJECT.md mentions "immutable named tuples" but this should be reconsidered. Here is why:

| Approach | Immutable | Validation | JSON Serialization | API Integration | Type Hints |
|----------|-----------|------------|-------------------|-----------------|------------|
| `NamedTuple` | Yes | None | Manual | Manual | Basic |
| `@dataclass(frozen=True)` | Yes | None | Manual | Manual | Full |
| `pydantic.BaseModel (frozen=True)` | Yes | Built-in | Built-in | Native FastAPI | Full |
| `msgspec.Struct (frozen=True)` | Yes | Built-in | Built-in (faster) | Manual adapter | Full |

**Use Pydantic v2 frozen models because:**

1. **Validation is critical.** A Pitch must have a valid letter name (A-G), valid accidental, valid octave. Pydantic validators enforce this at construction time.
2. **FastAPI integration is zero-cost.** Pydantic models ARE the request/response schemas.
3. **OMN serialization.** Custom `model_serializer` can output OMN strings. Custom `model_validator` can parse OMN strings.
4. **Immutability.** `model_config = ConfigDict(frozen=True)` gives hashable, immutable objects.
5. **Performance.** Pydantic v2's Rust core (pydantic-core) is fast enough for API use. If profiling shows it is a bottleneck, the internal representations can be swapped to msgspec later without changing the API layer.

### Proposed Core Data Model

```python
from pydantic import BaseModel, ConfigDict, field_validator
from enum import Enum
from typing import Optional

class PitchName(str, Enum):
    C = "c"; D = "d"; E = "e"; F = "f"
    G = "g"; A = "a"; B = "b"

class Accidental(str, Enum):
    NATURAL = "n"
    SHARP = "s"       # OMN convention: 's' suffix
    FLAT = "b"        # OMN convention: 'b' suffix
    DOUBLE_SHARP = "ss"
    DOUBLE_FLAT = "bb"

class Dynamic(str, Enum):
    PPPP = "pppp"; PPP = "ppp"; PP = "pp"; P = "p"
    MP = "mp"; MF = "mf"; F = "f"; FF = "ff"
    FFF = "fff"; FFFF = "ffff"

class Pitch(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: PitchName
    accidental: Accidental = Accidental.NATURAL
    octave: int  # Scientific pitch: middle C = C4

    @field_validator("octave")
    @classmethod
    def valid_octave(cls, v: int) -> int:
        if not -1 <= v <= 10:
            raise ValueError(f"Octave {v} out of range [-1, 10]")
        return v

    @property
    def midi_number(self) -> int:
        # C4 = 60
        ...

class Duration(BaseModel):
    model_config = ConfigDict(frozen=True)
    # OMN durations: w=whole, h=half, q=quarter, e=eighth, s=sixteenth
    base: str  # "w", "h", "q", "e", "s", "t" (32nd)
    dots: int = 0
    tuplet_ratio: Optional[tuple[int, int]] = None  # (3,2) = triplet

class Note(BaseModel):
    model_config = ConfigDict(frozen=True)
    pitch: Pitch
    duration: Duration
    dynamic: Optional[Dynamic] = None
    articulations: tuple[str, ...] = ()

class Rest(BaseModel):
    model_config = ConfigDict(frozen=True)
    duration: Duration

class Chord(BaseModel):
    model_config = ConfigDict(frozen=True)
    pitches: tuple[Pitch, ...]
    duration: Duration
    dynamic: Optional[Dynamic] = None
    articulations: tuple[str, ...] = ()

# A musical phrase is a sequence of events
MusicalEvent = Note | Rest | Chord
Phrase = tuple[MusicalEvent, ...]
```

**Key design decisions:**

- Use `tuple` not `list` for immutable sequences (hashable, consistent with frozen model).
- Pitch uses scientific notation internally, converts to/from OMN on serialization boundary.
- Dynamic is optional per-event (inherits from context if not specified).
- Articulations as tuple of strings (extensible, matches OMN's open vocabulary).

---

## OMN Notation Parsing

### The OMN Format

OMN (Opusmodus Music Notation) represents musical events as S-expression-like sequences:

```
(e c4 mp stacc)        ; eighth note, C4, mezzo-piano, staccato
(q. eb4 f ten)          ; dotted quarter, Eb4, forte, tenuto
(h c4e4g4 pp)           ; half note chord (C-E-G), pianissimo
(-q)                    ; quarter rest
(s fs5 ff acc)          ; sixteenth, F#5, fortissimo, accent
(3q c4 d4 e4 mf)       ; triplet quarters
```

**OMN syntax rules (from Opusmodus documentation):**

| Element | Syntax | Examples |
|---------|--------|----------|
| Duration | Letter prefix: `w`=whole, `h`=half, `q`=quarter, `e`=eighth, `s`=16th, `t`=32nd | `q`, `e.` (dotted), `3q` (triplet) |
| Pitch | Note name + optional accidental + octave number | `c4`, `eb3`, `fs5`, `bb2` |
| Accidental | `s`=sharp, `b`=flat, `ss`=double-sharp, `bb`=double-flat, `n`=natural | `cs4`, `bb3` |
| Dynamic | Standard markings | `ppp`, `pp`, `p`, `mp`, `mf`, `f`, `ff`, `fff` |
| Articulation | Text keywords | `stacc`, `ten`, `acc`, `marc`, `leg` |
| Rest | Duration prefixed with `-` | `-q`, `-e`, `-h` |
| Chord | Pitches concatenated (no spaces) | `c4e4g4` (C major triad) |
| Tuplet | Number prefix on duration | `3q` (triplet quarter), `5e` (quintuplet eighth) |

### Parsing Approach: Lark (EBNF Grammar Parser)

**Library:** `lark` (formerly `lark-parser`)
**Version:** 1.2+ (VERIFY)
**Confidence:** HIGH

**Why Lark and not alternatives:**

| Parser | Why/Why Not |
|--------|-------------|
| **Lark** | EBNF grammar syntax, Earley + LALR backends, tree transformers, excellent for DSLs. USE THIS. |
| `pyparsing` | Older, slower, less elegant. No grammar file support. |
| `ply` (Python Lex/Yacc) | Too low-level for this use case. |
| `parsimonious` | PEG parser, decent but Lark has better DX and community. |
| Hand-written recursive descent | Would work but unnecessary -- OMN grammar is regular enough for Lark. |
| `re` (regex only) | OMN has nesting (chords, tuplets) that regex handles poorly. |

### OMN Grammar (Lark EBNF)

```lark
start: event+

event: note | rest | chord

note: duration pitch dynamic? articulation*
rest: REST_DURATION
chord: duration pitch_group dynamic? articulation*

pitch_group: pitch pitch+     // Two or more pitches = chord
pitch: PITCH_NAME ACCIDENTAL? OCTAVE
duration: TUPLET? BASE_DURATION DOTS?

PITCH_NAME: /[a-g]/
ACCIDENTAL: "ss" | "bb" | "s" | "b" | "n"
OCTAVE: /[0-9]|10/
BASE_DURATION: "w" | "h" | "q" | "e" | "s" | "t"
DOTS: /\.+/
TUPLET: /[3-9]/
REST_DURATION: "-" BASE_DURATION DOTS?

dynamic: DYNAMIC
DYNAMIC: "pppp" | "ppp" | "pp" | "p" | "mp" | "mf" | "f" | "ff" | "fff" | "ffff"

articulation: ARTICULATION
ARTICULATION: "stacc" | "ten" | "acc" | "marc" | "leg" | "port"
            | "trem" | "trill" | "fermata" | "pizz" | "arco"

%import common.WS
%ignore WS
```

**Implementation plan:**

1. Define grammar in `.lark` file (loaded at module init, not per-parse).
2. Use `Transformer` class to convert Lark parse tree into Cadenza data model objects.
3. Provide `parse_omn(text: str) -> Phrase` and `to_omn(phrase: Phrase) -> str` as the public API.
4. The serializer (`to_omn`) is simpler -- just string formatting from the data model, no parser needed.

**Cadenza OMN extensions beyond Opusmodus:**
- Allow optional parentheses (Opusmodus requires them, Cadenza can support flat sequences too).
- Allow JSON-embedded OMN strings in API payloads.
- Support duration-sticky parsing: if duration is omitted, inherit from previous event (Opusmodus behavior).

---

## MIDI / MusicXML I/O

### MIDI

**Recommendation: `mido` for low-level MIDI I/O**

| Library | Version | Status | Recommendation |
|---------|---------|--------|----------------|
| `mido` | 1.3+ (VERIFY) | Active, well-maintained | **USE** -- clean API, no heavy dependencies, read/write MIDI files |
| `pretty_midi` | 0.2.10+ (VERIFY) | Maintained but depends on numpy | **Optional** -- useful for piano-roll / timing analysis, but numpy dependency is heavy for a library |
| `midiutil` | 1.2.1 | Stable but minimal updates | **Skip** -- mido covers the same ground with better API |
| `python-rtmidi` | 1.5+ (VERIFY) | Active | **Skip** -- real-time MIDI I/O, not needed (Cadenza is offline/file-based) |

**Why mido:**
- Pure Python with optional C extension for speed.
- Clean message/track/file model that maps well to Cadenza's data model.
- No numpy/scipy dependency.
- Handles all standard MIDI file types (0, 1, 2).

**MIDI conversion strategy:**

```python
# cadenza.io.midi
def phrase_to_midi(phrase: Phrase, tempo: int = 120) -> mido.MidiFile: ...
def midi_to_phrase(midi: mido.MidiFile, track: int = 0) -> Phrase: ...
```

Note: MIDI loses information vs. OMN (no enharmonic spelling, no articulation detail). Document this clearly in the API.

### MusicXML

**Recommendation: Build a lightweight MusicXML reader/writer using `lxml`, with Music21 as validation fallback**

| Approach | Pros | Cons |
|----------|------|------|
| **`lxml` (direct XML)** | Fast, no heavy deps, full control | Must implement MusicXML schema mapping manually |
| Music21's MusicXML module | Complete, battle-tested | Pulls in all of Music21 (~200MB+), slow |
| `partitura` | Academic, good MusicXML support | numpy/scipy deps, less maintained |
| `music-tag` | Not relevant (audio metadata, not notation) | -- |

**Why build on lxml:**

1. MusicXML is XML. Cadenza only needs a subset (notes, chords, rests, dynamics, articulations, key/time signatures). Full MusicXML 4.0 is enormous but the Cadenza-relevant subset is manageable.
2. Both Dorico and Sibelius export/import MusicXML. This is THE interchange format.
3. `lxml` is fast (C-based libxml2 bindings), well-maintained, and a common dependency that won't bloat the install.
4. Custom implementation means exact control over how OMN data maps to/from MusicXML elements.

**MusicXML subset to support (Phase 1):**

| MusicXML Element | Cadenza Mapping |
|------------------|-----------------|
| `<note>` | `Note` / `Rest` |
| `<pitch>` (step, alter, octave) | `Pitch` |
| `<duration>` + `<type>` | `Duration` |
| `<chord/>` tag | `Chord` (multiple pitches) |
| `<rest/>` | `Rest` |
| `<dynamics>` | `Dynamic` |
| `<articulations>` | articulation strings |
| `<key>` | Key context |
| `<time>` | Time signature context |
| `<direction>` (tempo) | Tempo context |

**Library:**

| Package | Version | Purpose |
|---------|---------|---------|
| `lxml` | 5.x (VERIFY) | MusicXML parsing and generation |

**Phase 2 (later):** For complex MusicXML features (beaming, layout, multi-voice), consider adding Music21 as optional dependency for fallback conversion.

---

## Testing

### Framework: pytest + hypothesis

**Confidence:** HIGH

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 8.x (VERIFY) | Test runner |
| `pytest-asyncio` | 0.24+ (VERIFY) | Async test support for FastAPI endpoints |
| `hypothesis` | 6.x (VERIFY) | Property-based testing -- critical for music theory |
| `httpx` | 0.27+ (VERIFY) | FastAPI TestClient |
| `pytest-cov` | 5.x (VERIFY) | Coverage reporting |

**Why hypothesis is critical for Cadenza:**

Music theory has formal properties that must hold universally:

```python
from hypothesis import given, strategies as st

# Retrograde of retrograde = original
@given(phrase=phrase_strategy())
def test_retrograde_involution(phrase):
    assert retrograde(retrograde(phrase)) == phrase

# Transposition preserves intervals
@given(phrase=phrase_strategy(), semitones=st.integers(-12, 12))
def test_transposition_preserves_intervals(phrase, semitones):
    original_intervals = get_intervals(phrase)
    transposed_intervals = get_intervals(transpose(phrase, semitones))
    assert original_intervals == transposed_intervals

# Inversion + inversion = original (around same axis)
@given(phrase=phrase_strategy(), axis=pitch_strategy())
def test_inversion_involution(phrase, axis):
    assert invert(invert(phrase, axis), axis) == phrase

# MIDI round-trip preserves pitch (but loses enharmonic spelling)
@given(note=note_strategy())
def test_midi_roundtrip_preserves_pitch_class(note):
    midi_num = note.pitch.midi_number
    roundtrip = pitch_from_midi(midi_num)
    assert roundtrip.midi_number == midi_num
```

**Custom hypothesis strategies needed:**

- `pitch_strategy()` -- generates valid Pitch objects within MIDI range
- `duration_strategy()` -- generates valid Duration objects
- `note_strategy()` -- generates valid Note objects
- `phrase_strategy()` -- generates sequences of events
- `key_strategy()` -- generates valid key signatures
- `scale_strategy()` -- generates valid scales

**Music21 as test oracle:**

Use Music21 in the test suite (not in production code) to validate Cadenza's output:

```python
def test_roman_numeral_analysis_matches_music21():
    # Parse with both Cadenza and Music21, compare results
    ...
```

---

## Package Management

### Recommendation: uv

**Version:** 0.5+ (VERIFY -- uv was rapidly evolving through 2025)
**Confidence:** MEDIUM (uv is newer, but has achieved wide adoption)

| Tool | Speed | Lock File | Workspace | Python Management | Recommendation |
|------|-------|-----------|-----------|-------------------|----------------|
| **uv** | Fastest (Rust) | Yes (`uv.lock`) | Yes | Yes (can install Python) | **USE** |
| Poetry | Medium | Yes (`poetry.lock`) | Yes | No | Viable fallback |
| pip + pip-tools | Slow | `requirements.txt` | No | No | Legacy |
| PDM | Medium | Yes | Yes | Yes | Less adoption than uv |

**Why uv:**

1. 10-100x faster than pip/poetry for dependency resolution.
2. Replaces pip, pip-tools, pyenv, and virtualenv in one tool.
3. Lock file format ensures reproducible installs.
4. Workspace support for monorepo (if Cadenza splits into `cadenza-core`, `cadenza-api`, `cadenza-io` packages later).
5. Wide adoption in the Python ecosystem as of 2025.

**Project structure with uv:**

```
cadenza/
  pyproject.toml          # Single source of truth for metadata + deps
  uv.lock                 # Locked dependencies
  src/
    cadenza/
      __init__.py
      core/               # Data model, pitch, interval, etc.
      transforms/         # Retrograde, inversion, transposition, etc.
      harmony/            # Chord analysis, Roman numerals, voice leading
      counterpoint/       # Species counterpoint, canon generation
      rhythm/             # Rhythmic transformations, Euclidean rhythms
      serial/             # 12-tone, set theory operations
      parser/             # OMN parsing (Lark grammar)
      io/                 # MIDI, MusicXML I/O
      api/                # FastAPI application
      compat/             # Music21 interop (optional)
  tests/
  grammars/
    omn.lark              # OMN grammar file
```

**pyproject.toml structure:**

```toml
[project]
name = "cadenza"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "pydantic>=2.9",
    "lark>=1.2",
    "mido>=1.3",
    "lxml>=5.0",
]

[project.optional-dependencies]
api = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
music21 = [
    "music21>=9.1",
]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "hypothesis>=6.100",
    "httpx>=0.27",
    "ruff>=0.8",
    "mypy>=1.12",
]
```

**Key: Core library has minimal deps (pydantic, lark, mido, lxml). FastAPI and Music21 are optional.**

---

## DAW Integration (Dorico / Sibelius APIs)

### Dorico Remote Control API

**Confidence:** MEDIUM (based on training data -- needs verification against current Steinberg docs)

Dorico (since version 4+) has a **Remote Control API** that communicates via WebSocket/HTTP:

- **Protocol:** JSON-RPC over WebSocket (port configurable, default around 4560).
- **NOT a Python scripting API embedded in Dorico.** Despite the PROJECT.md mention of "Dorico has a Python scripting API," what Dorico actually has is:
  1. A **Lua scripting engine** (Script menu) for internal automation.
  2. A **Remote Control API** (JSON-RPC) for external tools to control Dorico.
- **What the Remote Control API can do:**
  - Get/set the current selection
  - Trigger Dorico commands (add note, change pitch, change duration, etc.)
  - Navigate the score (move to measure, select voices, etc.)
  - Import/export MusicXML
  - Get score structure (flows, layouts, players, instruments)

**Integration strategy for Cadenza + Dorico:**

1. Cadenza runs as an HTTP service.
2. A small **bridge script** (Lua or standalone Python) connects to both Dorico's Remote Control API and Cadenza's REST API.
3. User selects notes in Dorico -> bridge reads selection via Dorico API -> sends to Cadenza for transformation -> bridge writes result back via Dorico API.
4. MusicXML is the data interchange format (Dorico can export selection as MusicXML).

**IMPORTANT CORRECTION:** The PROJECT.md states "Dorico has a Python scripting API." This needs verification. Based on training data, Dorico's native scripting is Lua, not Python. The Remote Control API is language-agnostic (any WebSocket client works, including Python). This is a critical clarification for the roadmap.

### Sibelius ManuScript / Plugin API

**Confidence:** MEDIUM (based on training data -- Avid's documentation is notoriously sparse)

Sibelius uses **ManuScript**, a proprietary scripting language:

- **ManuScript** is a simple procedural language (C-like syntax) built into Sibelius.
- Plugins are `.plg` files written in ManuScript.
- **Capabilities:** Select notes, modify pitch/duration/dynamics, add text, navigate score.
- **Limitations:** No HTTP client built into ManuScript. No direct way to call external APIs.
- **No Python scripting.** Sibelius has no Python integration.

**Integration strategy for Cadenza + Sibelius:**

1. Cadenza runs as an HTTP service.
2. A **companion app** (Electron, Python, or native) acts as bridge:
   - Reads Sibelius selection via ManuScript plugin that exports selection to a temp MusicXML file.
   - Calls Cadenza REST API with the extracted musical data.
   - Writes result back as MusicXML, reimports into Sibelius via ManuScript.
3. Alternatively, Sibelius users export MusicXML, process with Cadenza, reimport.

**ManuScript plugin (Sibelius side) example concept:**

```manuscript
// Export selection to MusicXML temp file
plugin "CadenzaBridge" {
    Initialize() {
        // Get current selection
        sel = Sibelius.ActiveScore.Selection;
        // Export to temp file
        Sibelius.ActiveScore.SaveAs(tempPath, "MusicXML");
        // Signal companion app (via file watcher or shared memory)
    }
}
```

**Sibelius also supports:** Cloud integration and a REST-based plugin framework in newer versions (Sibelius 2024+). This is worth investigating but documentation is scarce.

---

## Recommendations Summary

| Category | Choice | Version (VERIFY) | Confidence |
|----------|--------|-------------------|------------|
| **Python** | 3.12+ | 3.12.x or 3.13.x | HIGH |
| **Data Model** | Pydantic v2 (frozen) | >=2.9 | HIGH |
| **OMN Parser** | Lark | >=1.2 | HIGH |
| **MIDI I/O** | mido | >=1.3 | HIGH |
| **MusicXML I/O** | lxml (custom) | >=5.0 | HIGH |
| **REST API** | FastAPI | >=0.115 | HIGH |
| **ASGI Server** | uvicorn | >=0.30 | HIGH |
| **Test Framework** | pytest + hypothesis | pytest>=8, hypothesis>=6.100 | HIGH |
| **Package Manager** | uv | >=0.5 | MEDIUM |
| **Linter/Formatter** | ruff | >=0.8 | HIGH |
| **Type Checker** | mypy | >=1.12 | HIGH |
| **Music21** | Test oracle + optional compat | >=9.1 | HIGH |
| **Dorico Integration** | REST API + Remote Control bridge | N/A | MEDIUM |
| **Sibelius Integration** | REST API + ManuScript bridge + MusicXML | N/A | MEDIUM |

### Dependency Tiers

**Tier 1 -- Core library (always installed):**
`pydantic`, `lark`, `mido`, `lxml`

**Tier 2 -- API server (optional):**
`fastapi`, `uvicorn`

**Tier 3 -- Interop (optional):**
`music21`

**Tier 4 -- Development:**
`pytest`, `hypothesis`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`, `pytest-cov`

---

## What NOT to Use

| Library/Tool | Why Not |
|--------------|---------|
| **mingus** | Abandoned, incomplete music theory, no enharmonic awareness |
| **music-tag** | For audio file metadata (ID3 tags), not notation. Wrong domain entirely. |
| **pretty_midi** | numpy dependency too heavy for a library. Use mido instead. If piano-roll visualization is needed later, add as optional dep. |
| **midiutil** | Less capable than mido, less maintained |
| **python-rtmidi** | Real-time MIDI -- Cadenza is offline/file-based |
| **FluidSynth / pyfluidsynth** | Audio synthesis -- explicitly out of scope |
| **Flask** | No async, no native Pydantic, no auto OpenAPI. Inferior to FastAPI for this use case. |
| **Django REST Framework** | Massive overkill. Cadenza has no database, no ORM, no admin panel. |
| **attrs** | Pydantic v2 subsumes attrs for validated data models, and integrates with FastAPI |
| **Named tuples (raw)** | No validation, no serialization support, no FastAPI integration |
| **Plain dataclasses** | No validation. `dataclasses` are fine for internal-only types but not for the API boundary. |
| **partitura** | Academic library with scipy/numpy deps. Cadenza's lxml-based MusicXML is lighter and more controlled. |
| **Music21 as runtime dep** | Too heavy, too slow, mutable model. Use as test oracle only. |

---

## Sources and Confidence Notes

All recommendations are based on training data with a cutoff of May 2025. The following need verification before implementation:

1. **FastAPI version:** Verify current stable version on PyPI. FastAPI was still on 0.x versioning; check if 1.0 has been released.
2. **uv version and stability:** uv was rapidly evolving. Confirm current version and that lock file format is stable.
3. **Dorico Remote Control API:** Verify current protocol details from Steinberg documentation. Confirm whether Python scripting has been added in Dorico 6 (if released).
4. **Sibelius REST plugin API:** Check Avid documentation for any newer integration mechanisms.
5. **lxml version:** Confirm 5.x is current stable.
6. **Music21 version:** Confirm 9.x is current. Check for any breaking changes.
7. **Lark version:** Confirm 1.2+ is current.
8. **Python version:** 3.13 may be stable by now. Verify 3.12+ is the right minimum.

**Overall stack confidence: HIGH** -- These are well-established libraries in the Python ecosystem. The main uncertainty is exact version numbers and whether any major new releases have occurred since May 2025.
