"""Pydantic v2 request/response models for all Cadenza API endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Response models ---


class PhraseResponse(BaseModel):
    """Single phrase result with CN string and JSON event structure."""

    phrase: str = Field(..., description="Result as CN notation string")
    events: dict | list = Field(..., description="Result as JSON event structure from json_codec")


class MultiPhraseResponse(BaseModel):
    """Multiple phrase results."""

    phrases: list[PhraseResponse]


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: str = Field(..., description="Error code, e.g. 'INVALID_CN'")
    message: str = Field(..., description="Human-readable error description")
    input: str | None = Field(None, description="The invalid input value")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    cadenza_version: str


# --- Transform request models ---


class TransposeRequest(BaseModel):
    """Chromatic transposition request."""

    phrase: str = Field(..., description="CN notation string")
    interval: str = Field(..., description="Interval string, e.g. 'm3', 'P5'")


class DiatonicTransposeRequest(BaseModel):
    """Diatonic transposition request."""

    phrase: str
    n: int = Field(..., description="Number of scale degrees to transpose")
    scale_name: str = Field("major", description="Scale name, e.g. 'major', 'dorian'")


class PhraseOnlyRequest(BaseModel):
    """Request with only a CN phrase (retrograde, mirror, sort, etc.)."""

    phrase: str = Field(..., description="CN notation string")


class InvertRequest(BaseModel):
    """Inversion request."""

    phrase: str
    axis: str | None = Field(None, description="Pitch axis, e.g. 'c4'. None=first pitch")


class RatioRequest(BaseModel):
    """Augment/diminish by ratio request."""

    phrase: str
    ratio: float = Field(..., description="Augment/diminish ratio, e.g. 2.0")


class RotateRequest(BaseModel):
    """Rotation request."""

    phrase: str
    n: int = Field(..., description="Number of positions to rotate")


class PermuteRequest(BaseModel):
    """Permutation request."""

    phrase: str
    indices: list[int] = Field(..., description="New order of indices, e.g. [2,0,1]")


class InterpolateRequest(BaseModel):
    """Interpolation request."""

    phrase: str
    steps: int = Field(1, description="Number of passing notes per gap")


class OmitRequest(BaseModel):
    """Omit every nth event request."""

    phrase: str
    n: int = Field(..., description="Remove every nth event (1-indexed)")


class FragmentRequest(BaseModel):
    """Fragment a phrase into sub-phrases."""

    phrase: str
    lengths: list[int] = Field(..., description="Sub-phrase lengths")


class ConcatenateRequest(BaseModel):
    """Concatenate multiple phrases."""

    phrases: list[str] = Field(..., description="List of CN notation strings to join")


class InterleaveRequest(BaseModel):
    """Interleave two phrases."""

    phrase: str = Field(..., description="First CN phrase")
    phrase2: str = Field(..., description="Second CN phrase")


class RepeatRequest(BaseModel):
    """Repeat a phrase N times."""

    phrase: str
    n: int = Field(..., description="Number of repetitions")


class QuantizeRequest(BaseModel):
    """Quantize durations to a grid."""

    phrase: str
    grid: list[str] = Field(..., description="Duration grid values, e.g. ['q', 'e']")


class MetricModulationRequest(BaseModel):
    """Metric modulation request."""

    phrase: str
    old_unit: str = Field(..., description="Old beat unit as CN duration, e.g. 'q.'")
    new_unit: str = Field(..., description="New beat unit as CN duration, e.g. 'q'")


# --- Theory request models ---


class ScaleRequest(BaseModel):
    """Scale generation request."""

    root: str = Field(..., description="Root pitch, e.g. 'c4', 'eb4'")
    name: str = Field(..., description="Scale name, e.g. 'major', 'dorian'")


class ChordRequest(BaseModel):
    """Chord voicing request."""

    root: str = Field(..., description="Root pitch, e.g. 'c4'")
    symbol: str = Field(..., description="Chord symbol, e.g. 'maj', 'm7', 'dim7'")
    inversion: int = Field(0, description="0=root, 1=first, 2=second, etc.")


class DiatonicChordsRequest(BaseModel):
    """Diatonic chords request."""

    root: str = Field(..., description="Scale root pitch, e.g. 'c4'")
    scale_name: str = Field("major", description="Scale name")
    quality: str = Field("triad", description="'triad' or 'seventh'")


class SecondaryDominantRequest(BaseModel):
    """Secondary dominant request."""

    degree: int = Field(..., description="Target scale degree (2-7)")
    root: str = Field(..., description="Key root pitch, e.g. 'c4'")
    key_name: str = Field("major", description="Scale name")


class Aug6Request(BaseModel):
    """Augmented sixth chord request."""

    aug6_type: str = Field(..., description="'italian', 'french', or 'german'")
    root: str = Field(..., description="Key root pitch")
    key_name: str = Field("major", description="Scale name")


class NeapolitanRequest(BaseModel):
    """Neapolitan chord request."""

    root: str = Field(..., description="Key root pitch")
    key_name: str = Field("major", description="Scale name")
