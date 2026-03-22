# Phase 12: I/O Expansion - Research

**Researched:** 2026-03-22
**Domain:** MusicXML and MIDI file import/export
**Confidence:** HIGH

## Summary

Phase 12 adds four I/O functions: MusicXML import/export and MIDI import/export. The project has a strict zero-runtime-dependency policy for the core library, which means MusicXML handling MUST use Python's stdlib `xml.etree.ElementTree` (not lxml). MIDI handling requires the third-party `mido` library (v1.3.3), which should be added as a new optional dependency group `[io]` following the pattern established by `[api]` for FastAPI.

The existing codebase provides strong foundations: `from_midi()` for pitch conversion, `Duration.from_cn()` for grid parsing, `Score.from_dict()` for multi-voice assembly, and the `ParseWarning` frozen dataclass pattern for the new `ImportWarning` type. The CN duration system uses fractions of a whole note (`Fraction(1,4)` = quarter), while MusicXML uses divisions-per-quarter-note integers and MIDI uses ticks-per-beat. Correct conversion between these three duration representations is the central technical challenge.

**Primary recommendation:** Use `xml.etree.ElementTree` for MusicXML (zero deps), `mido` as optional `[io]` dependency for MIDI, and implement a shared duration conversion utility that maps between Cadenza's `Fraction`-based durations and both MusicXML divisions and MIDI ticks.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Single-part import returns `Phrase`, multi-part returns `Score`. One function per format: `import_musicxml(path) -> tuple[Phrase | Score, list[ImportWarning]]`
- Tied notes are merged into one `Note` with summed `Duration`
- Export: `export_musicxml(phrase_or_score, path) -> None` and `export_midi(phrase_or_score, path, tempo=120) -> None`
- Caller-specified quantization grid: `import_midi(path, grid='16') -> tuple[Phrase | Score, list[ImportWarning]]`
- Multi-track MIDI maps to `Score` with one `Phrase` per track
- Off-grid notes snap to nearest grid position (nearest-neighbor quantization)
- Fixed 8-level dynamic-to-velocity mapping (ppp=16 through fff=127), hardcoded not configurable
- `dynamic=None` exports as velocity 64
- MIDI import prefers flats by default, `prefer_sharps=True` override
- `ImportWarning` is a frozen dataclass with `element`, `position`, `message` fields
- All import functions return `(Phrase | Score, list[ImportWarning])`
- Export raises `ValueError` on unmappable content
- New module: `src/cadenza/io/` package

### Claude's Discretion
- MusicXML library: whether to use `lxml`, `xml.etree.ElementTree`, or another XML library
- MIDI library: roadmap suggests `mido`; confirm availability
- MusicXML export measure structure: fixed duration measures (e.g., 4/4) or single measure containing entire phrase
- Score voice naming in MIDI import: when track names absent, use `'track_0'`, `'track_1'`, etc.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| NOTA-08 | System imports MusicXML files into internal representation | MusicXML partwise format parsing via xml.etree.ElementTree; pitch/step/alter/octave mapping to Pitch; divisions-based duration conversion to Duration fractions; tied note merging; dynamics from direction elements; articulations from notations elements |
| NOTA-09 | System exports internal representation to MusicXML | Generate score-partwise XML with 4/4 measures; convert Duration fractions to divisions-based integers; map dynamics to direction elements; map articulations to notations/articulations elements |
| NOTA-10 | System imports MIDI files into internal representation | mido.MidiFile parsing; tick-to-duration conversion using ticks_per_beat; note_on/note_off pairing; velocity-to-dynamic mapping; nearest-grid quantization; from_midi() for pitch conversion |
| NOTA-11 | System exports internal representation to MIDI | mido.MidiFile creation; Duration fraction to tick conversion; dynamic-to-velocity mapping; tempo meta message; Pitch.midi_number for note events |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| xml.etree.ElementTree | stdlib | MusicXML parsing and generation | Zero external dependencies; adequate for MusicXML file sizes; API-compatible subset of lxml |
| mido | 1.3.3 | MIDI file reading and writing | De facto Python MIDI library; clean API for messages and tracks; MIT licensed; no heavy dependencies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| fractions.Fraction | stdlib | Duration arithmetic | Already used throughout Cadenza core; critical for lossless duration conversion |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| xml.etree.ElementTree | lxml 6.0.2 | lxml is 20x faster but adds C dependency; MusicXML files are small (KB-MB), so performance gain is negligible; would violate zero-dep core policy |
| mido | python-midi, pretty_midi | mido has cleaner API, better maintenance, wider adoption; pretty_midi pulls in numpy |

### Discretion Decisions

**MusicXML library: `xml.etree.ElementTree`** -- The project has a zero-runtime-dependency core policy (`dependencies = []` in pyproject.toml). lxml would add a C extension dependency. MusicXML files are small enough that stdlib XML performance is adequate. The `xml.etree.ElementTree` API covers all needed operations: `ET.parse()`, `ET.SubElement()`, `tree.write()`, XPath-like `findall()`.

**MIDI library: `mido`** -- Confirmed available on PyPI as v1.3.3 (October 2024). Add as optional dependency: `io = ["mido>=1.3,<2.0"]`. Import guard pattern: `try: import mido except ImportError: raise ImportError("Install cadenza[io] for MIDI support")`.

**MusicXML export measure structure: 4/4 measures** -- Export in 4/4 time with proper measure boundaries. This produces valid, idiomatic MusicXML that Dorico and Sibelius import cleanly. Notes spanning measure boundaries should be tied across measures. Use `divisions=4` (4 divisions per quarter note) to cleanly represent all standard durations down to sixteenth notes; use `divisions=48` if triplet support is needed (LCM of 4 and 3 = 12; 48 = 12*4 gives clean integers for all standard durations including triplets).

**MIDI track naming: `'track_0'`, `'track_1'`** -- When MIDI track metadata lacks a name, fall back to `'track_0'`, `'track_1'`, etc. This is consistent with the `'voice_0'`, `'voice_1'` pattern used elsewhere in the codebase.

**Installation:**
```bash
pip install mido>=1.3,<2.0
# Or via optional extra:
pip install cadenza[io]
```

## Architecture Patterns

### Recommended Project Structure
```
src/cadenza/io/
    __init__.py          # Re-exports: import_musicxml, export_musicxml, import_midi, export_midi, ImportWarning
    _warnings.py         # ImportWarning frozen dataclass
    _duration_conv.py    # Shared duration conversion utilities (fraction <-> divisions, fraction <-> ticks)
    _dynamics_map.py     # Dynamic <-> velocity mapping constants and lookup functions
    musicxml.py          # import_musicxml(), export_musicxml()
    midi.py              # import_midi(), export_midi()

tests/io/
    __init__.py
    conftest.py          # Shared fixtures: sample MusicXML strings, MIDI bytes
    test_musicxml_import.py
    test_musicxml_export.py
    test_midi_import.py
    test_midi_export.py
    test_roundtrip.py    # Export-then-import produces same data
    fixtures/            # Sample .musicxml and .mid files for integration tests
```

### Pattern 1: Duration Conversion (Fraction <-> MusicXML Divisions)
**What:** Convert between Cadenza's `Duration.fraction` (fraction of whole note) and MusicXML's integer duration (divisions per quarter note).
**When to use:** Every note import/export in MusicXML.
**Example:**
```python
# Cadenza Duration.fraction is fraction-of-whole-note
# MusicXML duration is integer: duration_value / divisions = quarter notes
# So: fraction_of_whole = (mxml_duration / divisions) / 4
#     mxml_duration = fraction_of_whole * 4 * divisions

def fraction_to_mxml_duration(frac: Fraction, divisions: int) -> int:
    """Convert Duration.fraction to MusicXML integer duration."""
    # fraction is in whole notes; multiply by 4 to get quarter notes, then by divisions
    result = frac * 4 * divisions
    if result.denominator != 1:
        raise ValueError(f"Duration {frac} not representable with divisions={divisions}")
    return int(result)

def mxml_duration_to_fraction(mxml_dur: int, divisions: int) -> Fraction:
    """Convert MusicXML integer duration to Duration.fraction."""
    # mxml_dur / divisions = quarter notes; divide by 4 for whole notes
    return Fraction(mxml_dur, divisions * 4)
```

### Pattern 2: Duration Conversion (Fraction <-> MIDI Ticks)
**What:** Convert between Cadenza's `Duration.fraction` and MIDI ticks.
**When to use:** Every note import/export in MIDI.
**Example:**
```python
def fraction_to_ticks(frac: Fraction, ticks_per_beat: int) -> int:
    """Convert Duration.fraction to MIDI ticks."""
    # fraction is whole notes; quarter = 1/4 whole = ticks_per_beat ticks
    result = frac * 4 * ticks_per_beat
    if result.denominator != 1:
        raise ValueError(f"Duration {frac} not representable at {ticks_per_beat} tpb")
    return int(result)

def ticks_to_fraction(ticks: int, ticks_per_beat: int) -> Fraction:
    """Convert MIDI ticks to Duration.fraction."""
    return Fraction(ticks, ticks_per_beat * 4)
```

### Pattern 3: Note-On/Note-Off Pairing for MIDI Import
**What:** Match `note_on` events with their corresponding `note_off` (or `note_on` with velocity=0) to compute note durations.
**When to use:** MIDI import.
**Example:**
```python
# Track absolute tick positions, pair note_on with note_off by pitch
active_notes: dict[int, tuple[int, int]]  # midi_number -> (start_tick, velocity)
abs_tick = 0
for msg in track:
    abs_tick += msg.time  # delta time
    if msg.type == 'note_on' and msg.velocity > 0:
        active_notes[msg.note] = (abs_tick, msg.velocity)
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in active_notes:
            start, vel = active_notes.pop(msg.note)
            duration_ticks = abs_tick - start
            # Convert to Note with quantized duration
```

### Pattern 4: Tied Note Merging for MusicXML Import
**What:** Consecutive notes with `<tie type="start"/>` and `<tie type="stop"/>` are merged into a single `Note` with summed duration.
**When to use:** MusicXML import.
**Example:**
```python
# During import, track tie state
# When a note has <tie type="start">, mark it as tie-start
# When next note has <tie type="stop"> and same pitch, merge:
#   merged_duration = Duration(fraction=note1.duration.fraction + note2.duration.fraction)
# If a note has both start and stop (middle of chain), continue accumulating
```

### Pattern 5: Import Guard for Optional Dependencies
**What:** Lazy import with helpful error message.
**When to use:** MIDI functions that need mido.
**Example:**
```python
def _require_mido():
    try:
        import mido
        return mido
    except ImportError:
        raise ImportError(
            "mido is required for MIDI I/O. Install with: pip install cadenza[io]"
        ) from None
```

### Anti-Patterns to Avoid
- **Floating-point duration arithmetic:** Never convert `Fraction` to `float` for tick/division math. Use `Fraction` throughout and convert to `int` only at the final step.
- **Parsing MusicXML with regex:** Use `xml.etree.ElementTree` tree walking. MusicXML is deeply nested XML; regex will break.
- **Assuming MIDI note_off exists:** Some MIDI files use `note_on` with `velocity=0` instead of `note_off`. Always handle both.
- **Ignoring MusicXML `<alter>` element:** The `<step>` alone does not determine pitch. Must read `<alter>` for sharps/flats.
- **Hardcoding divisions=1:** Different MusicXML files use different divisions values. Always read from `<divisions>` element.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MIDI file binary format | Custom binary MIDI parser/writer | `mido.MidiFile` | MIDI binary format has variable-length quantities, running status, meta events; extremely error-prone to parse manually |
| XML parsing/generation | String concatenation or regex | `xml.etree.ElementTree` | XML escaping, namespace handling, encoding declarations all handled correctly |
| Tempo conversion | Manual BPM-to-microseconds math | `mido.bpm2tempo()` / `mido.tempo2bpm()` | Standard conversion; avoids off-by-one in microsecond math |
| Duration quantization | New quantization algorithm | Adapt existing `cadenza.transforms.rhythm.quantize` pattern | Nearest-grid snapping already proven; reuse the fraction-comparison logic |

**Key insight:** The hard parts of I/O are format parsing (binary MIDI, nested XML) and duration arithmetic (three different representations). Libraries handle the former; `Fraction` handles the latter. The domain logic (mapping pitches, dynamics, articulations) is straightforward table lookups.

## Common Pitfalls

### Pitfall 1: MusicXML Divisions Vary Per Part and Per Measure
**What goes wrong:** Assuming a single global `divisions` value. Different parts or even different measures can declare new `<divisions>` values.
**Why it happens:** The `<divisions>` element appears inside `<attributes>`, which can appear in any measure.
**How to avoid:** Track the current divisions value per part. Update it whenever a new `<attributes><divisions>` is encountered.
**Warning signs:** Durations that are wildly wrong for some measures but correct for others.

### Pitfall 2: MusicXML Pitch Alter Values
**What goes wrong:** Ignoring the `<alter>` element and treating all pitches as natural.
**Why it happens:** `<alter>` is optional (omitted for natural notes). Easy to forget when it is present.
**How to avoid:** Default `alter=0`, then check for `<alter>` child element. Map: -2=bb, -1=b, 0=n, 1=s, 2=ss.
**Warning signs:** All imported pitches are natural (no sharps or flats).

### Pitfall 3: MIDI Running Status and Velocity-Zero Note-Off
**What goes wrong:** Missing note-off events, causing notes with infinite duration.
**Why it happens:** Many MIDI files use `note_on` with `velocity=0` as a de facto `note_off`. Some use running status (omitting repeated message types).
**How to avoid:** mido handles running status parsing. In your note pairing, treat `note_on` with `velocity=0` as `note_off`.
**Warning signs:** Extremely long notes or hanging notes in import output.

### Pitfall 4: Duration Fraction Precision Loss
**What goes wrong:** A `Duration` with fraction `Fraction(1,6)` (triplet quarter) cannot be cleanly represented with divisions=4 in MusicXML.
**Why it happens:** The chosen divisions value does not have the required prime factors.
**How to avoid:** For export, compute divisions as LCM of all duration denominators multiplied by 4. For example, if any triplets exist, use divisions=12 (or 48 for finer resolution). Raise `ValueError` if a duration truly cannot be represented.
**Warning signs:** `fraction_to_mxml_duration` returning non-integer results.

### Pitfall 5: MusicXML Tie Chains
**What goes wrong:** Only merging pairs of tied notes, missing chains of 3+ tied notes.
**Why it happens:** A note can have both `<tie type="stop"/>` AND `<tie type="start"/>` (middle of a chain).
**How to avoid:** Use an accumulator pattern: when a note has `tie type="start"`, begin accumulating duration. Continue accumulating while notes have `tie type="stop"` AND `tie type="start"`. Emit the merged note only when `tie type="stop"` without a corresponding `tie type="start"`.
**Warning signs:** Some tied notes are merged but others produce two separate notes.

### Pitfall 6: MIDI Track 0 as Tempo/Meta Track
**What goes wrong:** Treating MIDI track 0 as containing musical notes in a Type 1 file.
**Why it happens:** In Type 1 MIDI files, track 0 is conventionally the tempo/conductor track containing only meta events (tempo, time signature, etc.), not note data.
**How to avoid:** For Type 1 files, check if a track contains any note events before creating a voice. Skip tempo-only tracks or extract tempo from track 0 for use across all voices.
**Warning signs:** An empty voice appearing in the imported Score.

## Code Examples

### MusicXML Import: Parsing a Note Element
```python
# Source: MusicXML 4.0 spec + Cadenza core types
import xml.etree.ElementTree as ET
from fractions import Fraction
from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note

ALTER_TO_ACCIDENTAL = {-2: "bb", -1: "b", 0: "n", 1: "s", 2: "ss"}

def _parse_mxml_note(note_elem: ET.Element, divisions: int) -> Note | None:
    """Parse a single MusicXML <note> element into a Cadenza Note."""
    # Check for rest
    if note_elem.find("rest") is not None:
        dur_val = int(note_elem.findtext("duration", "0"))
        frac = Fraction(dur_val, divisions * 4)
        return None  # Would return Rest instead

    # Parse pitch
    pitch_elem = note_elem.find("pitch")
    if pitch_elem is None:
        return None
    step = pitch_elem.findtext("step", "C").lower()
    alter = int(float(pitch_elem.findtext("alter", "0")))
    octave = int(pitch_elem.findtext("octave", "4"))
    accidental = ALTER_TO_ACCIDENTAL.get(alter, "n")
    pitch = Pitch(step=step, accidental=accidental, octave=octave)

    # Parse duration
    dur_val = int(note_elem.findtext("duration", "0"))
    frac = Fraction(dur_val, divisions * 4)
    # Find best CN base for this fraction
    duration = _fraction_to_duration(frac)

    return Note(pitch=pitch, duration=duration)
```

### MusicXML Export: Building a Note Element
```python
import xml.etree.ElementTree as ET
from cadenza.core.note import Note

ACCIDENTAL_TO_ALTER = {"bb": -2, "b": -1, "n": 0, "s": 1, "ss": 2}

def _build_mxml_note(note: Note, divisions: int) -> ET.Element:
    """Build a MusicXML <note> element from a Cadenza Note."""
    note_elem = ET.Element("note")

    # Pitch
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = note.pitch.step.upper()
    alter = ACCIDENTAL_TO_ALTER[note.pitch.accidental]
    if alter != 0:
        ET.SubElement(pitch_elem, "alter").text = str(alter)
    ET.SubElement(pitch_elem, "octave").text = str(note.pitch.octave)

    # Duration
    dur_val = int(note.duration.fraction * 4 * divisions)
    ET.SubElement(note_elem, "duration").text = str(dur_val)

    # Type (whole, half, quarter, eighth, 16th, 32nd, 64th)
    type_name = _fraction_to_type_name(note.duration)
    if type_name:
        ET.SubElement(note_elem, "type").text = type_name

    return note_elem
```

### MIDI Import: Core Loop
```python
# Source: mido docs + Cadenza core types
def _import_midi_track(track, ticks_per_beat: int, grid_fraction: Fraction,
                       prefer_sharps: bool) -> list[tuple[int, Note]]:
    """Import a MIDI track into (absolute_tick, Note) pairs."""
    from cadenza.transforms.pitch import from_midi

    active: dict[int, tuple[int, int]] = {}  # midi_note -> (start_tick, velocity)
    notes: list[tuple[int, Note]] = []
    abs_tick = 0

    for msg in track:
        abs_tick += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            active[msg.note] = (abs_tick, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active:
                start, vel = active.pop(msg.note)
                dur_ticks = abs_tick - start
                dur_frac = Fraction(dur_ticks, ticks_per_beat * 4)
                # Quantize to grid
                quantized = _snap_to_grid(dur_frac, grid_fraction)
                pitch = from_midi(msg.note, prefer_sharps=prefer_sharps)
                dynamic = _velocity_to_dynamic(vel)
                duration = _fraction_to_duration(quantized)
                notes.append((start, Note(pitch=pitch, duration=duration, dynamic=dynamic)))

    return notes
```

### Dynamic-Velocity Mapping Table
```python
# Module-level constant in _dynamics_map.py
DYNAMIC_TO_VELOCITY: dict[str, int] = {
    "ppp": 16, "pp": 33, "p": 49, "mp": 64,
    "mf": 80, "f": 96, "ff": 112, "fff": 127,
}

# Velocity ranges for import (upper bound inclusive)
VELOCITY_RANGES: list[tuple[range, str]] = [
    (range(1, 25), "ppp"),
    (range(25, 41), "pp"),
    (range(41, 57), "p"),
    (range(57, 73), "mp"),
    (range(73, 89), "mf"),
    (range(89, 105), "f"),
    (range(105, 120), "ff"),
    (range(120, 128), "fff"),
]

def velocity_to_dynamic(velocity: int) -> str:
    """Convert MIDI velocity (1-127) to dynamic string."""
    for vel_range, dynamic in VELOCITY_RANGES:
        if velocity in vel_range:
            return dynamic
    return "mf"  # fallback for velocity 0

def dynamic_to_velocity(dynamic: str | None) -> int:
    """Convert dynamic string to MIDI velocity."""
    if dynamic is None:
        return 64
    return DYNAMIC_TO_VELOCITY.get(dynamic, 64)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MusicXML 3.1 | MusicXML 4.0 | 2021 | Minor schema updates; 4.0 is W3C Community Group standard |
| Custom MIDI parsers | mido 1.3.x | Stable since 2022 | Clean message-based API; handles running status |
| lxml required for XML | xml.etree.ElementTree sufficient | Always | For file sizes under 10MB, stdlib is adequate |

**Deprecated/outdated:**
- MusicXML 2.0: Still widely exported by older software but 4.0 is backward-compatible
- python-midi: Unmaintained; use mido instead

## Mapping Tables

### Cadenza Accidental <-> MusicXML Alter
| Cadenza accidental | MusicXML alter | MusicXML accidental element |
|--------------------|----------------|-----------------------------|
| `"bb"` | `-2` | `double-flat` |
| `"b"` | `-1` | `flat` |
| `"n"` | `0` (or omitted) | `natural` (or omitted) |
| `"s"` | `1` | `sharp` |
| `"ss"` | `2` | `double-sharp` |

### Cadenza Duration Base <-> MusicXML Type Name
| CN base | Duration.fraction | MusicXML type |
|---------|-------------------|---------------|
| `"w"` | `1/1` | `whole` |
| `"h"` | `1/2` | `half` |
| `"q"` | `1/4` | `quarter` |
| `"e"` | `1/8` | `eighth` |
| `"s"` | `1/16` | `16th` |
| `"t"` | `1/32` | `32nd` |
| `"x"` | `1/64` | `64th` |

### Cadenza Articulation <-> MusicXML Articulation Element
| Cadenza articulation | MusicXML element |
|----------------------|------------------|
| `"stacc"` | `<staccato/>` |
| `"ten"` | `<tenuto/>` |
| `"accent"` | `<accent/>` |
| `"marc"` | `<strong-accent/>` |
| `"legato"` | `<detached-legato/>` |
| `"fermata"` | `<fermata/>` (under `<notations>`, not `<articulations>`) |
| `"trill"` | `<trill-mark/>` (under `<ornaments>`, not `<articulations>`) |

Note: `fermata` and `trill` are under different MusicXML parent elements than standard articulations. This mapping must account for the structural difference.

## Open Questions

1. **Divisions value for export**
   - What we know: divisions must be an integer that cleanly divides all note durations in the piece. Using `divisions=4` handles standard durations. Triplets need a multiple of 3.
   - What's unclear: Whether to use a fixed value (e.g., 48) or dynamically compute LCM of all duration denominators.
   - Recommendation: Dynamically compute. Scan all durations, collect denominators, compute LCM, multiply by 4. This handles all cases without wasting precision.

2. **MusicXML articulation name mapping completeness**
   - What we know: The Cadenza articulation vocabulary (from NOTA-07) includes stacc, ten, accent, legato, marc, fermata, trill, and others.
   - What's unclear: Exact mapping for all Cadenza articulations to MusicXML elements. Some may not have direct MusicXML equivalents.
   - Recommendation: Map the core set above. Unsupported articulations in import generate `ImportWarning`. Unmappable articulations in export are silently omitted (or generate a warning if strict mode is desired).

3. **Rest gaps in MIDI import**
   - What we know: MIDI has no "rest" concept; silence is just time between note_off and next note_on.
   - What's unclear: How to handle gaps -- insert Rest events or ignore gaps.
   - Recommendation: Insert Rest events for gaps between notes. This preserves rhythmic fidelity. Quantize rest durations to the same grid as note durations.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | `pyproject.toml [tool.pytest.ini_options]` |
| Quick run command | `python3 -m pytest tests/io/ -x -q` |
| Full suite command | `python3 -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NOTA-08 | MusicXML import: pitches, durations, dynamics, articulations preserved | unit + integration | `python3 -m pytest tests/io/test_musicxml_import.py -x` | Wave 0 |
| NOTA-08 | MusicXML import: tied note merging | unit | `python3 -m pytest tests/io/test_musicxml_import.py::test_tied_notes -x` | Wave 0 |
| NOTA-08 | MusicXML import: multi-part -> Score | unit | `python3 -m pytest tests/io/test_musicxml_import.py::test_multipart -x` | Wave 0 |
| NOTA-08 | MusicXML import: unsupported elements -> warnings | unit | `python3 -m pytest tests/io/test_musicxml_import.py::test_warnings -x` | Wave 0 |
| NOTA-09 | MusicXML export: Phrase produces valid XML | unit + integration | `python3 -m pytest tests/io/test_musicxml_export.py -x` | Wave 0 |
| NOTA-09 | MusicXML export: Score produces multi-part XML | unit | `python3 -m pytest tests/io/test_musicxml_export.py::test_score_export -x` | Wave 0 |
| NOTA-09 | MusicXML roundtrip: export then import preserves data | integration | `python3 -m pytest tests/io/test_roundtrip.py::test_musicxml_roundtrip -x` | Wave 0 |
| NOTA-10 | MIDI import: pitches and durations from note events | unit | `python3 -m pytest tests/io/test_midi_import.py -x` | Wave 0 |
| NOTA-10 | MIDI import: quantization to specified grid | unit | `python3 -m pytest tests/io/test_midi_import.py::test_quantization -x` | Wave 0 |
| NOTA-10 | MIDI import: velocity -> dynamic mapping | unit | `python3 -m pytest tests/io/test_midi_import.py::test_velocity_mapping -x` | Wave 0 |
| NOTA-10 | MIDI import: multi-track -> Score | unit | `python3 -m pytest tests/io/test_midi_import.py::test_multitrack -x` | Wave 0 |
| NOTA-11 | MIDI export: note_on/off with correct velocities | unit | `python3 -m pytest tests/io/test_midi_export.py -x` | Wave 0 |
| NOTA-11 | MIDI export: tempo metadata | unit | `python3 -m pytest tests/io/test_midi_export.py::test_tempo -x` | Wave 0 |
| NOTA-11 | MIDI roundtrip: export then import preserves data | integration | `python3 -m pytest tests/io/test_roundtrip.py::test_midi_roundtrip -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/io/ -x -q`
- **Per wave merge:** `python3 -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/io/__init__.py` -- package init
- [ ] `tests/io/conftest.py` -- shared fixtures (sample MusicXML strings, helper to create mido MidiFile objects in memory)
- [ ] `tests/io/test_musicxml_import.py` -- covers NOTA-08
- [ ] `tests/io/test_musicxml_export.py` -- covers NOTA-09
- [ ] `tests/io/test_midi_import.py` -- covers NOTA-10
- [ ] `tests/io/test_midi_export.py` -- covers NOTA-11
- [ ] `tests/io/test_roundtrip.py` -- covers roundtrip for both formats
- [ ] `mido` dependency added to `pyproject.toml` `[project.optional-dependencies]` as `io` group

## Sources

### Primary (HIGH confidence)
- [MusicXML 4.0 Tutorial: Hello World](https://www.w3.org/2021/06/musicxml40/tutorial/hello-world/) -- XML structure, divisions, note elements
- [MusicXML 4.0 Tutorial: Notation Basics](https://www.w3.org/2021/06/musicxml40/tutorial/notation-basics/) -- ties, dynamics, articulations
- [MusicXML 4.0: divisions element](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/divisions/) -- duration system
- [MusicXML 4.0: alter element](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/alter/) -- accidental encoding
- [MusicXML 4.0: articulations element](https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-articulations.htm) -- articulation child elements
- [Mido Documentation: MIDI Files](https://mido.readthedocs.io/en/stable/files/midi.html) -- MidiFile API, tracks, messages, ticks
- [Mido on PyPI](https://pypi.org/project/mido/) -- version 1.3.3, Python 3.7+

### Secondary (MEDIUM confidence)
- [lxml Performance Benchmarks](https://lxml.de/performance.html) -- verified stdlib is adequate for small files
- [Twilio: Working with MIDI in Python using Mido](https://www.twilio.com/en-us/blog/developers/tutorials/building-blocks/working-with-midi-data-in-python-using-mido) -- practical mido patterns

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- stdlib xml.etree is verified available; mido 1.3.3 confirmed on PyPI; zero-dep constraint clearly met
- Architecture: HIGH -- patterns derived from existing codebase (ParseWarning, Score.from_dict, from_midi) and official MusicXML/MIDI specs
- Pitfalls: HIGH -- based on MusicXML spec details (divisions, alter, ties) and well-documented MIDI quirks (velocity-zero note-off)
- Mapping tables: MEDIUM -- articulation mapping needs validation against actual Dorico/Sibelius MusicXML exports

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable domain, specs do not change frequently)
