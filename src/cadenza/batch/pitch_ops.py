"""Batch pitch operations: replace_pitch, filter_phrase.

BATCH-07: replace_pitch
BATCH-08: filter_phrase
"""

from __future__ import annotations

from dataclasses import replace

from cadenza.core.note import Event, Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch

from collections.abc import Callable


def replace_pitch(
    phrase: Phrase,
    old: Pitch,
    new: Pitch,
    *,
    by_class: bool = False,
) -> Phrase:
    """Replace pitches in a phrase.

    If by_class is False: exact pitch match (step + accidental + octave).
    If by_class is True: match by pitch class (any octave), preserving the
    original note's octave.
    Rests are unchanged.
    """
    result: list[Event] = []
    for event in phrase:
        if isinstance(event, Note):
            if by_class:
                if event.pitch.pitch_class == old.pitch_class:
                    new_pitch = Pitch(new.step, new.accidental, event.pitch.octave)
                    result.append(replace(event, pitch=new_pitch))
                else:
                    result.append(event)
            else:
                if event.pitch == old:
                    result.append(replace(event, pitch=new))
                else:
                    result.append(event)
        else:
            result.append(event)
    return tuple(result)


def filter_phrase(
    phrase: Phrase, predicate: Callable[[Event], bool]
) -> Phrase:
    """Keep only events matching the predicate.

    Returns a Phrase (tuple of Events).
    """
    return tuple(e for e in phrase if predicate(e))
