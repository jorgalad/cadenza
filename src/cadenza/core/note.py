"""Note and Rest: immutable event types for musical phrases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration


@dataclass(frozen=True)
class Note:
    """An immutable musical note with pitch, duration, dynamic, and articulations."""

    pitch: Pitch
    duration: Duration
    dynamic: str | None = None
    articulations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Rest:
    """An immutable musical rest with duration only."""

    duration: Duration


Event: TypeAlias = Note | Rest
