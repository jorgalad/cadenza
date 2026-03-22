"""Cadenza I/O: import and export for MusicXML and MIDI formats."""

from cadenza.io._warnings import ImportWarning
from cadenza.io.musicxml import export_musicxml, import_musicxml

__all__ = ["ImportWarning", "import_musicxml", "export_musicxml"]

try:
    from cadenza.io.midi import export_midi, import_midi

    __all__ += ["import_midi", "export_midi"]
except ImportError:
    pass
