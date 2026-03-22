"""MusicXML import and export."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

from cadenza.core.duration import Duration
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.io._duration_conv import (
    compute_divisions,
    fraction_to_best_duration,
    fraction_to_mxml_duration,
    mxml_duration_to_fraction,
)
from cadenza.io._warnings import ImportWarning

# --- Mapping tables (import) ---

ALTER_TO_ACCIDENTAL: dict[int, str] = {-2: "bb", -1: "b", 0: "n", 1: "s", 2: "ss"}

# MusicXML articulation element name -> Cadenza articulation string
MXML_ARTICULATION_MAP: dict[str, str] = {
    "staccato": "stacc",
    "tenuto": "ten",
    "accent": "accent",
    "strong-accent": "marc",
    "detached-legato": "legato",
}

# MusicXML dynamics element names we recognize
DYNAMIC_NAMES: frozenset[str] = frozenset(
    {"ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"}
)


# --- Import ---


def import_musicxml(
    path: str | Path,
) -> tuple[Phrase | Score, list[ImportWarning]]:
    """Import a MusicXML file into Cadenza representation.

    Single-part files return a Phrase; multi-part files return a Score.
    Unsupported elements produce ImportWarning objects (not exceptions).
    """
    tree = ET.parse(str(path))
    root = tree.getroot()

    warnings: list[ImportWarning] = []

    # Extract part names from part-list
    part_names: dict[str, str] = {}
    part_list = root.find("part-list")
    if part_list is not None:
        for sp in part_list.findall("score-part"):
            pid = sp.get("id", "")
            name_elem = sp.find("part-name")
            part_names[pid] = name_elem.text if name_elem is not None and name_elem.text else pid

    # Parse each part
    voices: dict[str, Phrase] = {}
    parts = root.findall("part")

    for part in parts:
        pid = part.get("id", "")
        voice_name = part_names.get(pid, pid)
        phrase = _parse_part(part, pid, warnings)
        voices[voice_name] = phrase

    if len(voices) == 1:
        return next(iter(voices.values())), warnings
    else:
        return Score.from_dict(voices), warnings


def _parse_part(
    part_elem: ET.Element, part_id: str, warnings: list[ImportWarning]
) -> Phrase:
    """Parse a single <part> element into a Phrase."""
    events: list[Event] = []
    divisions: int = 1
    current_dynamic: str | None = None

    # Tie accumulator
    tie_pitch: Pitch | None = None
    tie_duration: Fraction = Fraction(0)
    tie_dynamic: str | None = None
    tie_articulations: tuple[str, ...] = ()

    for measure_idx, measure in enumerate(part_elem.findall("measure")):
        # Check for divisions update in attributes
        attrs = measure.find("attributes")
        if attrs is not None:
            div_elem = attrs.find("divisions")
            if div_elem is not None and div_elem.text:
                divisions = int(div_elem.text)

        for child in measure:
            # Handle direction elements (dynamics)
            if child.tag == "direction":
                dyn = _parse_direction_dynamic(child)
                if dyn is not None:
                    current_dynamic = dyn
                continue

            if child.tag != "note":
                continue

            note_elem = child
            measure_num = measure.get("number", str(measure_idx + 1))

            # Skip grace notes
            if note_elem.find("grace") is not None:
                warnings.append(ImportWarning(
                    element="grace-note",
                    position=f"{part_id}/M{measure_num}",
                    message="Grace note skipped",
                ))
                continue

            # Skip chord notes (simultaneous)
            if note_elem.find("chord") is not None:
                warnings.append(ImportWarning(
                    element="chord",
                    position=f"{part_id}/M{measure_num}",
                    message="Chord note skipped (only single notes supported)",
                ))
                continue

            # Parse duration value
            dur_text = note_elem.findtext("duration")
            if dur_text is None:
                continue
            dur_val = int(dur_text)
            frac = mxml_duration_to_fraction(dur_val, divisions)

            # Check for rest
            if note_elem.find("rest") is not None:
                # Flush any pending tie
                if tie_pitch is not None:
                    events.append(_make_note(
                        tie_pitch, tie_duration, tie_dynamic, tie_articulations
                    ))
                    tie_pitch = None
                    tie_duration = Fraction(0)

                events.append(Rest(duration=fraction_to_best_duration(frac)))
                continue

            # Parse pitch
            pitch = _parse_pitch(note_elem)
            if pitch is None:
                continue

            # Parse articulations
            articulations = _parse_articulations(note_elem)

            # Parse tie information
            tie_types = _parse_tie_types(note_elem)
            has_start = "start" in tie_types
            has_stop = "stop" in tie_types

            if has_stop and tie_pitch is not None:
                # Continue or end a tie chain
                tie_duration += frac
                if has_start:
                    # Middle of chain: keep accumulating
                    continue
                else:
                    # End of chain: emit merged note
                    events.append(_make_note(
                        tie_pitch, tie_duration, tie_dynamic, tie_articulations
                    ))
                    tie_pitch = None
                    tie_duration = Fraction(0)
                    continue
            elif has_start:
                # Start of a new tie chain
                # Flush any previous incomplete tie first
                if tie_pitch is not None:
                    events.append(_make_note(
                        tie_pitch, tie_duration, tie_dynamic, tie_articulations
                    ))
                tie_pitch = pitch
                tie_duration = frac
                tie_dynamic = current_dynamic
                tie_articulations = articulations
                continue

            # Regular note (no tie)
            events.append(Note(
                pitch=pitch,
                duration=fraction_to_best_duration(frac),
                dynamic=current_dynamic,
                articulations=articulations,
            ))

    # Flush any remaining tie
    if tie_pitch is not None:
        events.append(_make_note(
            tie_pitch, tie_duration, tie_dynamic, tie_articulations
        ))

    return tuple(events)


def _make_note(
    pitch: Pitch, total_frac: Fraction, dynamic: str | None,
    articulations: tuple[str, ...]
) -> Note:
    """Create a Note from accumulated tie data."""
    return Note(
        pitch=pitch,
        duration=fraction_to_best_duration(total_frac),
        dynamic=dynamic,
        articulations=articulations,
    )


def _parse_pitch(note_elem: ET.Element) -> Pitch | None:
    """Parse pitch from a <note> element. Returns None if no pitch found."""
    pitch_elem = note_elem.find("pitch")
    if pitch_elem is None:
        return None
    step = (pitch_elem.findtext("step") or "C").lower()
    alter_text = pitch_elem.findtext("alter")
    alter = int(float(alter_text)) if alter_text else 0
    octave = int(pitch_elem.findtext("octave") or "4")
    accidental = ALTER_TO_ACCIDENTAL.get(alter, "n")
    return Pitch(step=step, accidental=accidental, octave=octave)


def _parse_tie_types(note_elem: ET.Element) -> set[str]:
    """Extract tie types from a <note> element."""
    types: set[str] = set()
    for tie in note_elem.findall("tie"):
        t = tie.get("type")
        if t:
            types.add(t)
    return types


def _parse_direction_dynamic(direction_elem: ET.Element) -> str | None:
    """Extract dynamic marking from a <direction> element."""
    for dt in direction_elem.findall("direction-type"):
        dyn_elem = dt.find("dynamics")
        if dyn_elem is not None:
            for child in dyn_elem:
                if child.tag in DYNAMIC_NAMES:
                    return child.tag
    return None


def _parse_articulations(note_elem: ET.Element) -> tuple[str, ...]:
    """Extract articulations from a <note> element's <notations>."""
    arts: list[str] = []
    for notations in note_elem.findall("notations"):
        # Standard articulations
        for art_group in notations.findall("articulations"):
            for child in art_group:
                mapped = MXML_ARTICULATION_MAP.get(child.tag)
                if mapped:
                    arts.append(mapped)
        # Fermata (directly under notations)
        if notations.find("fermata") is not None:
            arts.append("fermata")
        # Ornaments (trill)
        for orn_group in notations.findall("ornaments"):
            if orn_group.find("trill-mark") is not None:
                arts.append("trill")
    return tuple(arts)


# --- Export mapping tables ---

ACCIDENTAL_TO_ALTER: dict[str, int] = {"bb": -2, "b": -1, "n": 0, "s": 1, "ss": 2}

# Cadenza articulation -> MusicXML element name
CADENZA_ARTICULATION_MAP: dict[str, str] = {
    "stacc": "staccato",
    "ten": "tenuto",
    "accent": "accent",
    "marc": "strong-accent",
    "legato": "detached-legato",
}

# Fraction -> MusicXML type name
FRACTION_TO_TYPE: dict[Fraction, str] = {
    Fraction(1, 1): "whole",
    Fraction(1, 2): "half",
    Fraction(1, 4): "quarter",
    Fraction(1, 8): "eighth",
    Fraction(1, 16): "16th",
    Fraction(1, 32): "32nd",
    Fraction(1, 64): "64th",
}

# One whole note in 4/4
MEASURE_DURATION = Fraction(1, 1)


# --- Export ---


def export_musicxml(source: Phrase | Score, path: str | Path) -> None:
    """Export a Phrase or Score to a MusicXML file.

    Produces valid MusicXML 4.0 with 4/4 time signature. Notes spanning
    measure boundaries are tied across measures. Raises ValueError if any
    duration cannot be represented.
    """
    # Normalize to dict of voices
    if isinstance(source, Score):
        voices: dict[str, Phrase] = source.voices
    else:
        voices = {"Part 1": source}

    # Compute divisions from all events
    all_events = [e for phrase in voices.values() for e in phrase]
    divisions = compute_divisions(all_events)

    # Validate all durations are representable
    for event in all_events:
        fraction_to_mxml_duration(event.duration.fraction, divisions)

    # Build XML
    root = ET.Element("score-partwise", version="4.0")

    # Part list
    part_list = ET.SubElement(root, "part-list")
    voice_items = list(voices.items())
    for idx, (name, _) in enumerate(voice_items, 1):
        pid = f"P{idx}"
        sp = ET.SubElement(part_list, "score-part", id=pid)
        ET.SubElement(sp, "part-name").text = name

    # Parts
    for idx, (name, phrase) in enumerate(voice_items, 1):
        pid = f"P{idx}"
        _build_part(root, pid, phrase, divisions)

    # Write
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(str(path), encoding="unicode", xml_declaration=True)


def _build_part(
    root: ET.Element, part_id: str, phrase: Phrase, divisions: int
) -> None:
    """Build a <part> element with proper 4/4 measures."""
    part_elem = ET.SubElement(root, "part", id=part_id)

    # Split events into measures
    measures = _split_into_measures(phrase, divisions)

    for m_idx, measure_events in enumerate(measures, 1):
        measure = ET.SubElement(part_elem, "measure", number=str(m_idx))

        # Attributes in first measure
        if m_idx == 1:
            attrs = ET.SubElement(measure, "attributes")
            ET.SubElement(attrs, "divisions").text = str(divisions)
            time_elem = ET.SubElement(attrs, "time")
            ET.SubElement(time_elem, "beats").text = "4"
            ET.SubElement(time_elem, "beat-type").text = "4"

        prev_dynamic: str | None = None
        for item in measure_events:
            if isinstance(item, _TiedNote):
                # Emit dynamic direction if changed
                if item.note.dynamic is not None and item.note.dynamic != prev_dynamic:
                    _add_direction_dynamic(measure, item.note.dynamic)
                    prev_dynamic = item.note.dynamic
                _add_note_element(measure, item, divisions)
            elif isinstance(item, Rest):
                _add_rest_element(measure, item, divisions)


class _TiedNote:
    """Internal representation for a note that may be part of a tie."""

    __slots__ = ("note", "fraction", "tie_start", "tie_stop")

    def __init__(
        self, note: Note, fraction: Fraction,
        tie_start: bool = False, tie_stop: bool = False
    ):
        self.note = note
        self.fraction = fraction
        self.tie_start = tie_start
        self.tie_stop = tie_stop


def _split_into_measures(
    phrase: Phrase, divisions: int
) -> list[list[_TiedNote | Rest]]:
    """Split events into 4/4 measures, tying notes across boundaries."""
    measures: list[list[_TiedNote | Rest]] = [[]]
    remaining_in_measure = MEASURE_DURATION

    for event in phrase:
        if isinstance(event, Rest):
            frac = event.duration.fraction
            while frac > Fraction(0):
                if frac <= remaining_in_measure:
                    measures[-1].append(
                        Rest(duration=Duration(fraction=frac, base=event.duration.base))
                    )
                    remaining_in_measure -= frac
                    frac = Fraction(0)
                else:
                    # Rest spans measure boundary
                    measures[-1].append(
                        Rest(duration=Duration(fraction=remaining_in_measure, base="q"))
                    )
                    frac -= remaining_in_measure
                    remaining_in_measure = MEASURE_DURATION
                    measures.append([])
                if remaining_in_measure == Fraction(0):
                    remaining_in_measure = MEASURE_DURATION
                    measures.append([])
        elif isinstance(event, Note):
            frac = event.duration.fraction
            is_first = True
            while frac > Fraction(0):
                if frac <= remaining_in_measure:
                    tied_note = _TiedNote(
                        note=event, fraction=frac,
                        tie_start=False,
                        tie_stop=not is_first,
                    )
                    measures[-1].append(tied_note)
                    remaining_in_measure -= frac
                    frac = Fraction(0)
                else:
                    # Note spans measure boundary
                    tied_note = _TiedNote(
                        note=event, fraction=remaining_in_measure,
                        tie_start=True,
                        tie_stop=not is_first,
                    )
                    measures[-1].append(tied_note)
                    frac -= remaining_in_measure
                    remaining_in_measure = MEASURE_DURATION
                    measures.append([])
                    is_first = False
                if remaining_in_measure == Fraction(0):
                    remaining_in_measure = MEASURE_DURATION
                    measures.append([])

    # Remove empty trailing measure
    if measures and not measures[-1]:
        measures.pop()

    return measures


def _add_direction_dynamic(measure: ET.Element, dynamic: str) -> None:
    """Add a <direction> element with dynamic marking."""
    direction = ET.SubElement(measure, "direction", placement="below")
    dt = ET.SubElement(direction, "direction-type")
    dynamics = ET.SubElement(dt, "dynamics")
    ET.SubElement(dynamics, dynamic)


def _add_note_element(
    measure: ET.Element, tied: _TiedNote, divisions: int
) -> None:
    """Add a <note> element to a measure."""
    note = tied.note
    note_elem = ET.SubElement(measure, "note")

    # Pitch
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = note.pitch.step.upper()
    alter = ACCIDENTAL_TO_ALTER[note.pitch.accidental]
    if alter != 0:
        ET.SubElement(pitch_elem, "alter").text = str(alter)
    ET.SubElement(pitch_elem, "octave").text = str(note.pitch.octave)

    # Duration
    dur_val = fraction_to_mxml_duration(tied.fraction, divisions)
    ET.SubElement(note_elem, "duration").text = str(dur_val)

    # Type
    type_name = _fraction_to_type_name(tied.fraction)
    if type_name:
        ET.SubElement(note_elem, "type").text = type_name

    # Ties
    if tied.tie_start:
        ET.SubElement(note_elem, "tie", type="start")
    if tied.tie_stop:
        ET.SubElement(note_elem, "tie", type="stop")

    # Notations (articulations, ties, ornaments, fermata)
    notations_needed = (
        tied.tie_start or tied.tie_stop or
        note.articulations
    )
    if notations_needed:
        notations = ET.SubElement(note_elem, "notations")

        # Tied notation (visual)
        if tied.tie_start:
            ET.SubElement(notations, "tied", type="start")
        if tied.tie_stop:
            ET.SubElement(notations, "tied", type="stop")

        # Articulations
        regular_arts = [
            a for a in note.articulations
            if a in CADENZA_ARTICULATION_MAP
        ]
        if regular_arts:
            arts_elem = ET.SubElement(notations, "articulations")
            for art in regular_arts:
                ET.SubElement(arts_elem, CADENZA_ARTICULATION_MAP[art])

        # Fermata
        if "fermata" in note.articulations:
            ET.SubElement(notations, "fermata")

        # Ornaments (trill)
        if "trill" in note.articulations:
            ornaments = ET.SubElement(notations, "ornaments")
            ET.SubElement(ornaments, "trill-mark")


def _add_rest_element(
    measure: ET.Element, rest: Rest, divisions: int
) -> None:
    """Add a rest <note> element to a measure."""
    note_elem = ET.SubElement(measure, "note")
    ET.SubElement(note_elem, "rest")
    dur_val = fraction_to_mxml_duration(rest.duration.fraction, divisions)
    ET.SubElement(note_elem, "duration").text = str(dur_val)
    type_name = _fraction_to_type_name(rest.duration.fraction)
    if type_name:
        ET.SubElement(note_elem, "type").text = type_name


def _fraction_to_type_name(frac: Fraction) -> str | None:
    """Map a fraction to MusicXML type name (whole, half, quarter, etc.)."""
    # Try exact match
    if frac in FRACTION_TO_TYPE:
        return FRACTION_TO_TYPE[frac]
    # Try undotted: dotted = base * 3/2, so base = frac * 2/3
    undotted = frac * Fraction(2, 3)
    if undotted in FRACTION_TO_TYPE:
        return FRACTION_TO_TYPE[undotted]
    # Try closest smaller base
    for base_frac, name in sorted(FRACTION_TO_TYPE.items(), reverse=True):
        if base_frac <= frac:
            return name
    return "quarter"  # fallback
