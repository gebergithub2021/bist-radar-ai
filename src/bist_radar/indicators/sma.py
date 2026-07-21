"""Simple Moving Average indicator."""

import pandas as pd


def calculate_sma(
    df: pd.DataFrame,
    period: int,
) -> pd.Series:
    """
    Calculate the Simple Moving Average (SMA).

    Args:
        df: Price DataFrame.
        period: Moving average period.

    Returns:
        SMA values.
    """

    return (
        df["Close"]
        .rolling(window=period)
        .mean()
    )