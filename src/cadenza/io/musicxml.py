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
    fraction_to_best_duration,
    mxml_duration_to_fraction,
)
from cadenza.io._warnings import ImportWarning

# --- Mapping tables ---

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
