"""Tests for Average True Range indicator."""

import pandas as pd
import pytest

from bist_radar.indicators.atr import calculate_atr
from bist_radar.indicators.atr import (
    calculate_atr,
    calculate_atr_percent,
)


def test_calculate_atr():
    """ATR should calculate average true range."""

    df = pd.DataFrame(
        {
            "High": [11, 12, 13, 14],
            "Low": [9, 10, 11, 12],
            "Close": [10, 11, 12, 13],
        }
    )

    result = calculate_atr(
        df,
        period=3,
    )

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])

    assert result.iloc[2] == pytest.approx(2.0)
    assert result.iloc[3] == pytest.approx(2.0)

def test_calculate_atr_percent():
    """ATR percentage should be relative to closing price."""

    df = pd.DataFrame(
        {
            "High": [101, 101, 101, 101],
            "Low": [99, 99, 99, 99],
            "Close": [100, 100, 100, 100],
        }
    )

    result = calculate_atr_percent(
        df,
        period=3,
    )

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])

    assert result.iloc[2] == pytest.approx(2.0)
    assert result.iloc[3] == pytest.approx(2.0)