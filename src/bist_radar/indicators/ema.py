"""Exponential Moving Average indicator."""

import pandas as pd


def calculate_ema(
    df: pd.DataFrame,
    period: int,
) -> pd.Series:
    """
    Calculate EMA.
    """

    return (
        df["Close"]
        .ewm(span=period, adjust=False)
        .mean()
    )