"""Moving Average Convergence Divergence (MACD) indicator."""

import pandas as pd

from bist_radar.indicators.ema import calculate_ema


def calculate_macd(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate MACD indicator.
    """

    ema12 = calculate_ema(df, period=12)
    ema26 = calculate_ema(df, period=26)

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False,
    ).mean()

    histogram = macd - signal

    return pd.DataFrame(
        {
            "MACD": macd,
            "Signal": signal,
            "Histogram": histogram,
        }
    )