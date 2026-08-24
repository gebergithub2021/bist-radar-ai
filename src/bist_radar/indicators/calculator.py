"""Indicator calculator."""

import pandas as pd

from bist_radar.indicators.ema import calculate_ema
from bist_radar.indicators.macd import calculate_macd
from bist_radar.indicators.rsi import calculate_rsi
from bist_radar.indicators.sma import calculate_sma


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to market data."""

    result = df.copy()

    result["SMA20"] = calculate_sma(result, period=20)
    result["EMA20"] = calculate_ema(result, period=20)
    result["RSI14"] = calculate_rsi(result, period=14)

    macd_df = calculate_macd(result)

    result = result.join(macd_df)

    return result