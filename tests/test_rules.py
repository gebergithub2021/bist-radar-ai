"""Tests for scanner rules."""

import pandas as pd

from bist_radar.scanner.rules import (
    is_above_sma20,
    is_rsi_above_50,
    is_macd_bullish,
    passes_basic_strategy,
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