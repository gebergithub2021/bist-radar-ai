"""Price momentum indicators."""

import pandas as pd


def calculate_price_change(
    df: pd.DataFrame,
    period: int,
) -> pd.Series:
    """Calculate percentage price change over a period."""

    return (
        df["Close"]
        .pct_change(periods=period)
        * 100
    )