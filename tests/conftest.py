"""Shared test fixtures for cadenza tests."""

from __future__ import annotations

import pytest

from cadenza.core.pitch import Pitch
from cadenza.core.duration import Duration


# --- Pitch fixtures ---

@pytest.fixture
def c4() -> Pitch:
    return Pitch("c", "n", 4)


@pytest.fixture
def eb3() -> Pitch:
    return Pitch("e", "b", 3)


@pytest.fixture
def ds3() -> Pitch:
    return Pitch("d", "s", 3)


@pytest.fixture
def fs5() -> Pitch:
    return Pitch("f", "s", 5)


@pytest.fixture
def a4() -> Pitch:
    return Pitch("a", "n", 4)


# --- Duration fixtures ---

@pytest.fixture
def quarter() -> Duration:
    return Duration.from_omn("q")


@pytest.fixture
def dotted_quarter() -> Duration:
    return Duration.from_omn("q", dots=1)


@pytest.fixture
def triplet_eighth() -> Duration:
    return Duration.from_omn("e", tuplet=3)
