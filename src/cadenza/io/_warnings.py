"""ImportWarning: frozen dataclass for tracking unsupported import elements."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImportWarning:
    """Warning generated during file import for unsupported or skipped elements.

    Attributes:
        element: Type of element that was skipped (e.g., 'grace-note', 'chord').
        position: Location in source file (XPath for MusicXML, tick string for MIDI).
        message: Human-readable description of what was skipped.
    """

    element: str
    position: str
    message: str
