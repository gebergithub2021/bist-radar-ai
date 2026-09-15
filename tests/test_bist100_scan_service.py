"""Tests for BIST 100 scan service."""

from dataclasses import dataclass

from bist_radar.api.bist100_scan_service import (
    build_bist100_scan_results,
    build_bist100_top_candidates,
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


def test_bist100_scan_service_returns_top_candidates() -> None:
    @dataclass
    class FakeResult:
        symbol: str
        weighted_score: int

    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list[FakeResult]:
        assert symbols == [
            "THYAO",
            "ASELS",
            "TUPRS",
        ]

        return [
            FakeResult("THYAO", 70),
            FakeResult("ASELS", 95),
            FakeResult("TUPRS", 82),
        ]

    fake_engine = object()
    universe = FakeUniverseProvider()

    results = build_bist100_top_candidates(
        engine=fake_engine,
        kap_enricher=None,
        universe=universe,
        scan_builder=fake_build_scan_results,
    )

    assert [result.symbol for result in results] == [
        "ASELS",
        "TUPRS",
        "THYAO",
    ]

    assert [
        result.weighted_score
        for result in results
    ] == [
        95,
        82,
        70,
    ]

def test_bist100_top_candidates_includes_ties_at_cutoff() -> None:
    @dataclass
    class FakeResult:
        symbol: str
        weighted_score: int

    class LargeFakeUniverseProvider(UniverseProvider):
        def get_symbols(self) -> list[str]:
            return [
                "AAA",
                "BBB",
                "CCC",
                "DDD",
                "EEE",
                "FFF",
                "GGG",
            ]

    def fake_build_scan_results(
        engine,
        kap_enricher,
        symbols: list[str],
    ) -> list[FakeResult]:
        return [
            FakeResult("AAA", 100),
            FakeResult("BBB", 100),
            FakeResult("CCC", 100),
            FakeResult("DDD", 100),
            FakeResult("EEE", 100),
            FakeResult("FFF", 100),
            FakeResult("GGG", 90),
        ]

    results = build_bist100_top_candidates(
        engine=object(),
        kap_enricher=None,
        universe=LargeFakeUniverseProvider(),
        scan_builder=fake_build_scan_results,
        limit=5,
    )

    assert len(results) == 6

    assert [result.symbol for result in results] == [
        "AAA",
        "BBB",
        "CCC",
        "DDD",
        "EEE",
        "FFF",
    ]