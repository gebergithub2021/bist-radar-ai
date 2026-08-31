"""Technical indicator calculator."""

import pandas as pd

from bist_radar.indicators.adx import calculate_adx
from bist_radar.indicators.atr import (
    calculate_atr,
    calculate_atr_percent,
)


def calculate_indicators(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate all technical indicators used by BIST Radar."""

    required_columns = {
        "Close",
        "High",
        "Low",
        "Volume",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # -------------------------------------------------
    # Prepare data
    # -------------------------------------------------

    result = df.copy()

    # Some market-data providers may return an unfinished
    # trading-day row where OHLC values are NaN.
    #
    # Such rows must be removed before indicators are
    # calculated. Otherwise the latest row can produce
    # NaN momentum, ATR%, 52-week position, etc.
    result = result.dropna(
        subset=[
            "Close",
            "High",
            "Low",
        ]
    )

    result = result.reset_index(
        drop=True,
    )

    if result.empty:
        return result

    close = result["Close"]

    # -------------------------------------------------
    # SMA 20
    # -------------------------------------------------

    result["SMA20"] = close.rolling(
        window=20,
    ).mean()

    # -------------------------------------------------
    # EMA 20
    # -------------------------------------------------

    result["EMA20"] = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    # -------------------------------------------------
    # RSI 14
    # -------------------------------------------------

    delta = close.diff()

    gain = delta.clip(
        lower=0,
    )

    loss = -delta.clip(
        upper=0,
    )

    average_gain = gain.rolling(
        window=14,
    ).mean()

    average_loss = loss.rolling(
        window=14,
    ).mean()

    rs = (
        average_gain
        / average_loss
    )

    result["RSI14"] = (
        100
        - (
            100
            / (
                1
                + rs
            )
        )
    )

    # No losses means maximum RSI.
    no_loss = (
        (average_loss == 0)
        & (average_gain > 0)
    )

    result.loc[
        no_loss,
        "RSI14",
    ] = 100.0

    # Completely flat price movement is neutral.
    flat_market = (
        (average_loss == 0)
        & (average_gain == 0)
    )

    result.loc[
        flat_market,
        "RSI14",
    ] = 50.0

    # -------------------------------------------------
    # MACD
    # -------------------------------------------------

    ema12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    result["MACD"] = (
        ema12
        - ema26
    )

    result["Signal"] = result[
        "MACD"
    ].ewm(
        span=9,
        adjust=False,
    ).mean()

    result["Histogram"] = (
        result["MACD"]
        - result["Signal"]
    )

    # -------------------------------------------------
    # Volume
    # -------------------------------------------------

    result["VolumeSMA20"] = result[
        "Volume"
    ].rolling(
        window=20,
    ).mean()

    result["VolumeRatio"] = (
        result["Volume"]
        / result["VolumeSMA20"]
    )

    # -------------------------------------------------
    # Momentum
    # -------------------------------------------------

    result["Momentum5"] = (
        close.pct_change(
            periods=5,
            fill_method=None,
        )
        * 100
    )

    result["Momentum20"] = (
        close.pct_change(
            periods=20,
            fill_method=None,
        )
        * 100
    )

    # -------------------------------------------------
    # 52-week values
    #
    # 252 trading sessions is approximately one year.
    # -------------------------------------------------

    rolling_low_52w = close.rolling(
        window=252,
        min_periods=1,
    ).min()

    rolling_high_52w = close.rolling(
        window=252,
        min_periods=1,
    ).max()

    # Keep the actual 52-week high.
    #
    # ScannerEngine and existing tests expect this
    # column to be named High52W.
    result["High52W"] = (
        rolling_high_52w
    )

    result["Low52W"] = (
    rolling_low_52w
    )

    range_52w = (
        rolling_high_52w
        - rolling_low_52w
    )

    # Current position inside the 52-week range.
    result["Position52W"] = (
        (
            close
            - rolling_low_52w
        )
        / range_52w
        * 100
    )

    # If high and low are identical, there is no range.
    # Treat that situation as neutral.
    result.loc[
        range_52w == 0,
        "Position52W",
    ] = 50.0

    # Distance from the 52-week high in percentage.
    result["High52WDistance"] = (
        (
            close
            / rolling_high_52w
        )
        - 1
    ) * 100

    # -------------------------------------------------
    # ATR 14
    # -------------------------------------------------

    result["ATR14"] = calculate_atr(
        result,
        period=14,
    )

    result["ATRPercent"] = (
        calculate_atr_percent(
            result,
            period=14,
        )
    )

    # -------------------------------------------------
    # ADX 14
    # -------------------------------------------------

    result["ADX14"] = calculate_adx(
        result,
        period=14,
    )

    return result


def add_indicators(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Main indicator entry point used by the scanner."""

    return calculate_indicators(df)