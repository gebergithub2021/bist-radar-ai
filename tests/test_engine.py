"""Tests for scanner engine."""

import pandas as pd

from bist_radar.scanner.engine import ScannerEngine
from bist_radar.data.provider import MarketDataProvider


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
                "Close": [100],
                "SMA20": [90],
                "RSI14": [60],
                "MACD": [2.5],
                "Signal": [1.5],
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
    """A symbol should fail when one strategy condition is not satisfied."""

    class FailingProvider(FakeProvider):
        def get_history(
            self,
            symbol: str,
            start,
            end,
        ) -> pd.DataFrame:
            return pd.DataFrame(
                {
                    "Close": [80],
                    "SMA20": [90],
                    "RSI14": [60],
                    "MACD": [2.5],
                    "Signal": [1.5],
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