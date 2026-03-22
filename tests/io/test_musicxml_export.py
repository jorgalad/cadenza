"""Tests for MusicXML export functionality."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.io.musicxml import export_musicxml


def _phrase(*events):
    """Helper to create a phrase tuple."""
    return tuple(events)


def _note(step, acc, octave, frac_num, frac_den, dynamic=None, articulations=()):
    return Note(
        pitch=Pitch(step, acc, octave),
        duration=Duration(fraction=Fraction(frac_num, frac_den)),
        dynamic=dynamic,
        articulations=articulations,
    )


def _rest(frac_num, frac_den):
    return Rest(duration=Duration(fraction=Fraction(frac_num, frac_den)))


class TestExportBasic:
    def test_creates_parseable_xml(self, tmp_path):
        phrase = _phrase(_note("c", "n", 4, 1, 4))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        assert tree.getroot().tag == "score-partwise"

    def test_pitch_c4(self, tmp_path):
        phrase = _phrase(_note("c", "n", 4, 1, 4))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        note = tree.find(".//note")
        assert note is not None
        pitch = note.find("pitch")
        assert pitch is not None
        assert pitch.findtext("step") == "C"
        assert pitch.find("alter") is None  # No alter for natural
        assert pitch.findtext("octave") == "4"

    def test_pitch_eb4(self, tmp_path):
        phrase = _phrase(_note("e", "b", 4, 1, 4))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        pitch = tree.find(".//pitch")
        assert pitch is not None
        assert pitch.findtext("step") == "E"
        assert pitch.findtext("alter") == "-1"
        assert pitch.findtext("octave") == "4"

    def test_duration_quarter(self, tmp_path):
        phrase = _phrase(_note("c", "n", 4, 1, 4))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        # divisions should match; duration = divisions (for quarter note)
        divisions = int(tree.findtext(".//divisions") or "1")
        dur = int(tree.find(".//note").findtext("duration") or "0")
        assert dur == divisions  # quarter note duration == divisions value

    def test_dynamics_as_direction(self, tmp_path):
        phrase = _phrase(_note("c", "n", 4, 1, 4, dynamic="f"))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        # Should have a <direction> with <dynamics><f/></dynamics>
        dynamics = tree.find(".//direction/direction-type/dynamics")
        assert dynamics is not None
        assert dynamics.find("f") is not None

    def test_articulations_staccato(self, tmp_path):
        phrase = _phrase(_note("c", "n", 4, 1, 4, articulations=("stacc",)))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        staccato = tree.find(".//notations/articulations/staccato")
        assert staccato is not None

    def test_rest_export(self, tmp_path):
        phrase = _phrase(_rest(1, 4))
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        note = tree.find(".//note")
        assert note is not None
        assert note.find("rest") is not None
        dur = int(note.findtext("duration") or "0")
        assert dur > 0


class TestExportScore:
    def test_multipart_export(self, tmp_path):
        phrase1 = _phrase(_note("c", "n", 4, 1, 4))
        phrase2 = _phrase(_note("e", "n", 3, 1, 4))
        score = Score.from_dict({"Violin": phrase1, "Cello": phrase2})
        path = tmp_path / "out.musicxml"
        export_musicxml(score, path)
        tree = ET.parse(str(path))
        parts = tree.findall("part")
        assert len(parts) == 2
        part_list = tree.find("part-list")
        assert part_list is not None
        score_parts = part_list.findall("score-part")
        assert len(score_parts) == 2


class TestExportDivisions:
    def test_dynamic_divisions(self, tmp_path):
        # Phrase with eighth (1/8) and triplet quarter (1/6)
        phrase = _phrase(
            _note("c", "n", 4, 1, 8),
            _note("d", "n", 4, 1, 6),
        )
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        divisions = int(tree.findtext(".//divisions") or "1")
        # divisions must allow both 1/8 and 1/6 to be represented as integers
        # 1/8 * 4 * div must be int -> div/2 must be int -> div divisible by 2
        # 1/6 * 4 * div must be int -> 2*div/3 must be int -> div divisible by 3
        assert divisions % 2 == 0
        assert divisions % 3 == 0


class TestExportMeasures:
    def test_creates_4_4_measures_with_ties(self, tmp_path):
        # A whole note + a quarter note should produce 2 measures with a tie
        phrase = _phrase(
            _note("c", "n", 4, 1, 1),  # whole note fills measure 1
            _note("d", "n", 4, 1, 4),  # quarter note in measure 2
        )
        path = tmp_path / "out.musicxml"
        export_musicxml(phrase, path)
        tree = ET.parse(str(path))
        measures = tree.findall(".//measure")
        assert len(measures) == 2


class TestExportErrors:
    def test_raises_for_unrepresentable_duration(self, tmp_path):
        # Fraction(1, 7) cannot be represented cleanly
        phrase = _phrase(
            Note(
                pitch=Pitch("c", "n", 4),
                duration=Duration(fraction=Fraction(1, 7), base="q"),
            )
        )
        path = tmp_path / "out.musicxml"
        with pytest.raises(ValueError):
            export_musicxml(phrase, path)
