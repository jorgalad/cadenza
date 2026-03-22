"""Cadenza: Music analysis, transformation, and generation library."""

__version__ = "0.1.0"

from cadenza.core import (
    Pitch,
    Duration,
    Interval,
    Note,
    Rest,
    Event,
    Phrase,
    Score,
    to_json,
    from_json,
)

__all__ = [
    "Pitch",
    "Duration",
    "Interval",
    "Note",
    "Rest",
    "Event",
    "Phrase",
    "Score",
    "to_json",
    "from_json",
]

# MusicXML I/O (stdlib only -- always available)
from cadenza.io import ImportWarning, import_musicxml, export_musicxml

__all__ += ["ImportWarning", "import_musicxml", "export_musicxml"]

# MIDI I/O (requires mido -- optional)
try:
    from cadenza.io.midi import import_midi, export_midi

    __all__ += ["import_midi", "export_midi"]
except ImportError:
    pass
