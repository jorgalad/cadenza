"""Analysis subpackage: chord identification, key detection, and harmonic analysis."""

from cadenza.analysis.chords import (
    ChordMatch,
    chord_symbol,
    identify_chord,
    parse_chord_symbol,
    realize_chord,
)
from cadenza.analysis.harmony import (
    HarmonicBeat,
    RomanNumeral,
    harmonic_rhythm,
    roman_numeral,
)
from cadenza.analysis.keys import (
    KeyResult,
    Modulation,
    detect_key,
    detect_modulations,
)

__all__ = [
    "ChordMatch",
    "HarmonicBeat",
    "KeyResult",
    "Modulation",
    "RomanNumeral",
    "chord_symbol",
    "detect_key",
    "detect_modulations",
    "harmonic_rhythm",
    "identify_chord",
    "parse_chord_symbol",
    "realize_chord",
    "roman_numeral",
]
