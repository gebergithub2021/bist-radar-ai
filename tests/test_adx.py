"""Tests for Average Directional Index indicator."""

import pandas as pd

from bist_radar.indicators.adx import calculate_adx


def test_calculate_adx():
    """ADX should produce a valid value for trending data."""

    df = pd.DataFrame(
        {
            "High": list(range(101, 141)),
            "Low": list(range(99, 139)),
            "Close": list(range(100, 140)),
        }
    )

    result = calculate_adx(
        df,
        period=14,
    )

    assert result.notna().any()
    assert result.iloc[-1] >= 0
    assert result.iloc[-1] <= 100