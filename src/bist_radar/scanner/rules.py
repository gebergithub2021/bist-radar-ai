"""Scanning rules."""

import pandas as pd


def is_above_sma20(df: pd.DataFrame) -> bool:
    """
    Return True if the latest close is above SMA20.
    """

    latest = df.iloc[-1]

    return latest["Close"] > latest["SMA20"]

def is_rsi_above_50(df: pd.DataFrame) -> bool:
    """
    Return True if the latest RSI14 is above 50.
    """

    latest = df.iloc[-1]

    return latest["RSI14"] > 50

def is_macd_bullish(df: pd.DataFrame) -> bool:
    """
    Return True if MACD is above Signal.
    """

    latest = df.iloc[-1]

    return latest["MACD"] > latest["Signal"]

def passes_basic_strategy(df: pd.DataFrame) -> bool:
    """
    Return True if the stock passes the basic strategy.
    """

    return (
        is_above_sma20(df)
        and is_rsi_above_50(df)
        and is_macd_bullish(df)
    )

def is_volume_above_average(df: pd.DataFrame) -> bool:
    """
    Return True if the latest volume is above its 20-day average.
    """

    latest = df.iloc[-1]

    return latest["VolumeRatio"] > 1.0

def volume_confirms_trend(df: pd.DataFrame) -> bool:
    """
    Return True if price is above SMA20
    and volume is above its 20-day average.
    """

    latest = df.iloc[-1]

    return (
        latest["Close"] > latest["SMA20"]
        and latest["VolumeRatio"] > 1.0
    )

def is_above_ema20(df: pd.DataFrame) -> bool:
    """Return True if latest close is above EMA20."""

    latest = df.iloc[-1]

    return latest["Close"] > latest["EMA20"]


def ema_is_above_sma(df: pd.DataFrame) -> bool:
    """Return True if EMA20 is above SMA20."""

    latest = df.iloc[-1]

    return latest["EMA20"] > latest["SMA20"]