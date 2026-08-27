"""Tests for volume indicators."""

import pandas as pd
import pytest

from bist_radar.indicators.volume import (
    calculate_volume_ratio,
    calculate_volume_sma,
)


def test_calculate_volume_sma():
    """Volume SMA should calculate rolling average volume."""

    df = pd.DataFrame(
        {
            "Volume": [
                100,
                200,
                300,
                400,
                500,
            ]
        }
    )

    result = calculate_volume_sma(
        df,
        period=3,
    )

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])

    assert result.iloc[2] == pytest.approx(200)
    assert result.iloc[3] == pytest.approx(300)
    assert result.iloc[4] == pytest.approx(400)


def test_calculate_volume_ratio():
    """Volume ratio should compare volume with rolling average."""

    df = pd.DataFrame(
        {
            "Volume": [
                100,
                100,
                100,
                100,
                200,
            ]
        }
    )

    result = calculate_volume_ratio(
        df,
        period=3,
    )

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])

    assert result.iloc[2] == pytest.approx(1.0)
    assert result.iloc[3] == pytest.approx(1.0)

    # Last 3 volumes: 100, 100, 200
    # Average: 133.333...
    # Ratio: 200 / 133.333... = 1.5
    assert result.iloc[4] == pytest.approx(1.5)