"""Scanner engine."""

from bist_radar.data.provider import MarketDataProvider
from bist_radar.indicators.calculator import add_indicators
from bist_radar.models.scan_result import ScanResult
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_macd_bullish,
    is_rsi_above_50,
    passes_basic_strategy,
)
from bist_radar.scanner.rules import volume_confirms_trend
from bist_radar.scanner.rules import (
    is_above_ema20,
    ema_is_above_sma,
)


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

        df = add_indicators(df)

        return passes_basic_strategy(df)

    def get_scan_result(
        self,
        symbol: str,
        start,
        end,
    ) -> ScanResult:
        """Return detailed scan result for a single symbol."""

        df = self.provider.get_history(
            symbol,
            start,
            end,
        )

        df = add_indicators(df)

        latest = df.iloc[-1]

        return ScanResult(
            symbol=symbol,
            above_sma20=bool(is_above_sma20(df)),
            rsi_above_50=bool(is_rsi_above_50(df)),
            macd_bullish=bool(is_macd_bullish(df)),
            close=float(latest["Close"]),
            sma20=float(latest["SMA20"]),
            rsi14=float(latest["RSI14"]),
            macd=float(latest["MACD"]),
            signal=float(latest["Signal"]),
            histogram=float(latest["Histogram"]),
            volume=float(latest["Volume"]),
            volume_sma20=float(latest["VolumeSMA20"]),
            volume_ratio=float(latest["VolumeRatio"]),
            volume_confirms_trend=bool(volume_confirms_trend(df)),
            momentum5=float(latest["Momentum5"]),
            momentum20=float(latest["Momentum20"]),
            above_ema20=bool(is_above_ema20(df)),
            ema_above_sma20=bool(ema_is_above_sma(df)),
            high_52w=float(latest["High52W"]),
            low_52w=float(latest["Low52W"]),
            position_52w=float(latest["Position52W"]),
            high_52w_distance=float(latest["High52WDistance"]),
        )

    def get_ranked_scan_results(
        self,
        symbols: list[str],
        start,
        end,
    ) -> list[ScanResult]:
        """Return scan results sorted by weighted score descending."""

        results = self.get_scan_results(
            symbols,
            start,
            end,
        )

        return sorted(
            results,
            key=lambda result: result.weighted_score,
            reverse=True,
        )
    
    def scan_symbols(
        self,
        symbols: list[str],
        start,
        end,
    ) -> list[str]:
        """Scan multiple symbols and return the ones that pass."""

        passed_symbols = []

        for symbol in symbols:
            if self.scan_symbol(
                symbol,
                start,
                end,
            ):
                passed_symbols.append(symbol)

        return passed_symbols

    def get_scan_results(
        self,
        symbols: list[str],
        start,
        end,
    ) -> list[ScanResult]:
        """Return detailed scan results for multiple symbols."""

        results = []

        for symbol in symbols:
            result = self.get_scan_result(
                symbol,
                start,
                end,
            )

            results.append(result)

        return results