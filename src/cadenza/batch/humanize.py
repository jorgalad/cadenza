"""Batch humanize operation: randomized dynamic perturbation.

BATCH-06: humanize
"""

from __future__ import annotations

import random
from dataclasses import replace

from cadenza.core.note import Event, Note
from cadenza.core.phrase import Phrase
from cadenza.batch.mutations import DYNAMICS, DYNAMIC_INDEX


def humanize(phrase: Phrase, seed: int | None = None) -> Phrase:
    """Randomly shift each Note's dynamic by -1/0/+1 step.

    - Notes with dynamic=None are left unchanged.
    - Dynamics are clamped at extremes (ppp cannot go below, fff cannot go above).
    - Rests pass through unchanged.
    - With a seed, results are fully deterministic.
    """
    rng = random.Random(seed)
    result: list[Event] = []
    for event in phrase:
        if isinstance(event, Note) and event.dynamic is not None:
            idx = DYNAMIC_INDEX[event.dynamic]
            shift = rng.choice([-1, 0, 1])
            new_idx = max(0, min(len(DYNAMICS) - 1, idx + shift))
            result.append(replace(event, dynamic=DYNAMICS[new_idx]))
        else:
            result.append(event)
    return tuple(result)
