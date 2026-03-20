"""Tests for counterpoint validation: rules engine and check_counterpoint."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.counterpoint.rules import (
    DISSONANCES,
    IMPERFECT_CONSONANCES,
    PERFECT_CONSONANCES,
    classify_interval,
)
from cadenza.counterpoint.validation import (
    CounterpointViolation,
    check_counterpoint,
)

from .conftest import make_phrase


# ---------------------------------------------------------------------------
# classify_interval tests
# ---------------------------------------------------------------------------


class TestClassifyInterval:
    """Test consonance classification by semitones mod 12."""

    def test_perfect_consonances(self) -> None:
        assert classify_interval(0) == "perfect"
        assert classify_interval(7) == "perfect"

    def test_imperfect_consonances(self) -> None:
        for s in (3, 4, 8, 9):
            assert classify_interval(s) == "imperfect", f"Failed for {s}"

    def test_dissonances(self) -> None:
        for s in (1, 2, 5, 6, 10, 11):
            assert classify_interval(s) == "dissonant", f"Failed for {s}"


# ---------------------------------------------------------------------------
# CounterpointViolation dataclass tests
# ---------------------------------------------------------------------------


class TestCounterpointViolation:
    """Test CounterpointViolation is a frozen dataclass with expected fields."""

    def test_is_frozen_dataclass(self) -> None:
        from cadenza.core.interval import Interval

        v = CounterpointViolation(
            rule="parallel_fifth",
            species=1,
            position=1,
            interval=Interval(quality="P", number=5, direction=1),
            severity="error",
        )
        assert v.rule == "parallel_fifth"
        assert v.species == 1
        assert v.position == 1
        assert v.severity == "error"

        with pytest.raises(AttributeError):
            v.rule = "something_else"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# check_counterpoint tests
# ---------------------------------------------------------------------------


class TestCheckCounterpoint:
    """Test check_counterpoint validation function."""

    def test_parallel_fifths_detected(self) -> None:
        """CF C4->D4, CP G4->A4: both P5, same direction = parallel fifth."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("a", "n", 4)])
        violations = check_counterpoint(cf, cp, species=1)
        pf = [v for v in violations if v.rule == "parallel_fifth"]
        assert len(pf) >= 1
        assert pf[0].severity == "error"

    def test_parallel_octaves_detected(self) -> None:
        """CF C4->D4, CP C5->D5: both P8, same direction = parallel octave."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("c", "n", 5), ("d", "n", 5)])
        violations = check_counterpoint(cf, cp, species=1)
        po = [v for v in violations if v.rule == "parallel_octave"]
        assert len(po) >= 1
        assert po[0].severity == "error"

    def test_dissonance_on_beat_detected(self) -> None:
        """CP F#4 against CF C4 = tritone (6 semitones) = dissonant."""
        cf = make_phrase([("c", "n", 4)])
        cp = make_phrase([("f", "s", 4)])
        violations = check_counterpoint(cf, cp, species=1)
        dis = [v for v in violations if v.rule == "dissonance_on_beat"]
        assert len(dis) >= 1
        assert dis[0].severity == "error"

    def test_voice_crossing_detected(self) -> None:
        """CP note below CF note when CP should be above."""
        cf = make_phrase([("c", "n", 4), ("e", "n", 4)])
        # CP goes below CF at position 1
        cp = make_phrase([("c", "n", 5), ("d", "n", 4)])
        violations = check_counterpoint(cf, cp, species=1)
        vc = [v for v in violations if v.rule == "voice_crossing"]
        assert len(vc) >= 1
        assert vc[0].severity == "error"

    def test_violations_sorted_by_position(self) -> None:
        """Violations should be sorted by position."""
        # Create a phrase with violations at different positions
        cf = make_phrase([
            ("c", "n", 4), ("d", "n", 4), ("e", "n", 4),
        ])
        # CP has dissonance at pos 0 and pos 2
        cp = make_phrase([
            ("f", "s", 4), ("a", "n", 4), ("f", "n", 4),
        ])
        violations = check_counterpoint(cf, cp, species=1)
        positions = [v.position for v in violations]
        assert positions == sorted(positions)

    def test_severity_override_via_rules(self) -> None:
        """Custom rules dict overrides severity for specified rules."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("a", "n", 4)])
        violations = check_counterpoint(
            cf, cp, species=1, rules={"parallel_fifth": "warning"}
        )
        pf = [v for v in violations if v.rule == "parallel_fifth"]
        assert len(pf) >= 1
        assert pf[0].severity == "warning"

    def test_rules_none_uses_defaults(self) -> None:
        """rules=None uses all default severities."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("a", "n", 4)])
        violations = check_counterpoint(cf, cp, species=1, rules=None)
        pf = [v for v in violations if v.rule == "parallel_fifth"]
        assert len(pf) >= 1
        assert pf[0].severity == "error"

    def test_valid_first_species_no_violations(self, cf_c_major) -> None:
        """Valid first species counterpoint should have no error violations."""
        # All consonant with CF, no parallel fifths/octaves, no crossings
        cp = make_phrase([
            ("e", "n", 5),
            ("d", "n", 5),
            ("a", "n", 4),
            ("c", "n", 5),
            ("c", "n", 5),
            ("b", "n", 4),
            ("a", "n", 4),
            ("c", "n", 5),
        ])
        violations = check_counterpoint(cf_c_major, cp, species=1)
        errors = [v for v in violations if v.severity == "error"]
        assert errors == []

    def test_large_leap_detected(self) -> None:
        """Leap > 12 semitones should produce large_leap warning."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        # CP jumps from C5 to E6 = 16 semitones
        cp = make_phrase([("c", "n", 5), ("e", "n", 6)])
        violations = check_counterpoint(cf, cp, species=1)
        ll = [v for v in violations if v.rule == "large_leap"]
        assert len(ll) >= 1
        assert ll[0].severity == "warning"

    def test_repeated_note_detected(self) -> None:
        """Same note repeated should produce repeated_note warning."""
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("g", "n", 4)])
        violations = check_counterpoint(cf, cp, species=1)
        rn = [v for v in violations if v.rule == "repeated_note"]
        assert len(rn) >= 1
        assert rn[0].severity == "warning"


# ---------------------------------------------------------------------------
# Species 2 validation tests
# ---------------------------------------------------------------------------


class TestCheckCounterpointSpecies2:
    """Test check_counterpoint with species=2."""

    def test_offbeat_passing_tone_not_flagged(self) -> None:
        """A consonant passing tone on an offbeat should not be flagged."""
        # CF: C4, D4 (2 notes = 4 CP notes in species 2)
        # CP: G4(consonant), A4(consonant step), A4(consonant), B4(consonant step)
        cf = make_phrase([("c", "n", 4), ("d", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("a", "n", 4), ("a", "n", 4), ("b", "n", 4)], base="h")
        violations = check_counterpoint(cf, cp, species=2)
        errors = [v for v in violations if v.severity == "error"]
        # No errors expected -- all notes are consonant
        dissonances = [v for v in errors if v.rule == "dissonance_on_beat"]
        assert dissonances == []


# ---------------------------------------------------------------------------
# Species 4 validation tests
# ---------------------------------------------------------------------------


class TestCheckCounterpointSpecies4:
    """Test check_counterpoint with species=4."""

    def test_unresolved_suspension_detected(self) -> None:
        """Dissonant held note not resolved stepwise down -> unresolved_suspension."""
        # CF: C4, D4, E4 (3 notes)
        # CP: G4, E4, B4 -- E4 is dissonant (2nd) with D4, then jumps UP to B4 instead of resolving down
        cf = make_phrase([("c", "n", 4), ("d", "n", 4), ("e", "n", 4)])
        cp = make_phrase([("g", "n", 4), ("e", "n", 4), ("b", "n", 4)])
        violations = check_counterpoint(cf, cp, species=4)
        unresolved = [v for v in violations if v.rule == "unresolved_suspension"]
        assert len(unresolved) >= 1
        assert unresolved[0].severity == "error"
