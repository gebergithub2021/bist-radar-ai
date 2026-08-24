"""Scanner engine."""

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

    def scan_symbols(
        self,
        symbols: list[str],
        start,
        end,
    ) -> list[str]:
        """Scan multiple symbols and return the ones that pass."""

        passed_symbols = []

        for symbol in symbols:
            if self.scan_symbol(symbol, start, end):
                passed_symbols.append(symbol)

        return passed_symbols