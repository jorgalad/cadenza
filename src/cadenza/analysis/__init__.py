"""Analysis subpackage: chord identification, key detection, harmonic and phrase analysis."""

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
from cadenza.analysis.phrases import (
    MotifMatch,
    SequenceMatch,
    ambitus,
    complexity_score,
    detect_sequence,
    find_motifs,
    interval_sequence,
    melodic_contour,
    phrase_similarity,
    pitch_class_histogram,
    rhythmic_density,
)

__all__ = [
    "ChordMatch",
    "HarmonicBeat",
    "KeyResult",
    "Modulation",
    "MotifMatch",
    "RomanNumeral",
    "SequenceMatch",
    "ambitus",
    "chord_symbol",
    "complexity_score",
    "detect_key",
    "detect_modulations",
    "detect_sequence",
    "find_motifs",
    "harmonic_rhythm",
    "identify_chord",
    "interval_sequence",
    "melodic_contour",
    "parse_chord_symbol",
    "phrase_similarity",
    "pitch_class_histogram",
    "realize_chord",
    "rhythmic_density",
    "roman_numeral",
]
