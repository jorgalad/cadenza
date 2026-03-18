"""Phrase: type alias for an immutable sequence of events."""

from __future__ import annotations

from typing import TypeAlias

from cadenza.core.note import Event

Phrase: TypeAlias = tuple[Event, ...]
