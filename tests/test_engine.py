"""Tests for scanner engine."""

import pandas as pd

from bist_radar.data.provider import MarketDataProvider
from bist_radar.scanner.engine import ScannerEngine


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
        return pd.DataFrame(
            {
                "Close": list(range(100, 140)),
                "Volume": list(range(1000, 5000, 100)),
            }
        )


def test_scan_symbol_returns_true_when_strategy_passes():
    """A symbol should pass when all strategy conditions are satisfied."""

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
            return pd.DataFrame(
                {
                    "Close": list(range(140, 100, -1)),
                    "Volume": [1000] * 40,
                }
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
                return pd.DataFrame(
                    {
                        "Close": list(range(100, 140)),
                        "Volume": [1000] * 40,
                    }
                )

            return pd.DataFrame(
                {
                    "Close": list(range(140, 100, -1)),
                    "Volume": [1000] * 40,
                }
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
    """Detailed scan result should contain rule outcomes and score."""

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
    assert result.volume_ratio > 0
    assert result.volume_confirms_trend
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
                return pd.DataFrame(
                    {
                        "Close": list(range(100, 140)),
                        "Volume": [1000] * 40,
                    }
                )

            return pd.DataFrame(
                {
                    "Close": list(range(140, 100, -1)),
                    "Volume": [1000] * 40,
                }
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
    assert results[0].score == 3
    assert results[0].passed

    assert results[1].symbol == "FAIL"
    assert results[1].score < 3
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
                return pd.DataFrame(
                    {
                        "Close": list(range(100, 140)),
                        "Volume": [1000] * 40,
                    }
                )

            if symbol == "WEAK":
                return pd.DataFrame(
                    {
                        "Close": list(range(100, 120))
                        + list(range(120, 100, -1)),
                        "Volume": [1000] * 40,
                        
                    }
                )

            return pd.DataFrame(
                {
                    "Close": list(range(140, 100, -1)),
                    "Volume": [1000] * 40,
                }
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