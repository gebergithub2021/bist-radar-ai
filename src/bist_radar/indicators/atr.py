"""Average True Range indicator."""

import pandas as pd


def calculate_atr(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.Series:
    """Calculate Average True Range."""

    high_low = df["High"] - df["Low"]

    high_close = (
        df["High"] - df["Close"].shift(1)
    ).abs()

    low_close = (
        df["Low"] - df["Close"].shift(1)
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_close,
            low_close,
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(
        window=period,
    ).mean()

def calculate_atr_percent(
    df: pd.DataFrame,
    period: int = 14,
    ) -> pd.Series:
    """Calculate ATR as a percentage of closing price."""

    atr = calculate_atr(
        df,
        period=period,
    )

    return (atr / df["Close"]) * 100
