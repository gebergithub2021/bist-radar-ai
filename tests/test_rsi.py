"""Tests for RSI indicator."""

import pandas as pd

from bist_radar.indicators.rsi import calculate_rsi


def test_calculate_rsi():
    """RSI should return valid values."""

    df = pd.DataFrame(
        {
            "Close": [
                100, 101, 102, 101, 103,
                105, 104, 106, 108, 107,
                109, 110, 111, 112, 113,
                114, 113, 115, 116, 117,
            ]
        }
    )

    rsi = calculate_rsi(df)

    # Aynı uzunlukta olmalı
    assert len(rsi) == len(df)

    # İlk period-1 değer NaN olmalı
    assert rsi.iloc[:13].isna().all()

    # Son değer hesaplanmış olmalı
    assert pd.notna(rsi.iloc[-1])

    # RSI her zaman 0-100 arasında olmalı
    assert 0 <= rsi.iloc[-1] <= 100