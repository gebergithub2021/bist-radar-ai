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
            ],
        "Volume": [
            1000, 1100, 1200, 1300, 1400,
            1500, 1600, 1700, 1800, 1900,
            2000, 2100, 2200, 2300, 2400,
            2500, 2600, 2700, 2800, 2900,
            3000, 3100, 3200, 3300, 3400,
            3500, 3600, 3700, 3800, 3900,
            ],

        "High": [
            101, 102, 103, 104, 105,
            106, 107, 108, 109, 110,
            111, 112, 113, 114, 115,
            116, 117, 118, 119, 120,
            121, 122, 123, 124, 125,
            126, 127, 128, 129, 130,
            ],
        "Low": [
            99, 100, 101, 102, 103,
            104, 105, 106, 107, 108,
            109, 110, 111, 112, 113,
            114, 115, 116, 117, 118,
            119, 120, 121, 122, 123,
            124, 125, 126, 127, 128,
        ],
        }
    )

    result = add_indicators(df)

    assert "SMA20" in result.columns
    assert "EMA20" in result.columns
    assert "RSI14" in result.columns
    assert "MACD" in result.columns
    assert "Signal" in result.columns
    assert "Histogram" in result.columns
    assert "VolumeSMA20" in result.columns
    assert "VolumeRatio" in result.columns
    assert "Momentum5" in result.columns
    assert "Momentum20" in result.columns
    assert "High52W" in result.columns
    assert "Low52W" in result.columns
    assert "Position52W" in result.columns
    assert "High52WDistance" in result.columns
    assert "ATR14" in result.columns
    assert "ATRPercent" in result.columns
    assert "ADX14" in result.columns