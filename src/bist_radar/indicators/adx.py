"""Average Directional Index indicator."""

import pandas as pd


def calculate_adx(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.Series:
    """Calculate Average Directional Index."""

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where(
        (plus_dm > minus_dm) & (plus_dm > 0),
        0.0,
    )

    minus_dm = minus_dm.where(
        (minus_dm > plus_dm) & (minus_dm > 0),
        0.0,
    )

    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = true_range.rolling(
        window=period,
    ).mean()

    plus_di = (
        100
        * plus_dm.rolling(window=period).mean()
        / atr
    )

    minus_di = (
        100
        * minus_dm.rolling(window=period).mean()
        / atr
    )

    dx = (
        (plus_di - minus_di).abs()
        / (plus_di + minus_di)
        * 100
    )

    return dx.rolling(
        window=period,
    ).mean()