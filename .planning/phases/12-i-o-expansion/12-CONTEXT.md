# Phase 12: I/O Expansion - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 12 delivers four import/export capabilities:

1. **MusicXML import (NOTA-08)** — parse a MusicXML file into Cadenza's internal representation.
2. **MusicXML export (NOTA-09)** — serialize a `Phrase` or `Score` to a MusicXML file.
3. **MIDI import (NOTA-10)** — parse a MIDI file into Cadenza's internal representation, with quantization.
4. **MIDI export (NOTA-11)** — serialize a `Phrase` or `Score` to a MIDI file with velocity and tempo.

New module: `src/cadenza/io/` package. Depends on Phase 1 (`Pitch`, `Note`, `Rest`, `Duration`, `Phrase`, `Score`).

</domain>

<decisions>
## Implementation Decisions

### Area 1: MusicXML Fidelity & Scope

- **Single-part import → `Phrase`** — bar lines dropped, measure structure is display metadata. All events flattened to a single `tuple[Event, ...]`.
- **Multi-part import → `Score`** — one named `Phrase` per `<part>`, part names from MusicXML `<part-name>` metadata.
- **One function: `import_musicxml(path) -> tuple[Phrase | Score, list[ImportWarning]]`** — returns `Phrase` for single-part, `Score` for multi-part. Caller checks type.
- **Tied notes are merged** — a tie is a duration extension, not a separate event. Consecutive tied notes collapse into one `Note` with the summed `Duration`.
- **Export: `export_musicxml(phrase_or_score, path) -> None`** — accepts both `Phrase` and `Score`.

### Area 2: MIDI Quantization

- **Caller-specified grid: `import_midi(path, grid='16') -> tuple[Phrase | Score, list[ImportWarning]]`** — `grid` is a CN duration string (`'4'`=quarter, `'8'`=eighth, `'16'`=sixteenth). Default `'16'` (sixteenth note).
- **Multi-track MIDI → `Score`** — one named `Phrase` per MIDI track; track names from MIDI metadata become voice names.
- **Off-grid notes snap to nearest grid position** — standard nearest-neighbor quantization. A note at tick 90 on a 96-tick grid snaps to tick 96.
- **Export: `export_midi(phrase_or_score, path, tempo=120) -> None`** — `tempo` is BPM integer, default 120.

### Area 3: Dynamic ↔ Velocity Mapping

- **Fixed standard 7-level mapping (hardcoded, not configurable):**

  | Dynamic | Export velocity | Import velocity range |
  |---------|----------------|-----------------------|
  | `'ppp'` | 16 | 1–24 |
  | `'pp'`  | 33 | 25–40 |
  | `'p'`   | 49 | 41–56 |
  | `'mp'`  | 64 | 57–72 |
  | `'mf'`  | 80 | 73–88 |
  | `'f'`   | 96 | 89–104 |
  | `'ff'`  | 112 | 105–119 |
  | `'fff'` | 127 | 120–127 |

- **`dynamic=None` exports as velocity 64** (MIDI default, neutral mezzo).
- **MIDI import prefers flats by default** — `Pitch` spelling uses flat accidentals (Eb not D#); caller can pass `prefer_sharps=True` to override.
- **Round-trip safe** — export then import produces the same dynamic string.

### Area 4: Unsupported Element Handling

- **Skip with warnings** — `ImportWarning` is a new frozen dataclass:
  ```python
  @dataclass(frozen=True, slots=True)
  class ImportWarning:
      element: str    # element type, e.g. 'grace-note', 'ornament', 'chord'
      position: str   # XPath for MusicXML ('part[1]/measure[3]/note[2]') or tick string for MIDI
      message: str    # human-readable description of what was skipped
  ```
- **All import functions return `(Phrase | Score, list[ImportWarning])`** — consistent regardless of single vs multi-part. Empty list = no warnings.
- **Mirrors `parse_cn()` pattern** — `parse_cn` already returns `tuple[Phrase, list[ParseWarning]]`; import functions use the same contract.
- **Export raises `ValueError` on unmappable content** — e.g., a `Duration` with a prime-number tuplet ratio that can't be expressed in standard MusicXML notation. Explicit failure prevents silent data corruption.

### Claude's Discretion

- **MusicXML library** — whether to use `lxml`, `xml.etree.ElementTree`, or another XML library for parsing/writing. The roadmap suggests `lxml`; planner should confirm this is available in the project's dependencies.
- **MIDI library** — the roadmap suggests `mido`; planner confirms availability.
- **MusicXML export measure structure** — whether to emit measures of a fixed duration (e.g., 4/4) or one measure containing the entire phrase. Choose whatever produces valid, importable MusicXML in Dorico/Sibelius.
- **Score voice naming in MIDI import** — when MIDI track names are absent, use `'track_0'`, `'track_1'`, etc. (consistent with `'voice_0'`, `'voice_1'` from Phase 8/10).

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

### Phase requirements
- `.planning/REQUIREMENTS.md` — NOTA-08 through NOTA-11

### Prior phase patterns to follow
- `src/cadenza/cn/parser.py` — `parse_cn(source) -> tuple[Phrase, list[ParseWarning]]` — direct model for `(result, warnings)` return pattern
- `src/cadenza/cn/serializer.py` — `to_cn(phrase) -> str` — model for export function style
- `src/cadenza/core/note.py` — `Note(pitch, duration, dynamic, articulations)` — fields preserved/mapped in both formats
- `src/cadenza/core/pitch.py` — `Pitch.midi_number` — used in MIDI export; `prefer_sharps` param in `from_midi` — used in MIDI import
- `src/cadenza/transforms/pitch.py` — `from_midi(midi_number, prefer_sharps=True)` — builds `Pitch` from MIDI note number
- `src/cadenza/core/score.py` — `Score` return type for multi-part/multi-track import

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cadenza.cn.parser.ParseWarning` — reference dataclass for `ImportWarning` structure; `ImportWarning` should use the same frozen dataclass pattern
- `cadenza.transforms.pitch.from_midi(midi_number, prefer_sharps)` — converts MIDI note number to `Pitch`; central to MIDI import
- `cadenza.core.pitch.Pitch.midi_number` — converts `Pitch` to MIDI note number; central to MIDI export
- `cadenza.core.duration.Duration.from_cn(string)` — builds `Duration` from CN base string (e.g., `'16'`); used for quantization grid
- `cadenza.core.score.Score` — `_voices: tuple[tuple[str, Phrase], ...]`; return type for multi-part/track imports
- `cadenza.transforms.rhythm.quantize` — already implements nearest-grid snapping for `Phrase`; potentially reusable for MIDI import quantization

### Established Patterns
- Frozen dataclasses: `@dataclass(frozen=True, slots=True)` for `ImportWarning`
- `ValueError` for invalid export inputs (unmappable durations, malformed paths)
- Module-level constants for lookup tables (dynamic↔velocity map fits this pattern)
- Plain Python types for results (`tuple[Phrase | Score, list[ImportWarning]]`)

### Integration Points
- New module: `src/cadenza/io/` package with `musicxml.py` and `midi.py`
- `cadenza.__init__` re-exports need updating with `import_musicxml`, `export_musicxml`, `import_midi`, `export_midi`, `ImportWarning`
- Tests: `tests/io/` directory

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 12-i-o-expansion*
*Context gathered: 2026-03-22*
