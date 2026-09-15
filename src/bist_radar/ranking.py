"""Ranking utilities for scan results."""

from typing import TypeVar


T = TypeVar("T")


def select_top_candidates(
    results: list[T],
    limit: int = 5,
) -> list[T]:
    """Return top candidates, including ties at the cutoff."""

    ranked = sorted(
        results,
        key=lambda result: result.weighted_score,
        reverse=True,
    )

    if limit <= 0:
        return []

    if len(ranked) <= limit:
        return ranked

    cutoff_score = ranked[
        limit - 1
    ].weighted_score

    return [
        result
        for result in ranked
        if result.weighted_score >= cutoff_score
    ]