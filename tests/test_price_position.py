"""Tests for price position indicators."""

import pandas as pd
import pytest

from bist_radar.indicators.price_position import (
    calculate_52w_high,
    calculate_52w_high_distance,
    calculate_52w_low,
    calculate_52w_position,
)


def test_calculate_52w_price_position():
    """52-week price position indicators should be calculated correctly."""

    prices = list(range(1, 253))

    df = pd.DataFrame(
        {
            "Close": prices,
        }
    )

    high = calculate_52w_high(df)
    low = calculate_52w_low(df)
    position = calculate_52w_position(df)
    high_distance = calculate_52w_high_distance(df)

    assert high.iloc[-1] == 252
    assert low.iloc[-1] == 1
    assert position.iloc[-1] == pytest.approx(100.0)
    assert high_distance.iloc[-1] == pytest.approx(0.0)