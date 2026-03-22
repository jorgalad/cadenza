"""Composition endpoints -- algorithmic melody generation."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.errors import NOT_IMPLEMENTED, CadenzaAPIError
from cadenza.api.helpers import _parse_phrase, _phrase_response, _safe_parse_pitch
from cadenza.api.schemas import (
    GenerateVariationsRequest,
    LSystemRequest,
    MarkovGenerateRequest,
    MarkovTrainRequest,
    PhraseOnlyRequest,
    ProbabilisticRequest,
    RandomWalkRequest,
)
from cadenza.composition import (
    generate_variations,
    lsystem_melody,
    markov_melody,
    probabilistic_melody,
    random_walk,
    train_markov,
)
from cadenza.theory import get_scale

router = APIRouter(prefix="/v1/composition", tags=["composition"])


@router.post(
    "/train-markov",
    response_model=None,
    summary="Train a Markov model from a phrase",
    description="Build a Markov transition table from a CN phrase. Returns the model's order and serialized transition table.",
)
def train_markov_endpoint(req: MarkovTrainRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    model = train_markov(phrase, req.order)
    # Serialize tuple keys to comma-separated strings for JSON compatibility
    table = {
        ",".join(str(m) for m in k): v
        for k, v in model.transition_table.items()
    }
    return {"order": model.order, "transition_table": table}


@router.post(
    "/markov-generate",
    response_model=None,
    summary="Generate melody using Markov chain",
    description="Train a Markov model from a CN phrase and generate a new melody. Use seed for reproducibility.",
)
def markov_generate_endpoint(req: MarkovGenerateRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    model = train_markov(phrase, req.order)
    result = markov_melody(model, req.length, req.seed)
    return _phrase_response(result)


@router.post(
    "/lsystem-melody",
    response_model=None,
    summary="Generate melody from L-system",
    description="Expand an L-system axiom through rewriting rules and translate via alphabet to CN events.",
)
def lsystem_melody_endpoint(req: LSystemRequest) -> dict:
    # Convert alphabet: each value is a CN string; parse and take first event
    alphabet_map = {}
    for key, cn_str in req.alphabet.items():
        parsed = _parse_phrase(cn_str)
        if parsed:
            alphabet_map[key] = parsed[0]
    result = lsystem_melody(req.axiom, req.rules, alphabet_map, req.generations)
    return _phrase_response(result)


@router.post(
    "/probabilistic-melody",
    response_model=None,
    summary="Generate melody from weighted probabilities",
    description="Select pitches randomly from a weighted distribution. Use seed for reproducibility.",
)
def probabilistic_melody_endpoint(req: ProbabilisticRequest) -> dict:
    pitch_weights = {_safe_parse_pitch(k): v for k, v in req.weights.items()}
    result = probabilistic_melody(pitch_weights, req.length, req.seed)
    return _phrase_response(result)


@router.post(
    "/tendency-mask-melody",
    response_model=None,
    summary="Generate melody with time-varying distribution (not available over HTTP)",
    description="Tendency mask melody requires a Python callable and cannot be invoked over HTTP.",
)
def tendency_mask_melody_endpoint(req: PhraseOnlyRequest) -> dict:
    raise CadenzaAPIError(
        NOT_IMPLEMENTED,
        "tendency-mask-melody requires a Python callable; not available over HTTP",
        "",
    )


@router.post(
    "/random-walk",
    response_model=None,
    summary="Generate melody via random walk on a scale",
    description="Walk randomly on a scale from a starting pitch. Use seed for reproducibility.",
)
def random_walk_endpoint(req: RandomWalkRequest) -> dict:
    start_pitch = _safe_parse_pitch(req.start)
    root = _safe_parse_pitch(req.scale_root)
    scale = get_scale(root, req.scale_name)
    result = random_walk(start_pitch, req.length, scale, req.max_step, req.seed)
    return _phrase_response(result)


@router.post(
    "/generate-variations",
    response_model=None,
    summary="Generate variations of a phrase",
    description="Produce N distinct but recognizably related variations of a CN phrase using systematic transforms.",
)
def generate_variations_endpoint(req: GenerateVariationsRequest) -> dict:
    phrase = _parse_phrase(req.phrase)
    variations = generate_variations(phrase, req.n)
    return {"variations": [_phrase_response(v) for v in variations]}
