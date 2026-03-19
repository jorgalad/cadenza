"""Musical transforms: pitch, rhythm, and melodic operations."""

from cadenza.transforms.pitch import (
    chromatic_transpose,
    diatonic_transpose,
    enharmonic_respell,
    from_frequency,
    from_midi,
    interval_between,
    invert,
    nearest_in_scale,
    pitch_class,
    pitch_in_scale,
    to_frequency,
)

from cadenza.transforms.rhythm import (
    augment,
    diminish,
    extract_rhythm,
    metric_modulation,
    quantize,
    rhythmic_retrograde,
    rhythmic_rotation,
    total_duration,
)

from cadenza.transforms.melodic import (
    concatenate,
    fragment,
    full_retrograde,
    interpolate,
    interleave,
    mirror,
    omit,
    permute,
    pitch_map,
    pitch_retrograde,
    repeat,
    retrograde_inversion,
    rotate,
)

__all__ = [
    # Pitch transforms
    "chromatic_transpose",
    "diatonic_transpose",
    "enharmonic_respell",
    "from_frequency",
    "from_midi",
    "interval_between",
    "invert",
    "nearest_in_scale",
    "pitch_class",
    "pitch_in_scale",
    "to_frequency",
    # Rhythm transforms
    "augment",
    "diminish",
    "extract_rhythm",
    "metric_modulation",
    "quantize",
    "rhythmic_retrograde",
    "rhythmic_rotation",
    "total_duration",
    # Melodic transforms
    "concatenate",
    "fragment",
    "full_retrograde",
    "interpolate",
    "interleave",
    "mirror",
    "omit",
    "permute",
    "pitch_map",
    "pitch_retrograde",
    "repeat",
    "retrograde_inversion",
    "rotate",
]
