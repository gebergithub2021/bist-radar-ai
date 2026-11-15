"""Yahoo Finance market data provider."""

from datetime import date

import pandas as pd
import yfinance as yf

from bist_radar.data.price_cache import PriceCache
from bist_radar.data.provider import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance implementation."""

    def __init__(self, cache_dir: str = ".cache/prices") -> None:
        self.price_cache = PriceCache(cache_dir=cache_dir)

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
        
        if start >= end:
            raise ValueError(
                "Start date must be earlier than end date."
            )

        
        missing_ranges = self.price_cache.get_download_ranges(
            symbol,
            start,
            end,
        )

        if not missing_ranges:
            cached_data = self.price_cache.load_range(
                symbol,
                start,
                end,
            )

            if cached_data is not None:
                return cached_data

        yahoo_symbol = self._normalize_symbol(symbol)
       
        downloaded_frames = []

        
        for range_start, range_end in missing_ranges:
            try:
                downloaded = yf.download(
                    yahoo_symbol,
                    start=range_start,
                    end=range_end,
                    progress=False,
                    auto_adjust=False,
                )
            except Exception as exc:
                print(
                    f"Yahoo Finance download failed "
                    f"for {symbol}: {exc}"
                )
                continue

            if not downloaded.empty:
                downloaded_frames.append(downloaded)


        if downloaded_frames:
            df = pd.concat(downloaded_frames)
        else:
            df = pd.DataFrame()

        
        if df.empty:
            cached_result = self.price_cache.load_range(
                symbol,
                start,
                end,
            )

            if cached_result is not None:
                return cached_result

            return pd.DataFrame(
                columns=[
                    "Date",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
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

        
        df.columns.name = None

        if not df.empty:
            self.price_cache.save(symbol, df)

        cached_result = self.price_cache.load_range(
            symbol,
            start,
            end,
        )

        if cached_result is not None:
            return cached_result

        return df


        return df