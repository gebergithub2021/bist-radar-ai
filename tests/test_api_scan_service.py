from datetime import date, datetime
from bist_radar.api.scan_service import build_scan_results
from bist_radar.models.scan_result import ScanResult
import pytest


class FakeScannerEngine:
    def get_ranked_scan_results(
        self,
        symbols: list[str],
        start: date,
        end: date,
    ) -> list[ScanResult]:
        return [
            ScanResult(
                symbol="ASELS",
                above_sma20=True,
                rsi_above_50=True,
                macd_bullish=True,
                close=220.0,
                sma20=210.0,
                rsi14=62.0,
                macd=3.2,
                signal=2.0,
                histogram=1.2,
            )
        ]


def test_build_scan_results_returns_scanner_results() -> None:
    engine = FakeScannerEngine()

    results = build_scan_results(
        engine=engine,
        kap_enricher=None,
        symbols=["ASELS"],
    )

    assert len(results) == 1
    assert results[0].symbol == "ASELS"
    assert results[0].weighted_score == 90

class FakeKapEnricher:
    def __init__(self) -> None:
        self.last_start: datetime | None = None
        self.last_end: datetime | None = None

    def enrich_all(
        self,
        results: list[ScanResult],
        start: datetime,
        end: datetime,
    ) -> list[ScanResult]:
        self.last_start = start
        self.last_end = end

        for result in results:
            result.kap_has_news = True
            result.kap_importance = "HIGH"
            result.kap_title = "Yeni İş İlişkisi"

        return results


def test_build_scan_results_enriches_with_30_day_kap_window() -> None:
    engine = FakeScannerEngine()
    kap_enricher = FakeKapEnricher()

    results = build_scan_results(
        engine=engine,
        kap_enricher=kap_enricher,
        symbols=["ASELS"],
    )

    assert results[0].kap_has_news is True
    assert results[0].kap_importance == "HIGH"

    assert kap_enricher.last_start is not None
    assert kap_enricher.last_end is not None

    assert (
        kap_enricher.last_end.date()
        - kap_enricher.last_start.date()
    ).days == 30

class FailingKapEnricher:
    def enrich_all(
        self,
        results: list[ScanResult],
        start: datetime,
        end: datetime,
    ) -> list[ScanResult]:
        raise RuntimeError("KAP service error")


def test_build_scan_results_preserves_results_when_kap_fails() -> None:
    engine = FakeScannerEngine()
    kap_enricher = FailingKapEnricher()

    results = build_scan_results(
        engine=engine,
        kap_enricher=kap_enricher,
        symbols=["ASELS"],
    )

    assert len(results) == 1

    result = results[0]

    assert result.symbol == "ASELS"
    assert result.weighted_score == 90

    assert result.kap_has_news is False
    assert result.kap_importance == "UNAVAILABLE"
    assert result.kap_title == "KAP service unavailable"
    assert result.kap_reason == "service error"
    assert result.kap_url == ""

class FailingScannerEngine:
    def get_ranked_scan_results(
        self,
        symbols: list[str],
        start: date,
        end: date,
    ) -> list[ScanResult]:
        raise RuntimeError("Market data error")


def test_build_scan_results_propagates_scanner_error() -> None:
    engine = FailingScannerEngine()

    with pytest.raises(
        RuntimeError,
        match="Market data error",
    ):
        build_scan_results(
            engine=engine,
            kap_enricher=None,
            symbols=["ASELS"],
        )