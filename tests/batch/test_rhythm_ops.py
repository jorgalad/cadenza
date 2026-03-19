"""Tests for cadenza.batch.rhythm_ops — BATCH-05."""

from __future__ import annotations

from fractions import Fraction

from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.pitch import Pitch
from cadenza.batch.rhythm_ops import quantize_lengths


def _make_note(base: str = "q") -> Note:
    return Note(
        pitch=Pitch("c", "n", 4),
        duration=Duration.from_cn(base),
    )


# ---------------------------------------------------------------------------
# BATCH-05: quantize_lengths
# ---------------------------------------------------------------------------

class TestQuantizeLengths:
    def test_snap_to_eighth(self):
        """Quantize to nearest 1/8 grid."""
        # A dotted eighth (3/16) should snap to nearest eighth (1/8 = 2/16)
        dotted_e = Note(
            pitch=Pitch("c", "n", 4),
            duration=Duration.from_cn("e", dots=1),  # 3/16
        )
        plain_q = _make_note("q")  # 1/4
        phrase = (dotted_e, plain_q)
        result = quantize_lengths(phrase, ["e", "q"])
        # Dotted eighth (3/16) is closer to eighth (2/16) than quarter (4/16)
        assert result[0].duration.fraction == Fraction(1, 8)
        # Quarter stays quarter
        assert result[1].duration.fraction == Fraction(1, 4)

    def test_rests_quantized_too(self):
        rest = Rest(duration=Duration.from_cn("e", dots=1))  # 3/16
        phrase = (rest,)
        result = quantize_lengths(phrase, ["e", "q"])
        assert result[0].duration.fraction == Fraction(1, 8)
