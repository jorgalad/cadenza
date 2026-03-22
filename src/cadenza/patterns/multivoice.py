"""Multi-voice pattern generation: rhythmic canon and hocket."""

from __future__ import annotations

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.phrase import Phrase
from cadenza.core.score import Score


def rhythmic_canon(phrase: Phrase, n: int, offset: Duration) -> Score:
    """Create an n-voice rhythmic canon from *phrase*.

    Each successive voice enters after *offset* more time than the previous.
    voice_0 plays the original phrase with no leading rest.  voice_i (i > 0)
    has a single leading rest whose duration equals ``offset.fraction * i``,
    followed by the full original phrase.

    Raises ``ValueError`` if *phrase* is empty or *n* < 1.
    """
    if not phrase:
        raise ValueError("phrase must not be empty")
    if n < 1:
        raise ValueError("n must be >= 1")

    voices: list[tuple[str, Phrase]] = []
    for i in range(n):
        if i == 0:
            voice_phrase = phrase
        else:
            rest_fraction = offset.fraction * i
            leading_rest = Rest(
                duration=Duration(fraction=rest_fraction, base=offset.base),
            )
            voice_phrase = (leading_rest,) + phrase
        voices.append((f"voice_{i}", voice_phrase))

    return Score(_voices=tuple(voices))


def hocket(phrase: Phrase, n: int) -> Score:
    """Distribute *phrase* events round-robin across *n* voices.

    Each event goes to exactly one voice (``idx % n``).  All other voices
    receive a ``Rest`` whose duration matches the original event, so every
    voice has the same number of events and the same total duration.

    Raises ``ValueError`` if *phrase* is empty or *n* < 1.
    """
    if not phrase:
        raise ValueError("phrase must not be empty")
    if n < 1:
        raise ValueError("n must be >= 1")

    voice_events: list[list[Note | Rest]] = [[] for _ in range(n)]

    for idx, event in enumerate(phrase):
        target = idx % n
        for v in range(n):
            if v == target:
                voice_events[v].append(event)
            else:
                voice_events[v].append(Rest(duration=event.duration))

    return Score(
        _voices=tuple(
            (f"voice_{v}", tuple(voice_events[v])) for v in range(n)
        ),
    )
