"""Tests for indicator calculator."""

import pandas as pd

from bist_radar.indicators.calculator import add_indicators


def test_add_indicators_adds_expected_columns():
    """Indicator calculator should add all expected columns."""

    df = pd.DataFrame(
        {
            "Close": [
                100, 101, 102, 103, 104,
                105, 106, 107, 108, 109,
                110, 111, 112, 113, 114,
                115, 116, 117, 118, 119,
                120, 121, 122, 123, 124,
                125, 126, 127, 128, 129,
            ]
        }
    )

    result = add_indicators(df)

    assert "SMA20" in result.columns
    assert "EMA20" in result.columns
    assert "RSI14" in result.columns
    assert "MACD" in result.columns
    assert "Signal" in result.columns
    assert "Histogram" in result.columns