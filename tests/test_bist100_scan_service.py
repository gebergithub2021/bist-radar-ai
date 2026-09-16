"""Tests for BIST 100 scan service."""

from dataclasses import dataclass

from bist_radar.api.bist100_scan_service import (
    build_bist100_scan_results,
    build_bist100_candidates,
)
from bist_radar.universe.provider import UniverseProvider


class FakeUniverseProvider(UniverseProvider):
    """Fake universe for scan service tests."""

    def get_symbols(self) -> list[str]:
        return [
            "THYAO",
            "ASELS",
            "TUPRS",
        ]


@dataclass
class FakeResult:
    symbol: str
    weighted_score: int


def test_bist100_scan_service_uses_universe_symbols() -> None:
    captured: dict[str, object] = {}

    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list:
        captured["engine"] = engine
        captured["kap_enricher"] = kap_enricher
        captured["symbols"] = symbols
        return []

    fake_engine = object()
    fake_kap_enricher = object()
    universe = FakeUniverseProvider()

    results = build_bist100_scan_results(
        engine=fake_engine,
        kap_enricher=fake_kap_enricher,
        universe=universe,
        scan_builder=fake_build_scan_results,
    )

    assert captured["engine"] is fake_engine
    assert captured["kap_enricher"] is fake_kap_enricher
    assert captured["symbols"] == [
        "THYAO",
        "ASELS",
        "TUPRS",
    ]
    assert results == []


def test_bist100_candidates_returns_all_results_at_or_above_85() -> None:
    class CandidateUniverseProvider(UniverseProvider):
        def get_symbols(self) -> list[str]:
            return [
                "AAA",
                "BBB",
                "CCC",
                "DDD",
                "EEE",
            ]

    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list[FakeResult]:
        return [
            FakeResult("AAA", 100),
            FakeResult("BBB", 90),
            FakeResult("CCC", 85),
            FakeResult("DDD", 84),
            FakeResult("EEE", 70),
        ]

    results = build_bist100_candidates(
        engine=object(),
        kap_enricher=None,
        universe=CandidateUniverseProvider(),
        scan_builder=fake_build_scan_results,
    )

    assert [result.symbol for result in results] == [
        "AAA",
        "BBB",
        "CCC",
    ]

    assert [result.weighted_score for result in results] == [
        100,
        90,
        85,
    ]


def test_bist100_candidates_accepts_custom_minimum_score() -> None:
    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list[FakeResult]:
        return [
            FakeResult("THYAO", 100),
            FakeResult("ASELS", 90),
            FakeResult("TUPRS", 85),
        ]

    results = build_bist100_candidates(
        engine=object(),
        kap_enricher=None,
        universe=FakeUniverseProvider(),
        scan_builder=fake_build_scan_results,
        minimum_score=90,
    )

    assert [result.symbol for result in results] == [
        "THYAO",
        "ASELS",
    ]


def test_bist100_candidates_returns_empty_when_none_reach_threshold() -> None:
    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list[FakeResult]:
        return [
            FakeResult("THYAO", 80),
            FakeResult("ASELS", 70),
            FakeResult("TUPRS", 60),
        ]

    results = build_bist100_candidates(
        engine=object(),
        kap_enricher=None,
        universe=FakeUniverseProvider(),
        scan_builder=fake_build_scan_results,
    )

    assert results == []