"""Mock market data provider."""

from datetime import date

import pandas as pd

from bist_radar.data.provider import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    """Mock implementation of the market data provider."""

    def get_symbols(self) -> list[str]:
        """Return a fixed list of symbols."""
        return ["THYAO", "TUPRS", "ASELS"]

    def get_history(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        """Return sample historical price data."""

        return pd.DataFrame(
            {
                "Date": pd.to_datetime(
                    [
                        "2026-07-01",
                        "2026-07-02",
                        "2026-07-03",
                        "2026-07-04",
                        "2026-07-05",
                    ]
                ),
                "Open": [300, 302, 305, 307, 310],
                "High": [305, 307, 309, 312, 315],
                "Low": [298, 300, 303, 306, 308],
                "Close": [303, 306, 307, 311, 314],
                "Volume": [1_000_000, 1_100_000, 1_300_000, 1_250_000, 1_500_000],
            }
        )