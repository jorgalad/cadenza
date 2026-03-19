"""Property-based round-trip tests for CN parse/serialize and JSON encode/decode.

Tests CN round-trip (parse_cn/to_cn), JSON round-trip (to_json/from_json),
cross-format round-trips, and explicit edge cases.

CN-dependent tests are skipped if the CN parser (plan 01-02) is not yet available.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, HealthCheck

from cadenza.core import Pitch, Duration, Note, Rest, to_json, from_json
from tests.strategies import (
    note_strategy,
    rest_strategy,
    phrase_strategy,
    phrase_with_rests_strategy,
)


def _resolve_sticky(phrase: tuple) -> tuple:
    """Resolve sticky parameters to produce the canonical form of a phrase.

    CN uses sticky parameters: when a note omits dynamic or articulations,
    the previous values carry forward. After serializing to CN and reparsing,
    originally-None dynamics and empty articulations become the inherited values.
    This helper simulates that normalization for comparison.
    """
    resolved = []
    prev_dynamic: str | None = None
    prev_articulations: tuple[str, ...] = ()
    for event in phrase:
        if isinstance(event, Note):
            # Sticky dynamic: None means "inherit previous"
            dyn = event.dynamic if event.dynamic is not None else prev_dynamic
            # Sticky articulations: () means "inherit previous"
            artics = event.articulations if event.articulations else prev_articulations
            resolved.append(Note(
                pitch=event.pitch,
                duration=event.duration,
                dynamic=dyn,
                articulations=artics,
            ))
            if event.dynamic is not None:
                prev_dynamic = event.dynamic
            if event.articulations:
                prev_articulations = event.articulations
        else:
            # Rest doesn't reset sticky state
            resolved.append(event)
    return tuple(resolved)

# Detect whether the CN parser is available (plan 01-02)
try:
    from cadenza.cn import parse_cn, to_cn  # type: ignore[import-untyped]
    HAS_CN = True
except ImportError:
    HAS_CN = False

cn_required = pytest.mark.skipif(not HAS_CN, reason="CN parser not available (plan 01-02)")


# ---------------------------------------------------------------------------
# Property-based CN round-trip tests
# ---------------------------------------------------------------------------


@cn_required
@given(note=note_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_cn_round_trip_single_note(note: Note) -> None:
    """A single Note serialized to CN and re-parsed preserves all fields."""
    cn_str = to_cn((note,))
    parsed, warnings = parse_cn(cn_str)
    assert len(parsed) == 1
    result = parsed[0]
    assert isinstance(result, Note)
    assert result.pitch == note.pitch
    assert result.duration.fraction == note.duration.fraction
    assert result.dynamic == note.dynamic
    assert result.articulations == note.articulations


@cn_required
@given(rest=rest_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_cn_round_trip_single_rest(rest: Rest) -> None:
    """A single Rest serialized to CN and re-parsed preserves duration."""
    cn_str = to_cn((rest,))
    parsed, warnings = parse_cn(cn_str)
    assert len(parsed) == 1
    assert isinstance(parsed[0], Rest)
    assert parsed[0].duration.fraction == rest.duration.fraction


@cn_required
@given(phrase=phrase_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_cn_round_trip_phrase(phrase: tuple) -> None:
    """A Phrase round-trips through CN: parse_cn(to_cn(phrase)) preserves structure.

    Note: CN uses sticky parameters, so None dynamics and empty articulations
    become inherited values after round-trip. We compare against the sticky-resolved
    version of the original phrase.
    """
    cn_str = to_cn(phrase)
    parsed, warnings = parse_cn(cn_str)
    expected = _resolve_sticky(phrase)
    assert len(parsed) == len(expected)
    for original, reparsed in zip(expected, parsed):
        assert type(original) == type(reparsed)
        if isinstance(original, Note):
            assert reparsed.pitch == original.pitch
            assert reparsed.duration.fraction == original.duration.fraction
            assert reparsed.dynamic == original.dynamic
            assert reparsed.articulations == original.articulations
        else:  # Rest
            assert reparsed.duration.fraction == original.duration.fraction


@given(phrase=phrase_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_json_round_trip_phrase(phrase: tuple) -> None:
    """A Phrase round-trips through JSON: from_json(to_json(phrase)) == phrase."""
    json_str = to_json(phrase)
    restored = from_json(json_str)
    # from_json returns a tuple (via the tuple _type handler)
    assert restored == phrase


@cn_required
@given(phrase=phrase_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_cn_idempotent(phrase: tuple) -> None:
    """After first CN round-trip, subsequent round-trips are stable (idempotent)."""
    cn1 = to_cn(phrase)
    p1, _ = parse_cn(cn1)
    cn2 = to_cn(p1)
    p2, _ = parse_cn(cn2)
    # After first round-trip, serialized form is stable
    assert cn2 == to_cn(p2)


@cn_required
@given(phrase=phrase_strategy())
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_cross_format_round_trip(phrase: tuple) -> None:
    """CN -> parse -> JSON -> from_json -> to_cn -> parse gives same Phrase."""
    # CN -> parse
    cn1 = to_cn(phrase)
    p1, _ = parse_cn(cn1)
    # JSON round-trip
    json_str = to_json(p1)
    p2 = from_json(json_str)
    if isinstance(p2, list):
        p2 = tuple(p2)
    # Back to CN
    cn2 = to_cn(p2)
    p3, _ = parse_cn(cn2)
    # Compare structurally
    assert len(p1) == len(p3)
    for a, b in zip(p1, p3):
        assert type(a) == type(b)
        if isinstance(a, Note):
            assert a.pitch == b.pitch
            assert a.duration.fraction == b.duration.fraction
            assert a.dynamic == b.dynamic
            assert a.articulations == b.articulations
        else:  # Rest
            assert a.duration.fraction == b.duration.fraction


# ---------------------------------------------------------------------------
# Explicit edge case tests (not property-based)
# ---------------------------------------------------------------------------


@cn_required
def test_empty_phrase_round_trip() -> None:
    """Empty phrase round-trips through CN."""
    cn_str = to_cn(())
    assert cn_str == ""
    parsed, warnings = parse_cn("")
    assert len(parsed) == 0


@cn_required
def test_single_rest_round_trip() -> None:
    """A single rest round-trips through CN."""
    rest = Rest(Duration.from_cn("q"))
    cn_str = to_cn((rest,))
    parsed, warnings = parse_cn(cn_str)
    assert len(parsed) == 1
    assert isinstance(parsed[0], Rest)
    assert parsed[0].duration.fraction == rest.duration.fraction


@cn_required
def test_all_dynamics_round_trip() -> None:
    """Phrase with each of 8 dynamics round-trips through CN."""
    dynamics = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
    events: list[Note] = []
    for i, dyn in enumerate(dynamics):
        pitch = Pitch("c", "n", 4)
        dur = Duration.from_cn("q")
        events.append(Note(pitch=pitch, duration=dur, dynamic=dyn))
    phrase = tuple(events)
    cn_str = to_cn(phrase)
    parsed, warnings = parse_cn(cn_str)
    assert len(parsed) == len(phrase)
    for orig, reparsed in zip(phrase, parsed):
        assert isinstance(reparsed, Note)
        assert reparsed.dynamic == orig.dynamic


@cn_required
def test_tuplet_round_trip() -> None:
    """Tuplet durations round-trip through CN."""
    cn_input = "3q c4 d4 e4"
    parsed, warnings = parse_cn(cn_input)
    assert len(parsed) == 3
    cn_output = to_cn(parsed)
    reparsed, _ = parse_cn(cn_output)
    assert len(reparsed) == 3
    for orig, rep in zip(parsed, reparsed):
        assert isinstance(orig, Note)
        assert isinstance(rep, Note)
        assert orig.duration.fraction == rep.duration.fraction
        assert orig.pitch == rep.pitch


@cn_required
def test_dotted_round_trip() -> None:
    """Dotted durations round-trip through CN."""
    cn_input = "q. c4 e. d4"
    parsed, warnings = parse_cn(cn_input)
    assert len(parsed) == 2
    cn_output = to_cn(parsed)
    reparsed, _ = parse_cn(cn_output)
    assert len(reparsed) == 2
    for orig, rep in zip(parsed, reparsed):
        assert isinstance(orig, Note)
        assert isinstance(rep, Note)
        assert orig.duration.fraction == rep.duration.fraction
        assert orig.pitch == rep.pitch


@cn_required
def test_double_accidentals_round_trip() -> None:
    """Double-sharp and double-flat pitches round-trip through CN."""
    cn_input = "q css4 dbb3"
    parsed, warnings = parse_cn(cn_input)
    assert len(parsed) == 2
    assert isinstance(parsed[0], Note)
    assert parsed[0].pitch.accidental == "ss"
    assert isinstance(parsed[1], Note)
    assert parsed[1].pitch.accidental == "bb"
    cn_output = to_cn(parsed)
    reparsed, _ = parse_cn(cn_output)
    assert len(reparsed) == 2
    for orig, rep in zip(parsed, reparsed):
        assert isinstance(orig, Note)
        assert isinstance(rep, Note)
        assert orig.pitch == rep.pitch


@cn_required
def test_mixed_notes_rests_round_trip() -> None:
    """A phrase mixing Notes and Rests round-trips through CN."""
    cn_input = "q c4 -e q d4"
    parsed, warnings = parse_cn(cn_input)
    assert len(parsed) == 3
    assert isinstance(parsed[0], Note)
    assert isinstance(parsed[1], Rest)
    assert isinstance(parsed[2], Note)
    cn_output = to_cn(parsed)
    reparsed, _ = parse_cn(cn_output)
    assert len(reparsed) == 3
    for orig, rep in zip(parsed, reparsed):
        assert type(orig) == type(rep)
        if isinstance(orig, Note):
            assert orig.pitch == rep.pitch
            assert orig.duration.fraction == rep.duration.fraction
        else:
            assert orig.duration.fraction == rep.duration.fraction


# ---------------------------------------------------------------------------
# JSON-only edge case tests (no CN dependency)
# ---------------------------------------------------------------------------


def test_json_round_trip_empty_phrase() -> None:
    """Empty phrase round-trips through JSON."""
    phrase: tuple = ()
    json_str = to_json(phrase)
    restored = from_json(json_str)
    assert restored == phrase


def test_json_round_trip_single_note() -> None:
    """A single Note round-trips through JSON with full fidelity."""
    note = Note(
        pitch=Pitch("e", "b", 3),
        duration=Duration.from_cn("q", dots=1),
        dynamic="mf",
        articulations=("stacc", "ten"),
    )
    json_str = to_json(note)
    restored = from_json(json_str)
    assert restored == note


def test_json_round_trip_rest() -> None:
    """A single Rest round-trips through JSON."""
    rest = Rest(Duration.from_cn("e", tuplet=3))
    json_str = to_json(rest)
    restored = from_json(json_str)
    assert restored == rest


def test_json_round_trip_complex_phrase() -> None:
    """A complex phrase with mixed events round-trips through JSON."""
    phrase = (
        Note(Pitch("c", "n", 4), Duration.from_cn("q"), "mf", ("stacc",)),
        Rest(Duration.from_cn("e")),
        Note(Pitch("e", "b", 3), Duration.from_cn("h", dots=1), "pp", ()),
        Note(Pitch("f", "ss", 5), Duration.from_cn("s", tuplet=3), "fff", ("ten", "acc")),
        Rest(Duration.from_cn("w")),
    )
    json_str = to_json(phrase)
    restored = from_json(json_str)
    assert restored == phrase
