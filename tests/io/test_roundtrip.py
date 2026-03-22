"""Roundtrip tests: export then import should preserve data."""

from __future__ import annotations

from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.io.midi import export_midi, import_midi
from cadenza.io.musicxml import export_musicxml, import_musicxml


def _note(step, acc, octave, frac_num, frac_den, dynamic=None, articulations=()):
    return Note(
        pitch=Pitch(step, acc, octave),
        duration=Duration(fraction=Fraction(frac_num, frac_den)),
        dynamic=dynamic,
        articulations=articulations,
    )


class TestMusicXMLRoundtrip:
    def test_pitches_and_durations_preserved(self, tmp_path):
        original = (
            _note("c", "n", 4, 1, 4),
            _note("e", "b", 4, 1, 4),
            _note("g", "s", 4, 1, 2),
        )
        path = tmp_path / "rt.musicxml"
        export_musicxml(original, path)
        result, warnings = import_musicxml(path)
        assert isinstance(result, tuple)
        assert len(result) == len(original)
        for orig, imported in zip(original, result):
            assert isinstance(imported, Note)
            assert imported.pitch == orig.pitch
            assert imported.duration.fraction == orig.duration.fraction

    def test_dynamics_preserved(self, tmp_path):
        original = (
            _note("c", "n", 4, 1, 4, dynamic="f"),
            _note("d", "n", 4, 1, 4, dynamic="p"),
        )
        path = tmp_path / "rt.musicxml"
        export_musicxml(original, path)
        result, warnings = import_musicxml(path)
        assert isinstance(result, tuple)
        assert result[0].dynamic == "f"
        assert result[1].dynamic == "p"

    def test_score_roundtrip(self, tmp_path):
        phrase1 = (_note("c", "n", 4, 1, 4),)
        phrase2 = (_note("e", "n", 3, 1, 4),)
        score = Score.from_dict({"Violin": phrase1, "Cello": phrase2})
        path = tmp_path / "rt.musicxml"
        export_musicxml(score, path)
        result, warnings = import_musicxml(path)
        assert isinstance(result, Score)
        assert "Violin" in result.voice_names
        assert "Cello" in result.voice_names
        violin_phrase = result["Violin"]
        assert len(violin_phrase) == 1
        assert violin_phrase[0].pitch == Pitch("c", "n", 4)


class TestMidiRoundtrip:
    """Test export-then-import roundtrip for MIDI."""

    def test_pitches_and_durations_preserved(self, tmp_path):
        original = (
            _note("c", "n", 4, 1, 4, dynamic="f"),
            _note("e", "n", 4, 1, 4, dynamic="f"),
            _note("g", "n", 4, 1, 2, dynamic="f"),
        )
        path = tmp_path / "rt.mid"
        export_midi(original, path)
        result, warnings = import_midi(path)
        assert isinstance(result, tuple)
        assert len(result) == len(original)
        for orig, imported in zip(original, result):
            assert isinstance(imported, Note)
            assert imported.pitch == orig.pitch
            assert imported.duration.fraction == orig.duration.fraction

    def test_dynamics_preserved(self, tmp_path):
        original = (
            _note("c", "n", 4, 1, 4, dynamic="pp"),
            _note("d", "n", 4, 1, 4, dynamic="ff"),
        )
        path = tmp_path / "rt.mid"
        export_midi(original, path)
        result, warnings = import_midi(path)
        assert isinstance(result, tuple)
        assert result[0].dynamic == "pp"
        assert result[1].dynamic == "ff"
