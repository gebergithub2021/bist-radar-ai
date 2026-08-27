"""Price position indicators."""

import pandas as pd


def calculate_52w_high(df: pd.DataFrame) -> pd.Series:
    """Calculate rolling 52-week high using 252 trading days."""

    return df["Close"].rolling(window=252).max()


def calculate_52w_low(df: pd.DataFrame) -> pd.Series:
    """Calculate rolling 52-week low using 252 trading days."""

    return df["Close"].rolling(window=252).min()


def calculate_52w_position(df: pd.DataFrame) -> pd.Series:
    """
    Calculate price position within the 52-week range.

    0 means the 52-week low.
    100 means the 52-week high.
    """

    high = calculate_52w_high(df)
    low = calculate_52w_low(df)

    price_range = high - low

    return ((df["Close"] - low) / price_range) * 100


def calculate_52w_high_distance(df: pd.DataFrame) -> pd.Series:
    """Calculate percentage distance from the 52-week high."""

    high = calculate_52w_high(df)

    return ((df["Close"] / high) - 1) * 100