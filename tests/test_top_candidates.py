"""Tests for Top 5 candidate selection."""

from dataclasses import dataclass

from bist_radar.ranking import select_top_candidates


@dataclass
class FakeScanResult:
    symbol: str
    weighted_score: int


def test_select_top_candidates_returns_highest_scores() -> None:
    results = [
        FakeScanResult("THYAO", 65),
        FakeScanResult("ASELS", 92),
        FakeScanResult("TUPRS", 78),
        FakeScanResult("EREGL", 55),
        FakeScanResult("KRDMD", 81),
        FakeScanResult("AKBNK", 88),
        FakeScanResult("GARAN", 73),
    ]

    top = select_top_candidates(results)

    assert len(top) == 5

    assert [result.symbol for result in top] == [
        "ASELS",
        "AKBNK",
        "KRDMD",
        "TUPRS",
        "GARAN",
    ]

    assert [result.weighted_score for result in top] == [
        92,
        88,
        81,
        78,
        73,
    ]


def test_select_top_candidates_handles_fewer_than_five() -> None:
    results = [
        FakeScanResult("THYAO", 70),
        FakeScanResult("ASELS", 90),
        FakeScanResult("TUPRS", 80),
    ]

    top = select_top_candidates(results)

    assert len(top) == 3

    assert [result.symbol for result in top] == [
        "ASELS",
        "TUPRS",
        "THYAO",
    ]

def test_select_top_candidates_includes_ties_at_cutoff() -> None:
    results = [
        FakeScanResult("AAA", 100),
        FakeScanResult("BBB", 100),
        FakeScanResult("CCC", 100),
        FakeScanResult("DDD", 100),
        FakeScanResult("EEE", 100),
        FakeScanResult("FFF", 100),
        FakeScanResult("GGG", 90),
    ]

    top = select_top_candidates(
        results,
        limit=5,
    )

    assert len(top) == 6

    assert [result.symbol for result in top] == [
        "AAA",
        "BBB",
        "CCC",
        "DDD",
        "EEE",
        "FFF",
    ]

    assert all(
        result.weighted_score == 100
        for result in top
    )