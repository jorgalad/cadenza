"""Tests for MIDI import functionality."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import mido
import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.core.score import Score
from cadenza.io._warnings import ImportWarning


# ---------------------------------------------------------------------------
# Helpers: create MIDI files in memory
# ---------------------------------------------------------------------------

def make_midi_file(
    notes: list[tuple[int, int, int, int]],
    ticks_per_beat: int = 480,
    tempo: int = 120,
    track_name: str | None = None,
    midi_type: int = 0,
) -> mido.MidiFile:
    """Create a MIDI file in memory.

    Each note is (midi_number, velocity, start_tick, duration_ticks).
    Notes are sorted by start_tick internally.
    """
    mid = mido.MidiFile(type=midi_type, ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Tempo meta message
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo), time=0))
    if track_name:
        track.append(mido.MetaMessage("track_name", name=track_name, time=0))

    # Sort notes by start tick
    sorted_notes = sorted(notes, key=lambda n: n[2])

    # Build events as (absolute_tick, message) pairs
    events: list[tuple[int, mido.Message]] = []
    for midi_num, vel, start, dur in sorted_notes:
        events.append((start, mido.Message("note_on", note=midi_num, velocity=vel, time=0)))
        events.append((start + dur, mido.Message("note_off", note=midi_num, velocity=0, time=0)))

    # Sort by absolute tick, then note_off before note_on at same tick
    events.sort(key=lambda e: (e[0], 0 if e[1].type == "note_off" else 1))

    # Convert to delta times
    current_tick = 0
    for abs_tick, msg in events:
        delta = abs_tick - current_tick
        msg.time = delta
        track.append(msg)
        current_tick = abs_tick

    return mid


def make_multitrack_midi(
    tracks: list[tuple[str, list[tuple[int, int, int, int]]]],
    ticks_per_beat: int = 480,
    tempo: int = 120,
) -> mido.MidiFile:
    """Create a multi-track (Type 1) MIDI file.

    tracks is [(track_name, [(midi_num, vel, start_tick, dur_ticks), ...]), ...]
    """
    mid = mido.MidiFile(type=1, ticks_per_beat=ticks_per_beat)

    # Track 0: tempo track
    tempo_track = mido.MidiTrack()
    mid.tracks.append(tempo_track)
    tempo_track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo), time=0))

    for name, notes in tracks:
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("track_name", name=name, time=0))

        sorted_notes = sorted(notes, key=lambda n: n[2])
        events: list[tuple[int, mido.Message]] = []
        for midi_num, vel, start, dur in sorted_notes:
            events.append((start, mido.Message("note_on", note=midi_num, velocity=vel, time=0)))
            events.append((start + dur, mido.Message("note_off", note=midi_num, velocity=0, time=0)))

        events.sort(key=lambda e: (e[0], 0 if e[1].type == "note_off" else 1))

        current_tick = 0
        for abs_tick, msg in events:
            msg.time = abs_tick - current_tick
            track.append(msg)
            current_tick = abs_tick

    return mid


@pytest.fixture
def simple_midi_path(tmp_path: Path) -> Path:
    """Single C4 quarter note at velocity 96."""
    # quarter note = 480 ticks at ticks_per_beat=480
    mid = make_midi_file([(60, 96, 0, 480)], ticks_per_beat=480, tempo=120)
    p = tmp_path / "simple.mid"
    mid.save(str(p))
    return p


@pytest.fixture
def multitrack_midi_path(tmp_path: Path) -> Path:
    """Two tracks with different notes."""
    mid = make_multitrack_midi(
        [
            ("Violin", [(64, 96, 0, 480)]),   # E4 quarter
            ("Cello", [(48, 80, 0, 480)]),     # C3 quarter
        ],
        ticks_per_beat=480,
        tempo=120,
    )
    p = tmp_path / "multitrack.mid"
    mid.save(str(p))
    return p


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestImportMidiErrors:
    """Test error handling for MIDI import."""

    def test_import_error_when_mido_not_installed(self):
        """import_midi raises ImportError with helpful message when mido not installed."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "mido":
                raise ModuleNotFoundError("No module named 'mido'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Need to reload module to trigger the import guard
            import importlib
            import cadenza.io.midi as midi_mod
            importlib.reload(midi_mod)
            with pytest.raises(ImportError, match="mido is required"):
                midi_mod.import_midi("dummy.mid")

        # Reload to restore normal state
        import importlib
        import cadenza.io.midi as midi_mod2
        importlib.reload(midi_mod2)


class TestImportMidiSingleTrack:
    """Test single-track MIDI import."""

    def test_single_c4_quarter(self, simple_midi_path: Path):
        """import_midi of single-track MIDI with C4 quarter returns correct Phrase."""
        from cadenza.io.midi import import_midi

        result, warnings = import_midi(simple_midi_path)
        assert isinstance(result, tuple)  # Phrase
        assert len(result) == 1
        note = result[0]
        assert isinstance(note, Note)
        assert note.pitch == Pitch("c", "n", 4)
        assert note.duration.fraction == Fraction(1, 4)  # quarter

    def test_velocity_96_maps_to_f(self, simple_midi_path: Path):
        """import_midi maps velocity 96 to dynamic 'f'."""
        from cadenza.io.midi import import_midi

        result, _ = import_midi(simple_midi_path)
        assert result[0].dynamic == "f"

    def test_velocity_33_maps_to_pp(self, tmp_path: Path):
        """import_midi maps velocity 33 to dynamic 'pp'."""
        from cadenza.io.midi import import_midi

        mid = make_midi_file([(60, 33, 0, 480)])
        p = tmp_path / "vel33.mid"
        mid.save(str(p))
        result, _ = import_midi(p)
        assert result[0].dynamic == "pp"

    def test_prefer_sharps_false_gives_eb(self, tmp_path: Path):
        """import_midi with prefer_sharps=False produces Eb for MIDI 63."""
        from cadenza.io.midi import import_midi

        mid = make_midi_file([(63, 80, 0, 480)])
        p = tmp_path / "eb.mid"
        mid.save(str(p))
        result, _ = import_midi(p, prefer_sharps=False)
        note = result[0]
        assert note.pitch.step == "e"
        assert note.pitch.accidental == "b"

    def test_prefer_sharps_true_gives_cs(self, tmp_path: Path):
        """import_midi with prefer_sharps=True produces C# for MIDI 61."""
        from cadenza.io.midi import import_midi

        mid = make_midi_file([(61, 80, 0, 480)])
        p = tmp_path / "cs.mid"
        mid.save(str(p))
        result, _ = import_midi(p, prefer_sharps=True)
        note = result[0]
        assert note.pitch.step == "c"
        assert note.pitch.accidental == "s"

    def test_default_prefer_sharps_false(self, tmp_path: Path):
        """import_midi default prefer_sharps=False (flats preferred)."""
        from cadenza.io.midi import import_midi

        mid = make_midi_file([(63, 80, 0, 480)])
        p = tmp_path / "default_flat.mid"
        mid.save(str(p))
        result, _ = import_midi(p)  # default
        note = result[0]
        # MIDI 63 = Eb4 with flats
        assert note.pitch.step == "e"
        assert note.pitch.accidental == "b"

    def test_quantize_default_sixteenth(self, tmp_path: Path):
        """import_midi quantizes to grid='16' by default (off-grid notes snap)."""
        from cadenza.io.midi import import_midi

        # 500 ticks at tpb=480 is slightly more than a quarter note
        # Should snap to nearest 16th: 480 ticks = quarter = 4 sixteenths
        # 500 / 120 (ticks per 16th) = 4.17 -> rounds to 4 sixteenths = quarter
        mid = make_midi_file([(60, 80, 0, 500)])
        p = tmp_path / "quantize.mid"
        mid.save(str(p))
        result, _ = import_midi(p)
        note = result[0]
        assert note.duration.fraction == Fraction(1, 4)  # snapped to quarter

    def test_quantize_eighth_grid(self, tmp_path: Path):
        """import_midi with grid='8' quantizes to eighth-note grid."""
        from cadenza.io.midi import import_midi

        # 300 ticks at tpb=480: fraction = 300/(480*4) = 300/1920 = 5/32
        # grid='8' -> grid_frac = 1/8
        # 5/32 / (1/8) = 5/4 = 1.25 -> rounds to 1 -> 1/8
        mid = make_midi_file([(60, 80, 0, 300)])
        p = tmp_path / "grid8.mid"
        mid.save(str(p))
        result, _ = import_midi(p, grid="8")
        note = result[0]
        assert note.duration.fraction == Fraction(1, 8)

    def test_note_on_velocity_zero_as_note_off(self, tmp_path: Path):
        """import_midi handles note_on with velocity=0 as note_off."""
        from cadenza.io.midi import import_midi

        # Manually create MIDI with note_on vel=0 instead of note_off
        mid = mido.MidiFile(type=0, ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
        track.append(mido.Message("note_on", note=60, velocity=96, time=0))
        track.append(mido.Message("note_on", note=60, velocity=0, time=480))
        p = tmp_path / "vel0.mid"
        mid.save(str(p))

        result, _ = import_midi(p)
        assert len(result) == 1
        assert isinstance(result[0], Note)
        assert result[0].pitch == Pitch("c", "n", 4)

    def test_gap_between_notes_produces_rest(self, tmp_path: Path):
        """import_midi inserts Rest for gaps between notes."""
        from cadenza.io.midi import import_midi

        # Note 1: ticks 0-480 (quarter), gap 480-960 (quarter), Note 2: 960-1440 (quarter)
        mid = make_midi_file([
            (60, 80, 0, 480),
            (62, 80, 960, 480),
        ])
        p = tmp_path / "gap.mid"
        mid.save(str(p))
        result, _ = import_midi(p)
        assert len(result) == 3
        assert isinstance(result[0], Note)
        assert isinstance(result[1], Rest)
        assert result[1].duration.fraction == Fraction(1, 4)
        assert isinstance(result[2], Note)

    def test_zero_duration_note_warning(self, tmp_path: Path):
        """import_midi of zero-duration note produces ImportWarning."""
        from cadenza.io.midi import import_midi

        # Simultaneous note_on and note_off
        mid = mido.MidiFile(type=0, ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
        track.append(mido.Message("note_on", note=60, velocity=96, time=0))
        track.append(mido.Message("note_off", note=60, velocity=0, time=0))
        # Add a real note so we get a non-empty result
        track.append(mido.Message("note_on", note=62, velocity=80, time=0))
        track.append(mido.Message("note_off", note=62, velocity=0, time=480))
        p = tmp_path / "zero_dur.mid"
        mid.save(str(p))

        result, warnings = import_midi(p)
        assert any(w.element == "zero-duration-note" for w in warnings)


class TestImportMidiMultiTrack:
    """Test multi-track MIDI import."""

    def test_multitrack_produces_score(self, multitrack_midi_path: Path):
        """import_midi multi-track -> Score with named voices."""
        from cadenza.io.midi import import_midi

        result, _ = import_midi(multitrack_midi_path)
        assert isinstance(result, Score)
        assert len(result.voice_names) == 2
        assert "Violin" in result.voice_names
        assert "Cello" in result.voice_names

    def test_skips_tempo_only_track(self, tmp_path: Path):
        """import_midi skips tempo-only track 0 in Type 1 files."""
        from cadenza.io.midi import import_midi

        # Type 1 with tempo track + 1 note track = should return Phrase, not Score
        mid = mido.MidiFile(type=1, ticks_per_beat=480)
        # Track 0: tempo only
        tempo_track = mido.MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
        # Track 1: notes
        note_track = mido.MidiTrack()
        mid.tracks.append(note_track)
        note_track.append(mido.MetaMessage("track_name", name="Piano", time=0))
        note_track.append(mido.Message("note_on", note=60, velocity=80, time=0))
        note_track.append(mido.Message("note_off", note=60, velocity=0, time=480))
        p = tmp_path / "type1_single.mid"
        mid.save(str(p))

        result, _ = import_midi(p)
        # Single track with notes -> returns Phrase, not Score
        assert isinstance(result, tuple)
        assert not isinstance(result, Score)
        assert len(result) == 1
