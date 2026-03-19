"""Rhythm transforms: retrograde, augmentation, diminution, rotation, and more.

All functions are pure -- they accept a Phrase and return a new Phrase.
Duration arithmetic uses Fraction exclusively (no floats).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.note import Event, Note, Rest
from cadenza.core.phrase import Phrase


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _scale_duration(dur: Duration, ratio: Fraction) -> Duration:
    """Scale a duration's fraction by *ratio*, keeping OMN metadata as hint."""
    return Duration(
        fraction=dur.fraction * ratio,
        base=dur.base,
        dots=dur.dots,
        tuplet=dur.tuplet,
    )


def _map_durations(phrase: Phrase, fn: Callable[[Duration], Duration]) -> Phrase:
    """Apply *fn* to the duration of every event (Note or Rest)."""
    return tuple(replace(event, duration=fn(event.duration)) for event in phrase)


def _to_fraction_ratio(ratio: Fraction | int | float) -> Fraction:
    """Convert a numeric ratio to an exact Fraction."""
    if isinstance(ratio, float):
        return Fraction(ratio).limit_denominator(1000)
    return Fraction(ratio)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rhythmic_retrograde(phrase: Phrase) -> Phrase:
    """Reverse duration sequence while keeping pitch/event order (RHYT-01).

    Both Notes and Rests participate -- durations are reversed across all
    events, then each event is rebuilt with the reversed duration at its
    original position.
    """
    if not phrase:
        return ()
    durations = [event.duration for event in phrase]
    durations.reverse()
    return tuple(replace(event, duration=dur) for event, dur in zip(phrase, durations))


def augment(phrase: Phrase, ratio: Fraction | int | float) -> Phrase:
    """Multiply all durations by *ratio* (RHYT-02).

    Accepts int, float, or Fraction.  Floats are converted to Fraction
    via ``limit_denominator(1000)`` to avoid drift.
    """
    if not phrase:
        return ()
    r = _to_fraction_ratio(ratio)
    return _map_durations(phrase, lambda d: _scale_duration(d, r))


def diminish(phrase: Phrase, ratio: Fraction | int | float) -> Phrase:
    """Divide all durations by *ratio* (RHYT-03).

    Equivalent to ``augment(phrase, 1/ratio)``.
    """
    if not phrase:
        return ()
    r = _to_fraction_ratio(ratio)
    return _map_durations(phrase, lambda d: _scale_duration(d, Fraction(1) / r))


def rhythmic_rotation(phrase: Phrase, n: int) -> Phrase:
    """Cyclic shift of durations only; pitches stay in place (RHYT-04).

    Positive *n* rotates durations left (first *n* durations move to end).
    Negative *n* rotates right.
    """
    if not phrase:
        return ()
    durations = [event.duration for event in phrase]
    k = n % len(durations)
    rotated = durations[k:] + durations[:k]
    return tuple(replace(event, duration=dur) for event, dur in zip(phrase, rotated))


def metric_modulation(
    phrase: Phrase,
    old_unit: Duration,
    new_unit: Duration,
) -> Phrase:
    """Scale all durations by ``new_unit / old_unit`` (RHYT-05).

    Models a metric modulation where the *old_unit* beat becomes the
    *new_unit* beat.  For example, dotted-quarter -> quarter scales
    everything by 2/3.
    """
    if not phrase:
        return ()
    ratio = new_unit.fraction / old_unit.fraction
    return augment(phrase, ratio)


def extract_rhythm(phrase: Phrase) -> tuple[Duration, ...]:
    """Return the duration sequence of a phrase, including rests (RHYT-07)."""
    return tuple(event.duration for event in phrase)


def quantize(phrase: Phrase, grid: Sequence[Duration | str]) -> Phrase:
    """Snap each event's duration to the nearest grid value (RHYT-08).

    Grid values may be ``Duration`` objects or OMN base strings (e.g. ``"q"``).
    """
    # Parse grid into Duration objects
    parsed: list[Duration] = []
    for item in grid:
        if isinstance(item, str):
            parsed.append(Duration.from_omn(item))
        else:
            parsed.append(item)

    def _snap(dur: Duration) -> Duration:
        best = min(parsed, key=lambda g: abs(g.fraction - dur.fraction))
        return best

    return _map_durations(phrase, _snap)


def total_duration(phrase: Phrase) -> Fraction:
    """Sum of all event durations as an exact Fraction (RHYT-09)."""
    return sum((event.duration.fraction for event in phrase), Fraction(0))
