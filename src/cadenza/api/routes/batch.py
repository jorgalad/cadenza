"""Batch dispatcher endpoint -- execute multiple operations in one request."""

from __future__ import annotations

from fractions import Fraction
from typing import Callable

from fastapi import APIRouter

from cadenza.api.errors import (
    BATCH_TOO_LARGE,
    UNKNOWN_OPERATION,
    CadenzaAPIError,
)
from cadenza.api.helpers import (
    _parse_phrase,
    _phrase_response,
    _pitch_to_cn,
    _pitch_tuple_response,
    _pitches_to_cn,
    _safe_parse_interval,
    _safe_parse_pitch,
)
from cadenza.api.schemas import BatchRequest

router = APIRouter(prefix="/v1", tags=["batch"])


# ---------------------------------------------------------------------------
# Handler factories for common patterns
# ---------------------------------------------------------------------------


def _make_phrase_handler(func: Callable) -> Callable[[dict], dict]:
    """Create a batch handler for func(phrase) -> Phrase pattern."""
    def handler(params: dict) -> dict:
        phrase = _parse_phrase(params["phrase"])
        result = func(phrase)
        return _phrase_response(result)
    return handler


def _make_phrase_n_handler(func: Callable, param_name: str = "n") -> Callable[[dict], dict]:
    """Create a batch handler for func(phrase, n) -> Phrase pattern."""
    def handler(params: dict) -> dict:
        phrase = _parse_phrase(params["phrase"])
        result = func(phrase, params[param_name])
        return _phrase_response(result)
    return handler


def _make_two_pcs_handler(func: Callable) -> Callable[[dict], dict]:
    """Create a batch handler for func(frozenset, frozenset) -> bool pattern."""
    def handler(params: dict) -> dict:
        return {"result": func(frozenset(params["pcs_a"]), frozenset(params["pcs_b"]))}
    return handler


# ---------------------------------------------------------------------------
# Specific handler wrappers (operations with non-standard signatures)
# ---------------------------------------------------------------------------


def _handle_chromatic_transpose(params: dict) -> dict:
    from cadenza.transforms import chromatic_transpose
    phrase = _parse_phrase(params["phrase"])
    interval = _safe_parse_interval(params["interval"])
    return _phrase_response(chromatic_transpose(phrase, interval))


def _handle_diatonic_transpose(params: dict) -> dict:
    from cadenza.core.note import Note
    from cadenza.theory import get_scale
    from cadenza.transforms import diatonic_transpose
    phrase = _parse_phrase(params["phrase"])
    scale = None
    scale_name = params.get("scale_name", "major")
    if scale_name:
        first_pitch = None
        for event in phrase:
            if isinstance(event, Note):
                first_pitch = event.pitch
                break
        if first_pitch is not None:
            scale = get_scale(first_pitch, scale_name)
    return _phrase_response(diatonic_transpose(phrase, params["n"], scale))


def _handle_invert(params: dict) -> dict:
    from cadenza.transforms import invert
    phrase = _parse_phrase(params["phrase"])
    axis = _safe_parse_pitch(params["axis"]) if params.get("axis") else None
    return _phrase_response(invert(phrase, axis))


def _handle_retrograde_inversion(params: dict) -> dict:
    from cadenza.transforms import retrograde_inversion
    phrase = _parse_phrase(params["phrase"])
    axis = _safe_parse_pitch(params["axis"]) if params.get("axis") else None
    return _phrase_response(retrograde_inversion(phrase, axis))


def _handle_augment(params: dict) -> dict:
    from cadenza.transforms import augment
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(augment(phrase, Fraction(params["ratio"]).limit_denominator(1000)))


def _handle_diminish(params: dict) -> dict:
    from cadenza.transforms import diminish
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(diminish(phrase, Fraction(params["ratio"]).limit_denominator(1000)))


def _handle_rotate(params: dict) -> dict:
    from cadenza.transforms import rotate
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(rotate(phrase, params["n"]))


def _handle_rhythmic_rotation(params: dict) -> dict:
    from cadenza.transforms import rhythmic_rotation
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(rhythmic_rotation(phrase, params["n"]))


def _handle_permute(params: dict) -> dict:
    from cadenza.transforms import permute
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(permute(phrase, params["indices"]))


def _handle_interpolate(params: dict) -> dict:
    from cadenza.transforms import interpolate
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(interpolate(phrase, params.get("steps", 1)))


def _handle_omit(params: dict) -> dict:
    from cadenza.transforms import omit
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(omit(phrase, n=params["n"]))


def _handle_repeat(params: dict) -> dict:
    from cadenza.transforms import repeat
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(repeat(phrase, params["n"]))


def _handle_fragment(params: dict) -> dict:
    from cadenza.transforms import fragment
    phrase = _parse_phrase(params["phrase"])
    fragments = fragment(phrase, params["lengths"])
    return {"phrases": [_phrase_response(f) for f in fragments]}


def _handle_concatenate(params: dict) -> dict:
    from cadenza.transforms import concatenate
    parsed = [_parse_phrase(p) for p in params["phrases"]]
    return _phrase_response(concatenate(*parsed))


def _handle_interleave(params: dict) -> dict:
    from cadenza.transforms import interleave
    p1 = _parse_phrase(params["phrase"])
    p2 = _parse_phrase(params["phrase2"])
    return _phrase_response(interleave(p1, p2))


def _handle_quantize(params: dict) -> dict:
    from cadenza.transforms import quantize
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(quantize(phrase, params["grid"]))


def _handle_metric_modulation(params: dict) -> dict:
    from cadenza.transforms import metric_modulation
    phrase = _parse_phrase(params["phrase"])
    old_phrase = _parse_phrase(f"{params['old_unit']} c4")
    new_phrase = _parse_phrase(f"{params['new_unit']} c4")
    return _phrase_response(metric_modulation(phrase, old_phrase[0].duration, new_phrase[0].duration))


def _handle_extract_rhythm(params: dict) -> dict:
    from cadenza.core.json_codec import _to_serializable
    from cadenza.transforms import extract_rhythm
    phrase = _parse_phrase(params["phrase"])
    return {"events": _to_serializable(extract_rhythm(phrase))}


def _handle_total_duration(params: dict) -> dict:
    from cadenza.transforms import total_duration
    phrase = _parse_phrase(params["phrase"])
    result = total_duration(phrase)
    return {"total": str(result), "numerator": result.numerator, "denominator": result.denominator}


# --- Analysis handlers ---


def _handle_identify_chord(params: dict) -> dict:
    from cadenza.analysis import identify_chord
    pitches = tuple(_safe_parse_pitch(p) for p in params["pitches"].split())
    result = identify_chord(pitches)
    return {
        "root": _pitch_to_cn(result.root),
        "symbol": result.symbol,
        "inversion": result.inversion,
        "pitches": _pitches_to_cn(result.pitches),
    }


def _handle_detect_key(params: dict) -> dict:
    from cadenza.analysis import detect_key
    phrase = _parse_phrase(params["phrase"])
    result = detect_key(phrase)
    return {"root": _pitch_to_cn(result.root), "mode": result.mode, "confidence": result.confidence}


def _handle_roman_numeral(params: dict) -> dict:
    from cadenza.analysis import KeyResult, identify_chord, roman_numeral
    pitches = tuple(_safe_parse_pitch(p) for p in params["pitches"].split())
    chord = identify_chord(pitches)
    key_root = _safe_parse_pitch(params["key_root"])
    key = KeyResult(root=key_root, mode=params.get("key_mode", "major"), confidence=1.0)
    rn = roman_numeral(chord, key)
    return {"numeral": rn.numeral, "function": rn.function}


def _handle_detect_modulations(params: dict) -> dict:
    from cadenza.analysis import detect_modulations
    phrase = _parse_phrase(params["phrase"])
    mods = detect_modulations(phrase, params.get("window", 4))
    return {
        "modulations": [
            {
                "position": m.position,
                "from_key": {"root": _pitch_to_cn(m.from_key.root), "mode": m.from_key.mode},
                "to_key": {"root": _pitch_to_cn(m.to_key.root), "mode": m.to_key.mode},
            }
            for m in mods
        ]
    }


def _handle_ambitus(params: dict) -> dict:
    from cadenza.analysis import ambitus
    phrase = _parse_phrase(params["phrase"])
    low, high = ambitus(phrase)
    return {"low": _pitch_to_cn(low), "high": _pitch_to_cn(high)}


def _handle_melodic_contour(params: dict) -> dict:
    from cadenza.analysis import melodic_contour
    phrase = _parse_phrase(params["phrase"])
    return {"contour": melodic_contour(phrase)}


def _handle_interval_sequence(params: dict) -> dict:
    from cadenza.analysis import interval_sequence
    phrase = _parse_phrase(params["phrase"])
    ivs = interval_sequence(phrase)
    return {"intervals": [{"quality": iv.quality, "number": iv.number} for iv in ivs]}


def _handle_pitch_class_histogram(params: dict) -> dict:
    from cadenza.analysis import pitch_class_histogram
    phrase = _parse_phrase(params["phrase"])
    return {"histogram": pitch_class_histogram(phrase)}


def _handle_rhythmic_density(params: dict) -> dict:
    from cadenza.analysis import rhythmic_density
    phrase = _parse_phrase(params["phrase"])
    return {"density": rhythmic_density(phrase)}


def _handle_complexity_score(params: dict) -> dict:
    from cadenza.analysis import complexity_score
    phrase = _parse_phrase(params["phrase"])
    return {"score": complexity_score(phrase)}


def _handle_find_motifs(params: dict) -> dict:
    from cadenza.analysis import find_motifs
    from cadenza.cn import to_cn
    phrase = _parse_phrase(params["phrase"])
    motifs = find_motifs(phrase, params.get("min_length", 2))
    return {"motifs": [{"phrase": to_cn(m.motif), "positions": list(m.positions)} for m in motifs]}


def _handle_phrase_similarity(params: dict) -> dict:
    from cadenza.analysis import phrase_similarity
    p1 = _parse_phrase(params["phrase"])
    p2 = _parse_phrase(params["phrase2"])
    return {"similarity": phrase_similarity(p1, p2)}


def _handle_detect_sequence(params: dict) -> dict:
    from cadenza.analysis import detect_sequence
    p1 = _parse_phrase(params["phrase"])
    p2 = _parse_phrase(params["phrase2"])
    matches = detect_sequence(p1, p2)
    return {
        "matches": [
            {
                "match_type": m.match_type,
                "offset": m.offset,
                "transposition": (
                    {"quality": m.transposition.quality, "number": m.transposition.number}
                    if m.transposition else None
                ),
            }
            for m in matches
        ]
    }


def _handle_check_voice_leading(params: dict) -> dict:
    from cadenza.analysis import check_voice_leading
    from cadenza.core.score import Score
    phrases = [_parse_phrase(v) for v in params["voices"]]
    voice_pairs: list[tuple[str, tuple]] = []
    for i, p in enumerate(phrases):
        voice_pairs.append((f"voice_{i}", p))
    score = Score(*[item for pair in voice_pairs for item in pair])
    violations = check_voice_leading(score)
    return {
        "violations": [
            {"rule": v.rule, "voice1": v.voice1, "voice2": v.voice2, "position": v.position, "severity": v.severity}
            for v in violations
        ]
    }


def _handle_smooth_voice_leading(params: dict) -> dict:
    from cadenza.analysis import smooth_voice_leading
    c1 = tuple(_safe_parse_pitch(p) for p in params["chord1"].split())
    c2 = tuple(_safe_parse_pitch(p) for p in params["chord2"].split())
    return _pitch_tuple_response(smooth_voice_leading(c1, c2))


# --- Batch ops handlers ---


def _handle_set_articulation_nth(params: dict) -> dict:
    from cadenza.batch import set_articulation_nth
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(set_articulation_nth(phrase, params["n"], params["articulation"]))


def _handle_set_dynamic_nth(params: dict) -> dict:
    from cadenza.batch import set_dynamic_nth
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(set_dynamic_nth(phrase, params["n"], params["dynamic"]))


def _handle_crescendo(params: dict) -> dict:
    from cadenza.batch import crescendo
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(crescendo(phrase, params["start"], params["end"]))


def _handle_decrescendo(params: dict) -> dict:
    from cadenza.batch import decrescendo
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(decrescendo(phrase, params["start"], params["end"]))


def _handle_replace_pitch(params: dict) -> dict:
    from cadenza.batch import replace_pitch
    phrase = _parse_phrase(params["phrase"])
    old = _safe_parse_pitch(params["old_pitch"])
    new = _safe_parse_pitch(params["new_pitch"])
    return _phrase_response(replace_pitch(phrase, old, new))


def _handle_quantize_lengths(params: dict) -> dict:
    from cadenza.batch import quantize_lengths
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(quantize_lengths(phrase, params["grid"]))


def _handle_humanize(params: dict) -> dict:
    from cadenza.batch import humanize
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(humanize(phrase, params.get("seed")))


# --- Set theory handlers ---


def _handle_prime_form(params: dict) -> dict:
    from cadenza.settheory import prime_form
    return {"prime_form": list(prime_form(frozenset(params["pcs"])))}


def _handle_interval_vector(params: dict) -> dict:
    from cadenza.settheory import interval_vector
    return {"interval_vector": list(interval_vector(frozenset(params["pcs"])))}


def _handle_forte_number(params: dict) -> dict:
    from cadenza.settheory import forte_number
    return {"forte_number": forte_number(frozenset(params["pcs"]))}


def _handle_lookup_by_forte(params: dict) -> dict:
    from cadenza.settheory import lookup_by_forte
    return {"prime_form": list(lookup_by_forte(params["forte"]))}


def _handle_complement(params: dict) -> dict:
    from cadenza.settheory import complement
    return {"complement": sorted(complement(frozenset(params["pcs"])))}


def _handle_invert_pcs(params: dict) -> dict:
    from cadenza.settheory import invert_pcs
    return {"inverted": sorted(invert_pcs(frozenset(params["pcs"])))}


def _handle_transpose_pcs(params: dict) -> dict:
    from cadenza.settheory import transpose_pcs
    return {"transposed": sorted(transpose_pcs(frozenset(params["pcs"]), params["n"]))}


# --- Patterns handlers ---


def _handle_euclidean_rhythm(params: dict) -> dict:
    from cadenza.patterns import euclidean_rhythm
    return {"pattern": list(euclidean_rhythm(params["n"], params["m"]))}


def _handle_binary_rhythm(params: dict) -> dict:
    from cadenza.patterns import binary_rhythm
    return {"pattern": list(binary_rhythm(params["n"]))}


def _handle_ostinato(params: dict) -> dict:
    from cadenza.patterns import ostinato
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(ostinato(phrase, params["n"]))


def _handle_accent_pattern(params: dict) -> dict:
    from cadenza.patterns import accent_pattern
    phrase = _parse_phrase(params["phrase"])
    return _phrase_response(accent_pattern(phrase, params["n"]))


def _handle_isorhythm(params: dict) -> dict:
    from cadenza.patterns import isorhythm
    talea = _parse_phrase(params["talea"])
    color = _parse_phrase(params["color"])
    return _phrase_response(isorhythm(talea, color, params.get("length")))


# --- Composition handlers ---


def _handle_markov_generate(params: dict) -> dict:
    from cadenza.composition import markov_melody, train_markov
    phrase = _parse_phrase(params["phrase"])
    model = train_markov(phrase, params.get("order", 1))
    return _phrase_response(markov_melody(model, params.get("length", 8), params.get("seed")))


def _handle_random_walk(params: dict) -> dict:
    from cadenza.composition import random_walk
    from cadenza.theory import get_scale
    start_pitch = _safe_parse_pitch(params["start"])
    root = _safe_parse_pitch(params["scale_root"])
    scale = get_scale(root, params["scale_name"])
    return _phrase_response(random_walk(start_pitch, params["length"], scale, params.get("max_step", 2), params.get("seed")))


def _handle_generate_variations(params: dict) -> dict:
    from cadenza.composition import generate_variations
    phrase = _parse_phrase(params["phrase"])
    variations = generate_variations(phrase, params["n"])
    return {"variations": [_phrase_response(v) for v in variations]}


def _handle_probabilistic_melody(params: dict) -> dict:
    from cadenza.composition import probabilistic_melody
    pitch_weights = {_safe_parse_pitch(k): v for k, v in params["weights"].items()}
    return _phrase_response(probabilistic_melody(pitch_weights, params["length"], params.get("seed")))


# ---------------------------------------------------------------------------
# Operation dispatch registry
# ---------------------------------------------------------------------------

# Import functions for factory-based handlers
from cadenza.transforms import (
    full_retrograde,
    mirror,
    pitch_retrograde,
    rhythmic_retrograde,
)

_DISPATCH: dict[str, Callable[[dict], dict]] = {
    # Transform operations -- pitch
    "chromatic-transpose": _handle_chromatic_transpose,
    "diatonic-transpose": _handle_diatonic_transpose,
    "invert": _handle_invert,
    "retrograde-inversion": _handle_retrograde_inversion,
    "augment": _handle_augment,
    "diminish": _handle_diminish,
    # Transform operations -- phrase-only
    "pitch-retrograde": _make_phrase_handler(pitch_retrograde),
    "full-retrograde": _make_phrase_handler(full_retrograde),
    "rhythmic-retrograde": _make_phrase_handler(rhythmic_retrograde),
    "mirror": _make_phrase_handler(mirror),
    # Transform operations -- with params
    "rotate": _handle_rotate,
    "rhythmic-rotation": _handle_rhythmic_rotation,
    "permute": _handle_permute,
    "interpolate": _handle_interpolate,
    "omit": _handle_omit,
    "repeat": _handle_repeat,
    "fragment": _handle_fragment,
    "concatenate": _handle_concatenate,
    "interleave": _handle_interleave,
    "quantize": _handle_quantize,
    "metric-modulation": _handle_metric_modulation,
    "extract-rhythm": _handle_extract_rhythm,
    "total-duration": _handle_total_duration,
    # Analysis operations
    "identify-chord": _handle_identify_chord,
    "detect-key": _handle_detect_key,
    "roman-numeral": _handle_roman_numeral,
    "detect-modulations": _handle_detect_modulations,
    "ambitus": _handle_ambitus,
    "melodic-contour": _handle_melodic_contour,
    "interval-sequence": _handle_interval_sequence,
    "pitch-class-histogram": _handle_pitch_class_histogram,
    "rhythmic-density": _handle_rhythmic_density,
    "complexity-score": _handle_complexity_score,
    "find-motifs": _handle_find_motifs,
    "phrase-similarity": _handle_phrase_similarity,
    "detect-sequence": _handle_detect_sequence,
    "check-voice-leading": _handle_check_voice_leading,
    "smooth-voice-leading": _handle_smooth_voice_leading,
    # Batch ops
    "set-articulation-nth": _handle_set_articulation_nth,
    "set-dynamic-nth": _handle_set_dynamic_nth,
    "crescendo": _handle_crescendo,
    "decrescendo": _handle_decrescendo,
    "replace-pitch": _handle_replace_pitch,
    "quantize-lengths": _handle_quantize_lengths,
    "humanize": _handle_humanize,
    # Set theory
    "prime-form": _handle_prime_form,
    "interval-vector": _handle_interval_vector,
    "forte-number": _handle_forte_number,
    "lookup-by-forte": _handle_lookup_by_forte,
    "complement": _handle_complement,
    "invert-pcs": _handle_invert_pcs,
    "transpose-pcs": _handle_transpose_pcs,
    "is-subset": _make_two_pcs_handler(
        __import__("cadenza.settheory", fromlist=["is_subset"]).is_subset
    ),
    "is-superset": _make_two_pcs_handler(
        __import__("cadenza.settheory", fromlist=["is_superset"]).is_superset
    ),
    "is-z-related": _make_two_pcs_handler(
        __import__("cadenza.settheory", fromlist=["is_z_related"]).is_z_related
    ),
    # Patterns
    "euclidean-rhythm": _handle_euclidean_rhythm,
    "binary-rhythm": _handle_binary_rhythm,
    "ostinato": _handle_ostinato,
    "accent-pattern": _handle_accent_pattern,
    "isorhythm": _handle_isorhythm,
    # Composition
    "markov-generate": _handle_markov_generate,
    "random-walk": _handle_random_walk,
    "generate-variations": _handle_generate_variations,
    "probabilistic-melody": _handle_probabilistic_melody,
}


# ---------------------------------------------------------------------------
# Batch endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/batch",
    response_model=None,
    summary="Execute multiple operations in one request",
    description="Accepts up to 50 operations. Each runs sequentially. Failures don't abort the batch.",
)
def batch_endpoint(req: BatchRequest) -> dict:
    if len(req.operations) > 50:
        raise CadenzaAPIError(
            BATCH_TOO_LARGE,
            f"Maximum 50 operations per batch, got {len(req.operations)}",
            "",
        )
    results = []
    for op in req.operations:
        handler = _DISPATCH.get(op.operation)
        if handler is None:
            results.append({
                "status": "error",
                "error": {"error": UNKNOWN_OPERATION, "message": f"Unknown operation: {op.operation}"},
            })
            continue
        try:
            result = handler(op.params)
            results.append({"status": "ok", "result": result})
        except CadenzaAPIError as e:
            results.append({
                "status": "error",
                "error": {"error": e.error_code, "message": e.message},
            })
        except Exception as e:
            results.append({
                "status": "error",
                "error": {"error": type(e).__name__, "message": str(e)},
            })
    return {"results": results}
