"""Indicator calculator."""

import pandas as pd

from bist_radar.indicators.ema import calculate_ema
from bist_radar.indicators.macd import calculate_macd
from bist_radar.indicators.rsi import calculate_rsi
from bist_radar.indicators.sma import calculate_sma
from bist_radar.indicators.volume import (
    calculate_volume_ratio,
    calculate_volume_sma,
)
from bist_radar.indicators.momentum import calculate_price_change
from bist_radar.indicators.price_position import (
    calculate_52w_high,
    calculate_52w_high_distance,
    calculate_52w_low,
    calculate_52w_position,
)
from bist_radar.indicators.atr import calculate_atr
from bist_radar.indicators.atr import (
    calculate_atr,
    calculate_atr_percent,
)
from bist_radar.indicators.adx import calculate_adx

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to market data."""

    result = df.copy()

    result["SMA20"] = calculate_sma(result, period=20)
    result["EMA20"] = calculate_ema(result, period=20)
    result["RSI14"] = calculate_rsi(result, period=14)

    result["VolumeSMA20"] = calculate_volume_sma(
    result,
    period=20,
    )

    result["VolumeRatio"] = calculate_volume_ratio(
    result,
    period=20,
    )

    result["Momentum5"] = calculate_price_change(
    result,
    period=5,
    )

    result["Momentum20"] = calculate_price_change(
    result,
    period=20,
    )

    result["High52W"] = calculate_52w_high(result)
    result["Low52W"] = calculate_52w_low(result)
    result["Position52W"] = calculate_52w_position(result)
    result["High52WDistance"] = calculate_52w_high_distance(result)
    result["ATR14"] = calculate_atr(
    result,
    period=14,
    )

    result["ATRPercent"] = calculate_atr_percent(
    result,
    period=14,
    )

    result["ADX14"] = calculate_adx(
    result,
    period=14,
    )

    macd_df = calculate_macd(result)

    result = result.join(macd_df)

    return result