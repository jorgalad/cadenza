"""Tests for MIDI export functionality."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import mido
import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score


@pytest.fixture
def quarter_c4_phrase() -> tuple[Note, ...]:
    """A single C4 quarter note phrase."""
    return (
        Note(
            pitch=Pitch("c", "n", 4),
            duration=Duration.from_cn("q"),
            dynamic="f",
        ),
    )


@pytest.fixture
def phrase_with_rest() -> tuple[Note | Rest, ...]:
    """Phrase: C4 quarter, quarter rest, D4 quarter."""
    return (
        Note(pitch=Pitch("c", "n", 4), duration=Duration.from_cn("q"), dynamic="mf"),
        Rest(duration=Duration.from_cn("q")),
        Note(pitch=Pitch("d", "n", 4), duration=Duration.from_cn("q"), dynamic="mf"),
    )


@pytest.fixture
def two_voice_score() -> Score:
    """Score with two voices."""
    return Score.from_dict({
        "Violin": (
            Note(pitch=Pitch("e", "n", 5), duration=Duration.from_cn("q"), dynamic="f"),
        ),
        "Cello": (
            Note(pitch=Pitch("c", "n", 3), duration=Duration.from_cn("q"), dynamic="p"),
        ),
    })


class TestExportMidiBasic:
    """Test basic MIDI export."""

    def test_creates_valid_midi_file(self, quarter_c4_phrase, tmp_path: Path):
        """export_midi creates a valid MIDI file readable by mido."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        assert mid is not None

    def test_ticks_per_beat_480(self, quarter_c4_phrase, tmp_path: Path):
        """Exported MIDI has ticks_per_beat = 480."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        assert mid.ticks_per_beat == 480

    def test_tempo_meta_message(self, quarter_c4_phrase, tmp_path: Path):
        """Exported MIDI contains set_tempo meta message matching 120 BPM."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        tempo_msgs = [msg for track in mid.tracks for msg in track if msg.type == "set_tempo"]
        assert len(tempo_msgs) >= 1
        assert tempo_msgs[0].tempo == mido.bpm2tempo(120)

    def test_note_on_c4_has_note_60(self, quarter_c4_phrase, tmp_path: Path):
        """Exported MIDI note_on for C4 has note=60."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        note_ons = [msg for track in mid.tracks for msg in track
                    if msg.type == "note_on" and msg.velocity > 0]
        assert len(note_ons) == 1
        assert note_ons[0].note == 60

    def test_dynamic_f_velocity_96(self, quarter_c4_phrase, tmp_path: Path):
        """Exported MIDI note_on for dynamic 'f' has velocity=96."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        note_ons = [msg for track in mid.tracks for msg in track
                    if msg.type == "note_on" and msg.velocity > 0]
        assert note_ons[0].velocity == 96

    def test_dynamic_none_velocity_64(self, tmp_path: Path):
        """Exported MIDI note_on for dynamic=None has velocity=64."""
        from cadenza.io.midi import export_midi

        phrase = (
            Note(pitch=Pitch("c", "n", 4), duration=Duration.from_cn("q"), dynamic=None),
        )
        p = tmp_path / "test.mid"
        export_midi(phrase, p)
        mid = mido.MidiFile(str(p))
        note_ons = [msg for track in mid.tracks for msg in track
                    if msg.type == "note_on" and msg.velocity > 0]
        assert note_ons[0].velocity == 64

    def test_note_duration_in_ticks(self, quarter_c4_phrase, tmp_path: Path):
        """Exported MIDI note duration in ticks matches input Duration fraction."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p)
        mid = mido.MidiFile(str(p))
        # Find note_on and note_off for note 60
        events = [(msg.type, msg.note, msg.time) for track in mid.tracks
                  for msg in track if hasattr(msg, "note")]
        # note_off time should be 480 (quarter at tpb=480)
        note_offs = [e for e in events if e[0] == "note_off"]
        assert len(note_offs) == 1
        assert note_offs[0][2] == 480

    def test_rest_produces_gap(self, phrase_with_rest, tmp_path: Path):
        """Exported MIDI for Rest produces gap (no note events for rest duration)."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(phrase_with_rest, p)
        mid = mido.MidiFile(str(p))

        # Collect note_on events with absolute ticks
        abs_tick = 0
        note_on_ticks = []
        for track in mid.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    note_on_ticks.append(abs_tick)

        # First note at tick 0, second note at tick 960 (480 for note + 480 for rest)
        assert len(note_on_ticks) == 2
        assert note_on_ticks[0] == 0
        assert note_on_ticks[1] == 960  # quarter note + quarter rest = 960 ticks


class TestExportMidiMultiTrack:
    """Test multi-track MIDI export."""

    def test_score_creates_multitrack(self, two_voice_score, tmp_path: Path):
        """export_midi(score) creates multi-track MIDI with one track per voice."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(two_voice_score, p)
        mid = mido.MidiFile(str(p))
        assert mid.type == 1
        # Track 0 = tempo, Track 1 = Violin, Track 2 = Cello
        assert len(mid.tracks) == 3

    def test_tempo_100(self, quarter_c4_phrase, tmp_path: Path):
        """export_midi with tempo=100 sets correct microseconds-per-beat."""
        from cadenza.io.midi import export_midi

        p = tmp_path / "test.mid"
        export_midi(quarter_c4_phrase, p, tempo=100)
        mid = mido.MidiFile(str(p))
        tempo_msgs = [msg for track in mid.tracks for msg in track if msg.type == "set_tempo"]
        assert tempo_msgs[0].tempo == mido.bpm2tempo(100)


class TestExportMidiInit:
    """Test that cadenza.io exports MIDI functions."""

    def test_io_init_exports(self):
        """cadenza.io.__init__ exports import_midi, export_midi, import_musicxml, export_musicxml, ImportWarning."""
        from cadenza.io import (
            ImportWarning,
            export_midi,
            export_musicxml,
            import_midi,
            import_musicxml,
        )
        assert callable(import_midi)
        assert callable(export_midi)
        assert callable(import_musicxml)
        assert callable(export_musicxml)
        assert ImportWarning is not None
