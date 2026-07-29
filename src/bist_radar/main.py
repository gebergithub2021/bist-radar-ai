"""Application entry point."""

import logging

from bist_radar.core.config import AppConfig
from bist_radar.core.logging import configure_logging
from bist_radar.data import provider
from datetime import date, timedelta
from bist_radar.data.yahoo_provider import YahooFinanceProvider
from bist_radar.indicators.sma import calculate_sma
from bist_radar.indicators.ema import calculate_ema
from bist_radar.indicators.rsi import calculate_rsi
from bist_radar.indicators.macd import calculate_macd
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_rsi_above_50,
    is_macd_bullish,
    passes_basic_strategy,
)


def main() -> None:
    """Run the application."""

    config = AppConfig()

    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info("%s v%s started.", config.app_name, config.version)

    provider = YahooFinanceProvider()
   
    print("=" * 50)
    print(config.app_name)
    print(f"Version : {config.version}")
    print("Status  : Foundation")
    print("=" * 50)

    """print("\nSemboller:")"""
    """print(provider.get_symbols())"""
    end = date.today()
    start = end - timedelta(days=365)

    print("\nTHYAO Örnek Verisi:")

    df = provider.get_history(
    "THYAO",
    start,
    end,
    )
    print(df.head())
    print()

    df["SMA20"] = calculate_sma(df, 20)
    print(df[["Date", "Close", "SMA20"]].tail())
    df["EMA20"] = calculate_ema(df, 20)

    print(
    df[
        [
            "Date",
            "Close",
            "SMA20",
            "EMA20",
        ]
    ].tail()
    )
    
    df["RSI14"] = calculate_rsi(df)

    print(
    df[
        [
            "Date",
            "Close",
            "SMA20",
            "EMA20",
            "RSI14",
        ]
    ].tail()
)
    macd_df = calculate_macd(df)
    df = df.join(macd_df)

    print(
    df[
        [
            "Date",
            "Close",
            "SMA20",
            "EMA20",
            "RSI14",
            "MACD",
            "Signal",
            "Histogram",
        ]
    ].tail()
)
    print("\nScanner Sonucu")

    print(
    "Close > SMA20:",
    is_above_sma20(df),
)

    print(
    "RSI14 > 50:",
    is_rsi_above_50(df),
)
    print(
    "MACD > Signal:",
    is_macd_bullish(df),
)
    print(
    "Basic Strategy:",
    passes_basic_strategy(df),
)
if __name__ == "__main__":
    main()