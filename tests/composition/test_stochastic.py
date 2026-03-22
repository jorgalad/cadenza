"""Tests for stochastic melody generators (ALGO-04, ALGO-05, ALGO-06)."""

from __future__ import annotations

import pytest

from cadenza.core.duration import Duration
from cadenza.core.note import Note
from cadenza.core.phrase import Phrase
from cadenza.core.pitch import Pitch
from cadenza.theory.scales import Scale, get_scale
from cadenza.composition.stochastic import (
    probabilistic_melody,
    tendency_mask_melody,
    random_walk,
)


# --- Helpers ---

C4 = Pitch(step="c", accidental="n", octave=4)
D4 = Pitch(step="d", accidental="n", octave=4)
E4 = Pitch(step="e", accidental="n", octave=4)


def _c_major_scale() -> Scale:
    return get_scale(Pitch(step="c", accidental="n", octave=4), "major")


# === probabilistic_melody ===


class TestProbabilisticMelody:
    def test_probabilistic_melody_seeded(self) -> None:
        weights = {C4: 0.5, D4: 0.3, E4: 0.2}
        a = probabilistic_melody(weights, 10, seed=42)
        b = probabilistic_melody(weights, 10, seed=42)
        assert a == b

    def test_probabilistic_melody_respects_weights(self) -> None:
        weights = {C4: 1.0, D4: 0.0}
        result = probabilistic_melody(weights, 10, seed=42)
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch == C4

    def test_probabilistic_melody_length(self) -> None:
        weights = {C4: 0.5, D4: 0.5}
        result = probabilistic_melody(weights, 15, seed=42)
        assert len(result) == 15

    def test_probabilistic_melody_invalid_length(self) -> None:
        with pytest.raises(ValueError):
            probabilistic_melody({C4: 1.0}, 0, seed=42)

    def test_probabilistic_melody_empty_weights(self) -> None:
        with pytest.raises(ValueError):
            probabilistic_melody({}, 5, seed=42)


# === tendency_mask_melody ===


class TestTendencyMaskMelody:
    @staticmethod
    def _rising_mask(t: float) -> dict[Pitch, float]:
        """Returns low pitches at t=0, high pitches at t=1."""
        low = Pitch(step="c", accidental="n", octave=3)
        high = Pitch(step="c", accidental="n", octave=6)
        return {low: 1.0 - t, high: t} if t > 0.0 else {low: 1.0, high: 0.0}

    def test_tendency_mask_low_to_high(self) -> None:
        result = tendency_mask_melody(self._rising_mask, 20, seed=42)
        midis = [e.pitch.midi_number for e in result if isinstance(e, Note)]
        first_half_avg = sum(midis[:10]) / 10
        second_half_avg = sum(midis[10:]) / 10
        assert first_half_avg < second_half_avg

    def test_tendency_mask_seeded(self) -> None:
        a = tendency_mask_melody(self._rising_mask, 10, seed=42)
        b = tendency_mask_melody(self._rising_mask, 10, seed=42)
        assert a == b

    def test_tendency_mask_length(self) -> None:
        result = tendency_mask_melody(self._rising_mask, 12, seed=42)
        assert len(result) == 12


# === random_walk ===


class TestRandomWalk:
    def test_random_walk_stays_in_scale(self) -> None:
        scale = _c_major_scale()
        result = random_walk(C4, 20, scale, max_step=2, seed=42)
        scale_pcs = {sp.pitch_class for sp in scale.pitches}
        for event in result:
            assert isinstance(event, Note)
            assert event.pitch.pitch_class in scale_pcs

    def test_random_walk_step_constraint(self) -> None:
        scale = _c_major_scale()
        result = random_walk(C4, 20, scale, max_step=2, seed=42)
        midis = [e.pitch.midi_number for e in result if isinstance(e, Note)]
        for i in range(len(midis) - 1):
            assert abs(midis[i + 1] - midis[i]) <= 2

    def test_random_walk_seeded(self) -> None:
        scale = _c_major_scale()
        a = random_walk(C4, 10, scale, max_step=2, seed=42)
        b = random_walk(C4, 10, scale, max_step=2, seed=42)
        assert a == b

    def test_random_walk_length(self) -> None:
        scale = _c_major_scale()
        result = random_walk(C4, 15, scale, max_step=2, seed=42)
        assert len(result) == 15

    def test_random_walk_invalid_length(self) -> None:
        scale = _c_major_scale()
        with pytest.raises(ValueError):
            random_walk(C4, 0, scale, max_step=2, seed=42)

    def test_random_walk_invalid_max_step(self) -> None:
        scale = _c_major_scale()
        with pytest.raises(ValueError):
            random_walk(C4, 10, scale, max_step=0, seed=42)
