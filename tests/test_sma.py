import pandas as pd

from bist_radar.indicators.sma import calculate_sma


def test_calculate_sma():
    df = pd.DataFrame(
        {
            "Close": [10, 20, 30, 40, 50],
        }
    )

    result = calculate_sma(df, period=3)

    expected = [None, None, 20.0, 30.0, 40.0]

    for actual, exp in zip(result.tolist(), expected):
        if exp is None:
            assert pd.isna(actual)
        else:
            assert actual == exp