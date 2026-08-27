"""Volume indicators."""

import pandas as pd


def calculate_volume_sma(
    df: pd.DataFrame,
    period: int = 20,
) -> pd.Series:
    """Calculate average trading volume."""

    return (
        df["Volume"]
        .rolling(window=period)
        .mean()
    )


def calculate_volume_ratio(
    df: pd.DataFrame,
    period: int = 20,
) -> pd.Series:
    """Calculate current volume relative to average volume."""

    average_volume = calculate_volume_sma(
        df,
        period=period,
    )

    return df["Volume"] / average_volume