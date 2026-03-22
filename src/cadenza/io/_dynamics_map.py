"""Dynamic-velocity mapping constants and lookup functions."""

from __future__ import annotations

# Exact 8-level mapping from CONTEXT.md
DYNAMIC_TO_VELOCITY: dict[str, int] = {
    "ppp": 16, "pp": 33, "p": 49, "mp": 64,
    "mf": 80, "f": 96, "ff": 112, "fff": 127,
}

# Velocity ranges for import (range is exclusive on upper bound)
VELOCITY_RANGES: list[tuple[range, str]] = [
    (range(1, 25), "ppp"),
    (range(25, 41), "pp"),
    (range(41, 57), "p"),
    (range(57, 73), "mp"),
    (range(73, 89), "mf"),
    (range(89, 105), "f"),
    (range(105, 120), "ff"),
    (range(120, 128), "fff"),
]


def velocity_to_dynamic(velocity: int) -> str:
    """Convert MIDI velocity (1-127) to dynamic string."""
    for vel_range, dynamic in VELOCITY_RANGES:
        if velocity in vel_range:
            return dynamic
    return "mf"  # fallback


def dynamic_to_velocity(dynamic: str | None) -> int:
    """Convert dynamic string to MIDI velocity. None -> 64."""
    if dynamic is None:
        return 64
    return DYNAMIC_TO_VELOCITY.get(dynamic, 64)
