"""CN serializer: converts Phrase to compact CN notation string."""

from __future__ import annotations

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch


def to_cn(phrase: Phrase) -> str:
    """Serialize a Phrase to compact CN notation.

    Uses sticky optimization: only emits duration, dynamic, and articulations
    when they differ from the previous note. Pitch is always emitted for every Note.
    """
    parts: list[str] = []
    prev_duration: Duration | None = None
    prev_dynamic: str | None = None
    prev_articulations: tuple[str, ...] = ()

    for event in phrase:
        if isinstance(event, Rest):
            parts.append(_rest_to_cn(event.duration))
            # Rest does NOT reset sticky state -- previous note state carries through
            continue

        if isinstance(event, Note):
            tokens: list[str] = []

            # Duration: emit only if changed
            if event.duration != prev_duration:
                tokens.append(_duration_to_cn(event.duration))
                prev_duration = event.duration

            # Pitch: always emit
            tokens.append(_pitch_to_cn(event.pitch))

            # Dynamic: emit only if changed.
            # CN cannot "unset" a dynamic, so only update prev when a
            # concrete dynamic is present. A Note with dynamic=None keeps
            # the previous sticky dynamic during serialization.
            if event.dynamic is not None and event.dynamic != prev_dynamic:
                tokens.append(event.dynamic)
                prev_dynamic = event.dynamic

            # Articulations: emit only if changed.
            # Empty articulations mean "keep previous" in CN, so only
            # update prev when there are concrete articulations.
            if event.articulations and event.articulations != prev_articulations:
                tokens.extend(event.articulations)
                prev_articulations = event.articulations

            parts.append(" ".join(tokens))

    return " ".join(parts)


def _duration_to_cn(d: Duration) -> str:
    """Convert a Duration to its CN string representation."""
    result = ""
    if d.tuplet is not None:
        result += str(d.tuplet)
    result += d.base
    result += "." * d.dots
    return result


def _pitch_to_cn(p: Pitch) -> str:
    """Convert a Pitch to its CN string representation."""
    acc = "" if p.accidental == "n" else p.accidental
    return f"{p.step}{acc}{p.octave}"


def _rest_to_cn(d: Duration) -> str:
    """Convert a rest Duration to its CN string representation."""
    return "-" + _duration_to_cn(d)


