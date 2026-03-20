"""Shared fixtures for set theory tests."""

import pytest


@pytest.fixture
def major_triad():
    return frozenset({0, 3, 7})


@pytest.fixture
def all_interval_tetrachord():
    return frozenset({0, 1, 4, 6})  # 4-Z15 prime form


@pytest.fixture
def z_related_pair():
    return frozenset({0, 1, 4, 6}), frozenset({0, 1, 3, 7})  # 4-Z15, 4-Z29
