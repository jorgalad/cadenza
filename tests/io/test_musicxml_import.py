"""Tests for MusicXML import functionality."""

from __future__ import annotations

from fractions import Fraction

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.io._duration_conv import (
    fraction_to_best_duration,
    fraction_to_mxml_duration,
    mxml_duration_to_fraction,
)
from cadenza.io._dynamics_map import (
    dynamic_to_velocity,
    velocity_to_dynamic,
)
from cadenza.io._warnings import ImportWarning
from cadenza.io.musicxml import import_musicxml

from tests.io.conftest import (
    DYNAMICS_ARTICULATIONS_MUSICXML,
    GRACE_NOTE_MUSICXML,
    MULTIPART_MUSICXML,
    REST_MUSICXML,
    SHARP_FLAT_MUSICXML,
    SIMPLE_MUSICXML,
    TIE_CHAIN_MUSICXML,
    TIED_NOTES_MUSICXML,
    VARYING_DIVISIONS_MUSICXML,
    write_xml,
)


# ---- ImportWarning tests ----


class TestImportWarning:
    def test_frozen_dataclass(self):
        w = ImportWarning(element="grace-note", position="P1/M1/N1", message="skipped")
        assert w.element == "grace-note"
        assert w.position == "P1/M1/N1"
        assert w.message == "skipped"
        with pytest.raises(AttributeError):
            w.element = "other"  # type: ignore[misc]


# ---- Duration conversion tests ----


class TestDurationConversion:
    def test_fraction_to_mxml_duration_quarter(self):
        assert fraction_to_mxml_duration(Fraction(1, 4), divisions=4) == 4

    def test_mxml_duration_to_fraction_quarter(self):
        assert mxml_duration_to_fraction(4, divisions=4) == Fraction(1, 4)

    def test_fraction_to_mxml_duration_half(self):
        assert fraction_to_mxml_duration(Fraction(1, 2), divisions=4) == 8

    def test_fraction_to_mxml_duration_raises_for_non_integer(self):
        # Fraction(1,6) with divisions=4 -> 1/6 * 4 * 4 = 8/3 -> not integer
        with pytest.raises(ValueError):
            fraction_to_mxml_duration(Fraction(1, 6), divisions=4)


# ---- Dynamics mapping tests ----


class TestDynamicsMapping:
    def test_velocity_to_dynamic_f(self):
        assert velocity_to_dynamic(96) == "f"

    def test_velocity_to_dynamic_ppp(self):
        assert velocity_to_dynamic(1) == "ppp"

    def test_velocity_to_dynamic_fff(self):
        assert velocity_to_dynamic(127) == "fff"

    def test_dynamic_to_velocity_f(self):
        assert dynamic_to_velocity("f") == 96

    def test_dynamic_to_velocity_none(self):
        assert dynamic_to_velocity(None) == 64


# ---- MusicXML import tests ----


class TestMusicXMLImportSimple:
    def test_single_note_c4_quarter(self, tmp_path):
        path = write_xml(SIMPLE_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert isinstance(result, tuple)  # Phrase
        assert len(result) == 1
        note = result[0]
        assert isinstance(note, Note)
        assert note.pitch == Pitch("c", "n", 4)
        assert note.duration.fraction == Fraction(1, 4)

    def test_sharps_flats(self, tmp_path):
        path = write_xml(SHARP_FLAT_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert len(result) == 2
        assert result[0].pitch == Pitch("f", "s", 4)  # F#4
        assert result[1].pitch == Pitch("e", "b", 4)  # Eb4

    def test_rest(self, tmp_path):
        path = write_xml(REST_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert len(result) == 1
        assert isinstance(result[0], Rest)
        assert result[0].duration.fraction == Fraction(1, 4)


class TestMusicXMLImportTies:
    def test_two_tied_quarters_merge_to_half(self, tmp_path):
        path = write_xml(TIED_NOTES_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert len(result) == 1
        note = result[0]
        assert isinstance(note, Note)
        assert note.pitch == Pitch("c", "n", 4)
        assert note.duration.fraction == Fraction(1, 2)

    def test_three_note_tie_chain(self, tmp_path):
        path = write_xml(TIE_CHAIN_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert len(result) == 1
        note = result[0]
        assert isinstance(note, Note)
        assert note.duration.fraction == Fraction(3, 4)  # 3 quarters


class TestMusicXMLImportDynamicsArticulations:
    def test_dynamics_read(self, tmp_path):
        path = write_xml(DYNAMICS_ARTICULATIONS_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        # Both notes should have "f" dynamic (sticky)
        assert result[0].dynamic == "f"
        assert result[1].dynamic == "f"

    def test_articulations_read(self, tmp_path):
        path = write_xml(DYNAMICS_ARTICULATIONS_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert "stacc" in result[0].articulations
        assert "accent" in result[1].articulations


class TestMusicXMLImportMultiPart:
    def test_multipart_returns_score(self, tmp_path):
        path = write_xml(MULTIPART_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert isinstance(result, Score)
        assert "Violin" in result.voice_names
        assert "Cello" in result.voice_names


class TestMusicXMLImportWarnings:
    def test_grace_note_skipped_with_warning(self, tmp_path):
        path = write_xml(GRACE_NOTE_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        # Grace note should be skipped; only the real C4 should be imported
        assert len(result) == 1
        assert result[0].pitch == Pitch("c", "n", 4)
        assert len(warnings) >= 1
        assert any(w.element == "grace-note" for w in warnings)


class TestMusicXMLImportVaryingDivisions:
    def test_handles_varying_divisions(self, tmp_path):
        path = write_xml(VARYING_DIVISIONS_MUSICXML, tmp_path)
        result, warnings = import_musicxml(path)
        assert len(result) == 2
        # Both should be quarter notes despite different divisions
        assert result[0].duration.fraction == Fraction(1, 4)
        assert result[1].duration.fraction == Fraction(1, 4)
