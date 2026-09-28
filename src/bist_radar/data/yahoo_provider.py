"""Yahoo Finance market data provider."""

from datetime import date

import pandas as pd
import yfinance as yf

from bist_radar.data.provider import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance implementation."""
    def _normalize_symbol():
        ...

    def _download():
        ...

    def _normalize_dataframe():
        ...
    def _normalize_symbol(self, symbol: str) -> str:
        """Convert a BIST symbol to Yahoo Finance format."""
        return f"{symbol.upper()}.IS"

    def get_symbols(self) -> list[str]:
        raise NotImplementedError("Yahoo provider does not supply symbol lists.")

    def get_market_cap(
        self,
        symbol: str,
    ) -> float | None:
        """Return current market capitalization for a symbol."""

        yahoo_symbol = self._normalize_symbol(symbol)

        try:
            ticker = yf.Ticker(yahoo_symbol)

            market_cap = ticker.fast_info.get(
            "marketCap"
            )

            if market_cap is None:
                market_cap = ticker.info.get(
                "marketCap"
            )

            if market_cap is None:
                return None

            return float(market_cap)

        except Exception:
            return None

    def get_history(
    self,
    symbol: str,
    start: date,
    end: date,
) -> pd.DataFrame:
        yahoo_symbol = self._normalize_symbol(symbol)
        df = yf.download(
        yahoo_symbol,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,
    )
        if isinstance(df.columns, pd.MultiIndex):df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df = df[
        [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        ]
        
]
        df.columns.name = None
        return df