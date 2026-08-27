"""Tests for price momentum indicators."""

import pandas as pd
import pytest

from bist_radar.indicators.momentum import calculate_price_change


def test_calculate_price_change():
    """Price change should calculate percentage change over period."""

    df = pd.DataFrame(
        {
            "Close": [
                100,
                102,
                104,
                106,
                108,
                110,
            ]
        }
    )

    result = calculate_price_change(
        df,
        period=5,
    )

    # From 100 to 110 over 5 periods = 10%
    assert result.iloc[-1] == pytest.approx(10.0)