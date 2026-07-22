import pandas as pd

from bist_radar.indicators.macd import calculate_macd


def test_calculate_macd():
    df = pd.DataFrame(
        {
            "Close": [
                100,101,102,103,104,
                105,106,107,108,109,
                110,111,112,113,114,
                115,116,117,118,119,
            ]
        }
    )

    macd = calculate_macd(df)

    assert len(macd) == len(df)

    assert "MACD" in macd.columns
    assert "Signal" in macd.columns
    assert "Histogram" in macd.columns

    assert pd.notna(macd.iloc[-1]["MACD"])
    assert pd.notna(macd.iloc[-1]["Signal"])
    assert pd.notna(macd.iloc[-1]["Histogram"])