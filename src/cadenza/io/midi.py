"""MIDI import and export for Cadenza.

Requires the ``mido`` library (install with ``pip install cadenza[io]``).
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.score import Score
from cadenza.io._duration_conv import fraction_to_best_duration
from cadenza.io._dynamics_map import dynamic_to_velocity, velocity_to_dynamic
from cadenza.io._warnings import ImportWarning
from cadenza.transforms.pitch import from_midi

if TYPE_CHECKING:
    pass


def _require_mido():  # noqa: ANN202
    """Import and return the mido module, raising a helpful error if missing."""
    try:
        import mido
        return mido
    except ImportError:
        raise ImportError(
            "mido is required for MIDI I/O. Install with: pip install cadenza[io]"
        ) from None


# ---------------------------------------------------------------------------
# Grid quantization
# ---------------------------------------------------------------------------

_GRID_TO_CN: dict[str, str] = {
    "1": "w",    # whole
    "2": "h",    # half
    "4": "q",    # quarter
    "8": "e",    # eighth
    "16": "s",   # sixteenth
    "32": "t",   # thirty-second
    "64": "x",   # sixty-fourth
}


def _grid_to_fraction(grid: str) -> Fraction:
    """Convert a grid string ('16', '8', etc.) to fraction of whole note."""
    cn_base = _GRID_TO_CN.get(grid)
    if cn_base is not None:
        return Duration.from_cn(cn_base).fraction
    # Fallback: try as CN base directly
    return Duration.from_cn(grid).fraction


def _snap_to_grid(frac: Fraction, grid: Fraction) -> Fraction:
    """Snap a duration fraction to the nearest multiple of the grid.

    Minimum result is one grid unit (no zero-duration output).
    """
    n = round(frac / grid)
    if n < 1:
        n = 1
    return n * grid


# ---------------------------------------------------------------------------
# MIDI Import
# ---------------------------------------------------------------------------

def import_midi(
    path: str | Path,
    grid: str = "16",
    prefer_sharps: bool = False,
) -> tuple[Phrase | Score, list[ImportWarning]]:
    """Import a MIDI file into Cadenza Phrase or Score.

    Args:
        path: Path to the MIDI file.
        grid: Quantization grid as CN base duration string (e.g. '16' for
              sixteenth notes, '8' for eighth notes). Default is '16'.
        prefer_sharps: If True, spell black keys as sharps; if False (default),
                       prefer flats.

    Returns:
        A tuple of (result, warnings) where result is a Phrase (single track)
        or Score (multi-track), and warnings is a list of ImportWarning.
    """
    mido = _require_mido()

    # Parse grid to fraction of whole note
    grid_fraction = _grid_to_fraction(grid)

    mid = mido.MidiFile(str(path))
    ticks_per_beat = mid.ticks_per_beat

    warnings: list[ImportWarning] = []
    voice_phrases: dict[str, Phrase] = {}

    for track_idx, track in enumerate(mid.tracks):
        # Extract track name
        track_name: str | None = None
        for msg in track:
            if msg.type == "track_name":
                track_name = msg.name
                break

        if track_name is None:
            track_name = f"track_{track_idx}"

        # Pair note_on / note_off events
        active_notes: dict[int, tuple[int, int]] = {}  # midi_num -> (start_tick, velocity)
        paired_notes: list[tuple[int, int, int, int]] = []  # (start_tick, midi_num, velocity, dur_ticks)
        current_tick = 0

        for msg in track:
            current_tick += msg.time

            if msg.type == "note_on" and msg.velocity > 0:
                active_notes[msg.note] = (current_tick, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active_notes:
                    start_tick, velocity = active_notes.pop(msg.note)
                    duration_ticks = current_tick - start_tick
                    if duration_ticks == 0:
                        warnings.append(ImportWarning(
                            element="zero-duration-note",
                            position=f"tick {start_tick}",
                            message=f"Zero-duration note (MIDI {msg.note}) at tick {start_tick}, skipped",
                        ))
                        continue
                    paired_notes.append((start_tick, msg.note, velocity, duration_ticks))

        # Skip tracks with no note events (e.g., tempo-only track)
        if not paired_notes:
            continue

        # Sort by start tick
        paired_notes.sort(key=lambda n: (n[0], n[1]))

        # Convert to events
        events: list[Note | Rest] = []
        current_end_tick = 0

        for start_tick, midi_num, velocity, dur_ticks in paired_notes:
            # Insert rest for gap
            if start_tick > current_end_tick:
                gap_ticks = start_tick - current_end_tick
                gap_frac = Fraction(gap_ticks, ticks_per_beat * 4)
                quantized_gap = _snap_to_grid(gap_frac, grid_fraction)
                rest_dur = fraction_to_best_duration(quantized_gap)
                events.append(Rest(duration=rest_dur))

            # Convert note
            dur_frac = Fraction(dur_ticks, ticks_per_beat * 4)
            quantized = _snap_to_grid(dur_frac, grid_fraction)
            pitch = from_midi(midi_num, prefer_sharps=prefer_sharps)
            dynamic = velocity_to_dynamic(velocity)
            duration = fraction_to_best_duration(quantized)
            events.append(Note(pitch=pitch, duration=duration, dynamic=dynamic))

            current_end_tick = start_tick + dur_ticks

        voice_phrases[track_name] = tuple(events)

    # Return Phrase for single track, Score for multiple
    if len(voice_phrases) == 1:
        phrase = next(iter(voice_phrases.values()))
        return phrase, warnings
    elif len(voice_phrases) == 0:
        return (), warnings
    else:
        return Score.from_dict(voice_phrases), warnings
