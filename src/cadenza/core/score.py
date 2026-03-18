"""Score: immutable container for multiple named voices."""

from __future__ import annotations

from dataclasses import dataclass

from cadenza.core.phrase import Phrase


@dataclass(frozen=True)
class Score:
    """Immutable multi-voice score.

    Stores voices as tuple of (name, phrase) pairs for true immutability
    and hashability. Provides dict-like access via properties.
    """

    _voices: tuple[tuple[str, Phrase], ...] = ()

    @staticmethod
    def from_dict(voices: dict[str, Phrase]) -> Score:
        """Create a Score from a dict of voice names to phrases."""
        return Score(_voices=tuple(voices.items()))

    @property
    def voices(self) -> dict[str, Phrase]:
        """Return voices as a dict (new copy each call)."""
        return dict(self._voices)

    @property
    def voice_names(self) -> tuple[str, ...]:
        """Return voice names in insertion order."""
        return tuple(name for name, _ in self._voices)

    def __getitem__(self, voice_name: str) -> Phrase:
        """Get a phrase by voice name."""
        for name, phrase in self._voices:
            if name == voice_name:
                return phrase
        raise KeyError(voice_name)
