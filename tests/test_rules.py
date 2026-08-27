"""Tests for scanner rules."""

import pandas as pd

from bist_radar.scanner.rules import (
    is_above_sma20,
    is_rsi_above_50,
    is_macd_bullish,
    passes_basic_strategy,
)
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_macd_bullish,
    is_rsi_above_50,
    is_volume_above_average,
    passes_basic_strategy,
)
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_macd_bullish,
    is_rsi_above_50,
    is_volume_above_average,
    passes_basic_strategy,
    volume_confirms_trend,
)

from bist_radar.scanner.rules import (
    is_above_ema20,
    ema_is_above_sma,
)

from bist_radar.scanner.rules import (
    ema_is_above_sma,
)

def test_is_above_sma20():
    """Close above SMA20 should return True."""

    df = pd.DataFrame(
        {
            "Close": [100],
            "SMA20": [90],
        }
    )

    assert is_above_sma20(df)

def test_is_rsi_above_50():
    """RSI above 50 should return True."""

    df = pd.DataFrame(
        {
            "RSI14": [55],
        }
    )

    assert is_rsi_above_50(df)

def test_is_macd_bullish():
    """MACD above Signal should return True."""

    df = pd.DataFrame(
        {
            "MACD": [2.5],
            "Signal": [1.8],
        }
    )

    assert is_macd_bullish(df)

def test_passes_basic_strategy():
    """All conditions satisfied should return True."""

    df = pd.DataFrame(
        {
            "Close": [100],
            "SMA20": [90],
            "RSI14": [60],
            "MACD": [2.5],
            "Signal": [1.5],
        }
    )

    assert passes_basic_strategy(df)

def test_is_volume_above_average_returns_true():
    """Volume ratio above 1 should return True."""

    df = pd.DataFrame(
        {
            "VolumeRatio": [1.25],
        }
    )

    assert is_volume_above_average(df)


def test_is_volume_above_average_returns_false():
    """Volume ratio at or below 1 should return False."""

    df = pd.DataFrame(
        {
            "VolumeRatio": [0.85],
        }
    )

    assert not is_volume_above_average(df)

def is_volume_above_average(df: pd.DataFrame) -> bool:
    """
    Return True if the latest volume is above its 20-day average.
    """

    latest = df.iloc[-1]

    return latest["VolumeRatio"] > 1.0

def test_volume_confirms_trend_returns_true():
    """Volume should confirm trend when price and volume are both strong."""

    df = pd.DataFrame(
        {
            "Close": [105],
            "SMA20": [100],
            "VolumeRatio": [1.25],
        }
    )

    assert volume_confirms_trend(df)


def test_volume_confirms_trend_returns_false():
    """Volume should not confirm trend when volume is below average."""

    df = pd.DataFrame(
        {
            "Close": [105],
            "SMA20": [100],
            "VolumeRatio": [0.80],
        }
    )

    assert not volume_confirms_trend(df)

def test_is_above_ema20_returns_true():
    df = pd.DataFrame(
        {
            "Close": [105],
            "EMA20": [100],
        }
    )

    assert is_above_ema20(df)


def test_is_above_ema20_returns_false():
    df = pd.DataFrame(
        {
            "Close": [95],
            "EMA20": [100],
        }
    )

    assert not is_above_ema20(df)


def test_ema_is_above_sma_returns_true():
    df = pd.DataFrame(
        {
            "SMA20": [100],
            "EMA20": [105],
        }
    )

    assert ema_is_above_sma(df)


def test_ema_is_above_sma_returns_false():
    df = pd.DataFrame(
        {
            "SMA20": [105],
            "EMA20": [100],
        }
    )

    assert not ema_is_above_sma(df)