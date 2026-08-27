"""Tests for scanner engine."""

import pandas as pd

from bist_radar.data.provider import MarketDataProvider
from bist_radar.scanner.engine import ScannerEngine


def make_market_df(
    close: list[float],
    volume: list[float] | None = None,
) -> pd.DataFrame:
    """Create market data required by scanner tests."""

    if volume is None:
        volume = [1000] * len(close)

    return pd.DataFrame(
        {
            "Close": close,
            "High": [value + 1 for value in close],
            "Low": [value - 1 for value in close],
            "Volume": volume,
        }
    )


class FakeProvider(MarketDataProvider):
    """Fake provider for scanner engine tests."""

    def get_symbols(self) -> list[str]:
        return ["TEST"]

    def get_history(
        self,
        symbol: str,
        start,
        end,
    ) -> pd.DataFrame:
        close = list(range(100, 140))

        volume = (
            [1000] * 39
            + [1500]
        )

        return make_market_df(
            close=close,
            volume=volume,
        )


def test_scan_symbol_returns_true_when_strategy_passes():
    """A symbol should pass when strategy conditions are satisfied."""

    provider = FakeProvider()
    engine = ScannerEngine(provider)

    result = engine.scan_symbol(
        "TEST",
        None,
        None,
    )

    assert result


def test_scan_symbol_returns_false_when_strategy_fails():
    """A symbol should fail when strategy conditions are not satisfied."""

    class FailingProvider(FakeProvider):
        def get_history(
            self,
            symbol: str,
            start,
            end,
        ) -> pd.DataFrame:
            close = list(range(140, 100, -1))

            return make_market_df(
                close=close,
            )

    provider = FailingProvider()
    engine = ScannerEngine(provider)

    result = engine.scan_symbol(
        "TEST",
        None,
        None,
    )

    assert not result


def test_scan_symbols_returns_only_matching_symbols():
    """Only symbols that pass the strategy should be returned."""

    class MixedProvider(FakeProvider):
        def get_history(
            self,
            symbol: str,
            start,
            end,
        ) -> pd.DataFrame:
            if symbol == "PASS":
                close = list(range(100, 140))
            else:
                close = list(range(140, 100, -1))

            return make_market_df(
                close=close,
            )

    provider = MixedProvider()
    engine = ScannerEngine(provider)

    result = engine.scan_symbols(
        ["PASS", "FAIL"],
        None,
        None,
    )

    assert result == ["PASS"]


def test_get_scan_result_returns_detailed_result():
    """Detailed scan result should contain expected values."""

    provider = FakeProvider()
    engine = ScannerEngine(provider)

    result = engine.get_scan_result(
        "TEST",
        None,
        None,
    )

    assert result.symbol == "TEST"

    assert result.above_sma20
    assert result.rsi_above_50
    assert result.macd_bullish

    assert result.score == 3
    assert result.passed

    assert result.volume > 0
    assert result.volume_sma20 > 0
    assert result.volume_ratio > 1
    assert result.volume_confirms_trend

    assert result.momentum5 > 0
    assert result.momentum20 > 0

    assert result.above_ema20
    assert result.ema_above_sma20

    assert result.atr14 > 0


def test_get_scan_results_returns_results_for_all_symbols():
    """Detailed scan results should be returned for all symbols."""

    class MixedProvider(FakeProvider):
        def get_history(
            self,
            symbol: str,
            start,
            end,
        ) -> pd.DataFrame:
            if symbol == "PASS":
                close = list(range(100, 140))
            else:
                close = list(range(140, 100, -1))

            return make_market_df(
                close=close,
            )

    provider = MixedProvider()
    engine = ScannerEngine(provider)

    results = engine.get_scan_results(
        ["PASS", "FAIL"],
        None,
        None,
    )

    assert len(results) == 2

    assert results[0].symbol == "PASS"
    assert results[0].passed

    assert results[1].symbol == "FAIL"
    assert not results[1].passed


def test_get_ranked_scan_results_sorts_by_weighted_score_descending():
    """Results should be sorted from highest to lowest weighted score."""

    class RankedProvider(FakeProvider):
        def get_history(
            self,
            symbol: str,
            start,
            end,
        ) -> pd.DataFrame:
            if symbol == "STRONG":
                close = list(range(100, 140))

            elif symbol == "WEAK":
                close = (
                    list(range(100, 120))
                    + list(range(120, 100, -1))
                )

            else:
                close = list(range(140, 100, -1))

            return make_market_df(
                close=close,
            )

    provider = RankedProvider()
    engine = ScannerEngine(provider)

    results = engine.get_ranked_scan_results(
        ["FAIL", "WEAK", "STRONG"],
        None,
        None,
    )

    scores = [
        result.weighted_score
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )