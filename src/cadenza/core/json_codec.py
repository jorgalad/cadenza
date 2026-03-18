"""JSON serialization/deserialization for all core types."""

from __future__ import annotations

import json
from fractions import Fraction
from typing import Any

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration
from cadenza.core.note import Note, Rest
from cadenza.core.score import Score


def _to_serializable(obj: Any) -> Any:
    """Recursively convert cadenza types to JSON-serializable dicts/lists."""
    if isinstance(obj, Fraction):
        return {"_type": "Fraction", "numerator": obj.numerator, "denominator": obj.denominator}
    if isinstance(obj, Pitch):
        return {
            "_type": "Pitch",
            "step": obj.step,
            "accidental": obj.accidental,
            "octave": obj.octave,
        }
    if isinstance(obj, Duration):
        return {
            "_type": "Duration",
            "fraction": _to_serializable(obj.fraction),
            "base": obj.base,
            "dots": obj.dots,
            "tuplet": obj.tuplet,
        }
    if isinstance(obj, Note):
        return {
            "_type": "Note",
            "pitch": _to_serializable(obj.pitch),
            "duration": _to_serializable(obj.duration),
            "dynamic": obj.dynamic,
            "articulations": list(obj.articulations),
        }
    if isinstance(obj, Rest):
        return {
            "_type": "Rest",
            "duration": _to_serializable(obj.duration),
        }
    if isinstance(obj, Score):
        return {
            "_type": "Score",
            "_voices": [
                [name, [_to_serializable(event) for event in phrase]]
                for name, phrase in obj._voices
            ],
        }
    if isinstance(obj, tuple):
        # Phrase (tuple of events) or generic tuple
        return {"_type": "tuple", "items": [_to_serializable(item) for item in obj]}
    return obj


class CadenzaEncoder(json.JSONEncoder):
    """Custom JSON encoder for cadenza core types."""

    def default(self, obj: Any) -> Any:
        result = _to_serializable(obj)
        if result is not obj:
            return result
        return super().default(obj)


def cadenza_decoder(dct: dict[str, Any]) -> Any:
    """Object hook for json.loads -- reconstructs cadenza types from _type discriminator."""
    if "_type" not in dct:
        return dct

    type_name = dct["_type"]

    if type_name == "Fraction":
        return Fraction(dct["numerator"], dct["denominator"])

    if type_name == "Pitch":
        return Pitch(
            step=dct["step"],
            accidental=dct["accidental"],
            octave=dct["octave"],
        )

    if type_name == "Duration":
        fraction = dct["fraction"]
        if isinstance(fraction, dict):
            fraction = Fraction(fraction["numerator"], fraction["denominator"])
        return Duration(
            fraction=fraction,
            base=dct["base"],
            dots=dct["dots"],
            tuplet=dct.get("tuplet"),
        )

    if type_name == "Note":
        pitch = dct["pitch"]
        if isinstance(pitch, dict):
            pitch = cadenza_decoder(pitch)
        duration = dct["duration"]
        if isinstance(duration, dict):
            duration = cadenza_decoder(duration)
        return Note(
            pitch=pitch,
            duration=duration,
            dynamic=dct.get("dynamic"),
            articulations=tuple(dct.get("articulations", ())),
        )

    if type_name == "Rest":
        duration = dct["duration"]
        if isinstance(duration, dict):
            duration = cadenza_decoder(duration)
        return Rest(duration=duration)

    if type_name == "Score":
        voices_data = dct["_voices"]
        voices_tuples: list[tuple[str, tuple[Note | Rest, ...]]] = []
        for name, events_list in voices_data:
            events = tuple(
                cadenza_decoder(e) if isinstance(e, dict) else e
                for e in events_list
            )
            voices_tuples.append((name, events))
        return Score(_voices=tuple(voices_tuples))

    if type_name == "tuple":
        items = dct["items"]
        return tuple(
            cadenza_decoder(item) if isinstance(item, dict) else item
            for item in items
        )

    return dct


def to_json(obj: Any) -> str:
    """Serialize a cadenza object to JSON string."""
    # Pre-convert to avoid tuple-as-array issue (json.dumps treats tuples as arrays)
    return json.dumps(_to_serializable(obj), indent=2)


def from_json(s: str) -> Any:
    """Deserialize a cadenza object from JSON string."""
    return json.loads(s, object_hook=cadenza_decoder)
