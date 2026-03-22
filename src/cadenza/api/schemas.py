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


# --- Score response models ---


class VoiceResponse(BaseModel):
    """Single voice in a score response."""

    name: str = Field(..., description="Voice name")
    phrase: str = Field(..., description="Voice phrase as CN notation string")
    events: dict | list = Field(..., description="Voice phrase as JSON event structure")


class ScoreResponse(BaseModel):
    """Multi-voice score response."""

    voices: list[VoiceResponse] = Field(..., description="List of voice results")


# --- Job/batch response models ---


class JobSubmitResponse(BaseModel):
    """Response after submitting an async job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field("pending", description="Job status, initially 'pending'")


class JobStatusResponse(BaseModel):
    """Response for checking job status."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    result: dict | None = Field(None, description="Job result when completed")
    error: dict | None = Field(None, description="Error details when failed")


class BatchOperation(BaseModel):
    """Single operation within a batch request."""

    operation: str = Field(..., description="Operation name, e.g. 'chromatic-transpose'")
    params: dict = Field(..., description="Operation parameters as key-value pairs")


class BatchRequest(BaseModel):
    """Batch of multiple operations to execute."""

    operations: list[BatchOperation] = Field(..., description="List of operations to execute")


class BatchResultItem(BaseModel):
    """Result of a single batch operation."""

    status: str = Field(..., description="'ok' or 'error'")
    result: dict | None = Field(None, description="Operation result when successful")
    error: dict | None = Field(None, description="Error details when failed")


class BatchResponse(BaseModel):
    """Response for a batch of operations."""

    results: list[BatchResultItem] = Field(..., description="Results in same order as operations")


# --- Analysis request models ---


class IdentifyChordRequest(BaseModel):
    """Chord identification from pitches."""

    pitches: str = Field(..., description="Space-separated pitch strings, e.g. 'c4 e4 g4 bb4'")


class DetectKeyRequest(BaseModel):
    """Key detection from a phrase."""

    phrase: str = Field(..., description="CN notation string to analyze")


class RomanNumeralRequest(BaseModel):
    """Roman numeral analysis request."""

    pitches: str = Field(..., description="Space-separated pitch strings for the chord")
    key_root: str = Field(..., description="Key root pitch, e.g. 'c4'")
    key_mode: str = Field("major", description="Key mode: 'major' or 'minor'")


class HarmonicRhythmRequest(BaseModel):
    """Harmonic rhythm analysis request."""

    phrase: str = Field(..., description="CN notation string to analyze")
    key_root: str = Field(..., description="Key root pitch, e.g. 'c4'")
    key_mode: str = Field("major", description="Key mode: 'major' or 'minor'")


class DetectModulationsRequest(BaseModel):
    """Modulation detection request."""

    phrase: str = Field(..., description="CN notation string to analyze")
    window: int = Field(4, description="Sliding window size in events")


# --- Batch ops request models ---


class SetArticulationNthRequest(BaseModel):
    """Set articulation on the nth event."""

    phrase: str = Field(..., description="CN notation string")
    n: int = Field(..., description="Event index (0-based)")
    articulation: str = Field(..., description="Articulation marking, e.g. 'staccato'")


class SetDynamicNthRequest(BaseModel):
    """Set dynamic on the nth event."""

    phrase: str = Field(..., description="CN notation string")
    n: int = Field(..., description="Event index (0-based)")
    dynamic: str = Field(..., description="Dynamic marking, e.g. 'ff'")


class CrescendoRequest(BaseModel):
    """Apply crescendo/decrescendo over a phrase."""

    phrase: str = Field(..., description="CN notation string")
    start: str = Field(..., description="Starting dynamic, e.g. 'pp'")
    end: str = Field(..., description="Ending dynamic, e.g. 'ff'")


class ReplacePitchRequest(BaseModel):
    """Replace all occurrences of a pitch."""

    phrase: str = Field(..., description="CN notation string")
    old_pitch: str = Field(..., description="Pitch to replace, e.g. 'c4'")
    new_pitch: str = Field(..., description="Replacement pitch, e.g. 'd4'")


class HumanizeRequest(BaseModel):
    """Humanize timing/velocity of a phrase."""

    phrase: str = Field(..., description="CN notation string")
    seed: int | None = Field(None, description="Random seed for reproducibility")


class QuantizeLengthsRequest(BaseModel):
    """Quantize durations to a rhythmic grid."""

    phrase: str = Field(..., description="CN notation string")
    grid: str = Field(..., description="Grid value, e.g. 'e' for eighth note")


# --- Counterpoint request models ---


class CounterpointRequest(BaseModel):
    """Generate counterpoint against a cantus firmus."""

    phrase: str = Field(..., description="Cantus firmus as CN notation string")
    above: bool = Field(True, description="Generate counterpoint above (True) or below (False)")


class MultiVoiceCounterpointRequest(BaseModel):
    """Generate multi-voice counterpoint."""

    phrase: str = Field(..., description="Cantus firmus as CN notation string")
    n: int = Field(2, description="Number of counterpoint voices to generate")
    species: int = Field(1, description="Counterpoint species (1-5)")
    above: int | None = Field(None, description="Number of voices above cantus firmus (None=auto)")


class CheckCounterpointRequest(BaseModel):
    """Check counterpoint for rule violations."""

    cantus_firmus: str = Field(..., description="Cantus firmus as CN notation string")
    counterpoint: str = Field(..., description="Counterpoint voice as CN notation string")
    species: int = Field(..., description="Counterpoint species to check against (1-5)")
    rules: dict[str, str] | None = Field(None, description="Custom rule overrides")


# --- Set theory request models ---


class PitchClassSetRequest(BaseModel):
    """Pitch-class set operations."""

    pcs: list[int] = Field(..., description="Pitch classes 0-11")


class TwoPCSRequest(BaseModel):
    """Operations on two pitch-class sets."""

    pcs_a: list[int] = Field(..., description="First pitch-class set")
    pcs_b: list[int] = Field(..., description="Second pitch-class set")


class TransposePCSRequest(BaseModel):
    """Transpose a pitch-class set."""

    pcs: list[int] = Field(..., description="Pitch classes 0-11")
    n: int = Field(..., description="Transposition level (semitones)")


class ForteRequest(BaseModel):
    """Look up a set class by Forte number."""

    forte: str = Field(..., description="Forte number, e.g. '3-1'")


class ToneRowRequest(BaseModel):
    """Twelve-tone row operations."""

    pcs: list[int] = Field(..., description="12 pitch classes in row order")


class RealizeRowRequest(BaseModel):
    """Realize a tone row as pitched notes."""

    row_form: list[int] = Field(..., description="Pitch classes in row order")
    base_octave: int = Field(4, description="Starting octave for realization")
    nearest: bool = Field(False, description="Use nearest-pitch realization")


class SegmentRowRequest(BaseModel):
    """Segment a tone row into subsets."""

    row_form: list[int] = Field(..., description="Pitch classes in row order")
    sizes: list[int] = Field(..., description="Segment sizes, e.g. [3, 3, 3, 3]")


class DeriveRowRequest(BaseModel):
    """Derive a twelve-tone row from a seed set."""

    seed: list[int] = Field(..., description="Seed pitch-class set to derive row from")


# --- Patterns request models ---


class EuclideanRequest(BaseModel):
    """Generate a Euclidean rhythm pattern."""

    n: int = Field(..., description="Total number of slots")
    m: int = Field(..., description="Number of active pulses")


class BinaryRhythmRequest(BaseModel):
    """Generate all binary rhythm patterns of length n."""

    n: int = Field(..., description="Pattern length in slots")


class ApplyRhythmRequest(BaseModel):
    """Apply a boolean rhythm pattern to pitches."""

    rhythm: list[bool] = Field(..., description="Rhythm pattern (True=note, False=rest)")
    pitches: str = Field(..., description="CN notation string of pitches to apply")


class IsorhythmRequest(BaseModel):
    """Generate isorhythmic pattern from talea and color."""

    talea: str = Field(..., description="Rhythmic pattern as CN notation string")
    color: str = Field(..., description="Pitch pattern as CN notation string")
    length: int | None = Field(None, description="Output length (None=LCM of talea and color)")


class OstinatoRequest(BaseModel):
    """Generate ostinato repetition."""

    phrase: str = Field(..., description="CN notation string to repeat")
    n: int = Field(..., description="Number of repetitions")


class AccentPatternRequest(BaseModel):
    """Apply accent pattern to a phrase."""

    phrase: str = Field(..., description="CN notation string")
    n: int = Field(..., description="Accent every nth event")


class RhythmicCanonRequest(BaseModel):
    """Generate a rhythmic canon."""

    phrase: str = Field(..., description="CN notation string")
    n: int = Field(..., description="Number of canon voices")
    offset: str = Field(..., description="Time offset between voices as CN duration string")


class HocketRequest(BaseModel):
    """Split a phrase into hocket voices."""

    phrase: str = Field(..., description="CN notation string")
    n: int = Field(..., description="Number of hocket voices")


# --- Composition request models ---


class MarkovTrainRequest(BaseModel):
    """Train a Markov model from a phrase."""

    phrase: str = Field(..., description="CN notation string for training data")
    order: int = Field(1, description="Markov chain order (1=first-order)")


class MarkovGenerateRequest(BaseModel):
    """Generate melody using trained Markov model."""

    phrase: str = Field(..., description="CN notation string for training data")
    order: int = Field(1, description="Markov chain order")
    length: int = Field(8, description="Number of events to generate")
    seed: int | None = Field(None, description="Random seed for reproducibility")


class LSystemRequest(BaseModel):
    """Generate music from an L-system."""

    axiom: str = Field(..., description="Initial axiom string")
    rules: dict[str, str] = Field(..., description="Rewriting rules, e.g. {'A': 'AB', 'B': 'A'}")
    alphabet: dict[str, str] = Field(..., description="Symbol-to-CN mapping, e.g. {'A': 'q c4', 'B': 'e d4'}")
    generations: int = Field(..., description="Number of L-system generations to apply")


class ProbabilisticRequest(BaseModel):
    """Generate melody from weighted probabilities."""

    weights: dict[str, float] = Field(..., description="CN event to probability mapping")
    length: int = Field(..., description="Number of events to generate")
    seed: int | None = Field(None, description="Random seed for reproducibility")


class RandomWalkRequest(BaseModel):
    """Generate melody via random walk on a scale."""

    start: str = Field(..., description="Starting pitch, e.g. 'c4'")
    length: int = Field(..., description="Number of events to generate")
    scale_root: str = Field(..., description="Scale root pitch, e.g. 'c4'")
    scale_name: str = Field(..., description="Scale name, e.g. 'major'")
    max_step: int = Field(2, description="Maximum step size in scale degrees")
    seed: int | None = Field(None, description="Random seed for reproducibility")


class GenerateVariationsRequest(BaseModel):
    """Generate variations of a phrase."""

    phrase: str = Field(..., description="CN notation string to vary")
    n: int = Field(..., description="Number of variations to generate")


# --- I/O request models ---


class ExportPhraseRequest(BaseModel):
    """Export a phrase to MusicXML."""

    phrase: str = Field(..., description="CN notation string to export")


class ExportMidiRequest(BaseModel):
    """Export a phrase to MIDI."""

    phrase: str = Field(..., description="CN notation string to export")
    tempo: int = Field(120, description="Tempo in BPM")


# --- Analysis request models (reusing PhraseOnlyRequest where appropriate) ---


class RealizeChordRequest(BaseModel):
    """Realize a chord from root and symbol."""

    root: str = Field(..., description="Root pitch, e.g. 'c4'")
    symbol: str = Field(..., description="Chord symbol, e.g. 'dom7'")
    inversion: int = Field(0, description="Inversion number (0=root position)")


class CheckVoiceLeadingRequest(BaseModel):
    """Check voice leading between chord progressions."""

    voices: list[str] = Field(..., description="List of CN phrases, one per voice")


class GenerateInnerVoicesRequest(BaseModel):
    """Generate inner voices between soprano and bass."""

    soprano: str = Field(..., description="Soprano voice as CN notation string")
    bass: str = Field(..., description="Bass voice as CN notation string")
    n: int = Field(2, description="Number of inner voices to generate")


class SmoothVoiceLeadingRequest(BaseModel):
    """Find smooth voice leading between two chords."""

    chord1: str = Field(..., description="First chord as space-separated pitch strings")
    chord2: str = Field(..., description="Second chord as space-separated pitch strings")


class TwoPhraseRequest(BaseModel):
    """Request with two CN phrases."""

    phrase: str = Field(..., description="First CN notation string")
    phrase2: str = Field(..., description="Second CN notation string")


class FindMotifsRequest(BaseModel):
    """Find recurring motifs in a phrase."""

    phrase: str = Field(..., description="CN notation string to search for motifs")
    min_length: int = Field(2, description="Minimum motif length in events")


class PhraseAnalysisRequest(BaseModel):
    """Phrase analysis request (alias for PhraseOnlyRequest)."""

    phrase: str = Field(..., description="CN notation string to analyze")
