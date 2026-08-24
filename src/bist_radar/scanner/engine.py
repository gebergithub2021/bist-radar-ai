"""Scanner engine."""

import pandas as pd

from bist_radar.data.provider import MarketDataProvider
from bist_radar.scanner.rules import passes_basic_strategy


class ScannerEngine:
    """Run scanning strategies on market data."""

    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def scan_symbol(
        self,
        symbol: str,
        start,
        end,
    ) -> bool:
        """Scan a single symbol."""

        df = self.provider.get_history(
            symbol,
            start,
            end,
        )

        return passes_basic_strategy(df)