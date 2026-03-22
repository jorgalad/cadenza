"""Analysis endpoints -- thin route handlers calling cadenza.analysis."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.helpers import (
    _parse_phrase,
    _phrase_response,
    _pitch_to_cn,
    _pitch_tuple_response,
    _pitches_to_cn,
    _safe_parse_pitch,
    _score_response,
)
from cadenza.api.schemas import (
    CheckVoiceLeadingRequest,
    DetectKeyRequest,
    DetectModulationsRequest,
    FindMotifsRequest,
    GenerateInnerVoicesRequest,
    HarmonicRhythmRequest,
    IdentifyChordRequest,
    PhraseOnlyRequest,
    RealizeChordRequest,
    RomanNumeralRequest,
    SmoothVoiceLeadingRequest,
    TwoPhraseRequest,
)
from cadenza.analysis import (
    KeyResult,
    ambitus,
    check_voice_leading,
    complexity_score,
    detect_key,
    detect_modulations,
    detect_sequence,
    find_motifs,
    generate_inner_voices,
    harmonic_rhythm,
    identify_chord,
    interval_sequence,
    melodic_contour,
    phrase_similarity,
    pitch_class_histogram,
    realize_chord,
    rhythmic_density,
    roman_numeral,
    smooth_voice_leading,
)
from cadenza.cn import to_cn
from cadenza.core.score import Score

router = APIRouter(prefix="/v1/analysis", tags=["analysis"])


# ---------------------------------------------------------------------------
# Chord / key endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/identify-chord",
    response_model=None,
    summary="Identify chord from pitches",
    description="Parse space-separated pitch strings and identify the chord quality, root, and inversion.",
)
def identify_chord_endpoint(req: IdentifyChordRequest) -> dict:
    pitches = tuple(_safe_parse_pitch(p) for p in req.pitches.split())
    result = identify_chord(pitches)
    return {
        "root": _pitch_to_cn(result.root),
        "symbol": result.symbol,
        "inversion": result.inversion,
        "pitches": _pitches_to_cn(result.pitches),
    }


@router.post(
    "/detect-key",
    response_model=None,
    summary="Detect key of a phrase",
    description="Analyze a CN phrase and return the most likely key with confidence score.",
)
def detect_key_endpoint(req: DetectKeyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = detect_key(phrase)
    return {
        "root": _pitch_to_cn(result.root),
        "mode": result.mode,
        "confidence": result.confidence,
    }


@router.post(
    "/roman-numeral",
    response_model=None,
    summary="Analyze chord as Roman numeral in key",
    description="Identify a chord from pitches and label it as a Roman numeral within the given key context.",
)
def roman_numeral_endpoint(req: RomanNumeralRequest) -> dict:
    pitches = tuple(_safe_parse_pitch(p) for p in req.pitches.split())
    chord = identify_chord(pitches)
    key_root = _safe_parse_pitch(req.key_root)
    key = KeyResult(root=key_root, mode=req.key_mode, confidence=1.0)
    rn = roman_numeral(chord, key)
    return {
        "numeral": rn.numeral,
        "function": rn.function,
    }


@router.post(
    "/harmonic-rhythm",
    response_model=None,
    summary="Analyze harmonic rhythm of a phrase",
    description="Detect chord changes and their positions within a phrase, labeling each with Roman numeral analysis.",
)
def harmonic_rhythm_endpoint(req: HarmonicRhythmRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    key_root = _safe_parse_pitch(req.key_root)
    key = KeyResult(root=key_root, mode=req.key_mode, confidence=1.0)
    beats = harmonic_rhythm(phrase, key)
    return {
        "beats": [
            {
                "onset": str(hb.onset),
                "duration": str(hb.duration),
                "chord_root": _pitch_to_cn(hb.chord.root),
                "chord_symbol": hb.chord.symbol,
                "numeral": hb.numeral.numeral,
                "function": hb.numeral.function,
            }
            for hb in beats
        ],
    }


@router.post(
    "/detect-modulations",
    response_model=None,
    summary="Detect key modulations in a phrase",
    description="Use a sliding window to find points where the key changes within a phrase.",
)
def detect_modulations_endpoint(req: DetectModulationsRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    mods = detect_modulations(phrase, req.window)
    return {
        "modulations": [
            {
                "position": m.position,
                "from_key": {
                    "root": _pitch_to_cn(m.from_key.root),
                    "mode": m.from_key.mode,
                },
                "to_key": {
                    "root": _pitch_to_cn(m.to_key.root),
                    "mode": m.to_key.mode,
                },
            }
            for m in mods
        ],
    }


@router.post(
    "/realize-chord",
    response_model=None,
    summary="Realize chord from root and symbol",
    description="Build a chord voicing from a root pitch and chord symbol, with optional inversion.",
)
def realize_chord_endpoint(req: RealizeChordRequest) -> dict:
    root = _safe_parse_pitch(req.root)
    pitches = realize_chord(root, req.symbol, req.inversion)
    return _pitch_tuple_response(pitches)


# ---------------------------------------------------------------------------
# Voice leading endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/check-voice-leading",
    response_model=None,
    summary="Check voice leading for violations",
    description="Parse multiple voice parts and check for parallel fifths, octaves, and other voice leading errors.",
)
def check_voice_leading_endpoint(req: CheckVoiceLeadingRequest) -> dict:
    phrases = [_parse_phrase(v) for v in req.voices]
    voice_pairs: list[tuple[str, tuple]] = []
    for i, p in enumerate(phrases):
        voice_pairs.append((f"voice_{i}", p))
    score = Score(*[item for pair in voice_pairs for item in pair])
    violations = check_voice_leading(score)
    return {
        "violations": [
            {
                "rule": v.rule,
                "voice1": v.voice1,
                "voice2": v.voice2,
                "position": v.position,
                "severity": v.severity,
            }
            for v in violations
        ],
    }


@router.post(
    "/smooth-voice-leading",
    response_model=None,
    summary="Find smooth voice leading between chords",
    description="Rearrange the second chord's pitches for minimal voice movement from the first chord.",
)
def smooth_voice_leading_endpoint(req: SmoothVoiceLeadingRequest) -> dict:
    c1 = tuple(_safe_parse_pitch(p) for p in req.chord1.split())
    c2 = tuple(_safe_parse_pitch(p) for p in req.chord2.split())
    result = smooth_voice_leading(c1, c2)
    return _pitch_tuple_response(result)


@router.post(
    "/generate-inner-voices",
    response_model=None,
    summary="Generate inner voices between soprano and bass",
    description="Create inner voice parts that connect soprano and bass lines with smooth voice leading.",
)
def generate_inner_voices_endpoint(req: GenerateInnerVoicesRequest) -> dict:
    soprano = _parse_phrase(req.soprano)
    bass = _parse_phrase(req.bass)
    voices = generate_inner_voices(soprano, bass, req.n)
    return {"voices": [_phrase_response(v) for v in voices]}


# ---------------------------------------------------------------------------
# Phrase analysis endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/ambitus",
    response_model=None,
    summary="Get the pitch range of a phrase",
    description="Return the lowest and highest pitches in a phrase.",
)
def ambitus_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    low, high = ambitus(phrase)
    return {"low": _pitch_to_cn(low), "high": _pitch_to_cn(high)}


@router.post(
    "/melodic-contour",
    response_model=None,
    summary="Get melodic contour of a phrase",
    description="Return a list of directional movements (up, down, same) between consecutive notes.",
)
def melodic_contour_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = melodic_contour(phrase)
    return {"contour": result}


@router.post(
    "/interval-sequence",
    response_model=None,
    summary="Get interval sequence of a phrase",
    description="Return the sequence of melodic intervals between consecutive notes.",
)
def interval_sequence_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    ivs = interval_sequence(phrase)
    return {
        "intervals": [
            {"quality": iv.quality, "number": iv.number}
            for iv in ivs
        ],
    }


@router.post(
    "/pitch-class-histogram",
    response_model=None,
    summary="Get pitch class distribution",
    description="Return a histogram mapping pitch classes (0-11) to occurrence counts.",
)
def pitch_class_histogram_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = pitch_class_histogram(phrase)
    return {"histogram": result}


@router.post(
    "/rhythmic-density",
    response_model=None,
    summary="Get rhythmic density of a phrase",
    description="Return the number of note onsets per beat division.",
)
def rhythmic_density_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = rhythmic_density(phrase)
    return {"density": result}


@router.post(
    "/complexity-score",
    response_model=None,
    summary="Calculate complexity score of a phrase",
    description="Return a single floating-point score estimating the musical complexity of a phrase.",
)
def complexity_score_endpoint(req: PhraseOnlyRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    result = complexity_score(phrase)
    return {"score": result}


@router.post(
    "/find-motifs",
    response_model=None,
    summary="Find recurring motifs in a phrase",
    description="Detect repeated melodic patterns within a phrase, returning each motif and its positions.",
)
def find_motifs_endpoint(req: FindMotifsRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    motifs = find_motifs(phrase, req.min_length)
    return {
        "motifs": [
            {"phrase": to_cn(m.motif), "positions": list(m.positions)}
            for m in motifs
        ],
    }


@router.post(
    "/phrase-similarity",
    response_model=None,
    summary="Compare two phrases for similarity",
    description="Return a 0.0-1.0 similarity score between two CN phrases.",
)
def phrase_similarity_endpoint(req: TwoPhraseRequest) -> dict:
    p1 = _parse_phrase(req.phrase)
    p2 = _parse_phrase(req.phrase2)
    result = phrase_similarity(p1, p2)
    return {"similarity": result}


@router.post(
    "/detect-sequence",
    response_model=None,
    summary="Detect sequential patterns between phrases",
    description="Find exact or transposed sequential imitations between two phrases.",
)
def detect_sequence_endpoint(req: TwoPhraseRequest) -> dict:
    p1 = _parse_phrase(req.phrase)
    p2 = _parse_phrase(req.phrase2)
    matches = detect_sequence(p1, p2)
    return {
        "matches": [
            {
                "match_type": m.match_type,
                "offset": m.offset,
                "transposition": (
                    {"quality": m.transposition.quality, "number": m.transposition.number}
                    if m.transposition
                    else None
                ),
            }
            for m in matches
        ],
    }
