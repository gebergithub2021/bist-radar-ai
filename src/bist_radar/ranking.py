"""Ranking utilities for scan results."""

from typing import TypeVar


T = TypeVar("T")


def select_candidates_by_score(
    results: list[T],
    minimum_score: int = 85,
) -> list[T]:
    """Return all candidates meeting the minimum technical score."""

    selected = [
        result
        for result in results
        if result.weighted_score >= minimum_score
    ]

    return sorted(
        selected,
        key=lambda result: result.weighted_score,
        reverse=True,
    )