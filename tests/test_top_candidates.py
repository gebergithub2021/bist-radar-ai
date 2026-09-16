"""Tests for technical candidate selection."""

from dataclasses import dataclass

from bist_radar.ranking import select_candidates_by_score


@dataclass
class FakeScanResult:
    symbol: str
    weighted_score: int


def test_select_candidates_returns_all_results_at_or_above_minimum_score() -> None:
    results = [
        FakeScanResult("AAA", 100),
        FakeScanResult("BBB", 90),
        FakeScanResult("CCC", 85),
        FakeScanResult("DDD", 84),
        FakeScanResult("EEE", 70),
    ]

    selected = select_candidates_by_score(
        results,
        minimum_score=85,
    )

    assert [result.symbol for result in selected] == [
        "AAA",
        "BBB",
        "CCC",
    ]

    assert [result.weighted_score for result in selected] == [
        100,
        90,
        85,
    ]


def test_select_candidates_sorts_results_by_score() -> None:
    results = [
        FakeScanResult("AAA", 85),
        FakeScanResult("BBB", 100),
        FakeScanResult("CCC", 90),
        FakeScanResult("DDD", 80),
    ]

    selected = select_candidates_by_score(
        results,
        minimum_score=85,
    )

    assert [result.symbol for result in selected] == [
        "BBB",
        "CCC",
        "AAA",
    ]


def test_select_candidates_returns_empty_when_none_reach_minimum_score() -> None:
    results = [
        FakeScanResult("AAA", 84),
        FakeScanResult("BBB", 70),
        FakeScanResult("CCC", 40),
    ]

    selected = select_candidates_by_score(
        results,
        minimum_score=85,
    )

    assert selected == []


def test_select_candidates_uses_85_as_default_minimum_score() -> None:
    results = [
        FakeScanResult("AAA", 90),
        FakeScanResult("BBB", 85),
        FakeScanResult("CCC", 84),
    ]

    selected = select_candidates_by_score(results)

    assert [result.symbol for result in selected] == [
        "AAA",
        "BBB",
    ]