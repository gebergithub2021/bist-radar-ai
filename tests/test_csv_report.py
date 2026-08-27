"""Tests for CSV report generator."""

from pathlib import Path

import pandas as pd

from bist_radar.models.scan_result import ScanResult
from bist_radar.reports.csv_report import export_scan_results_to_csv


def test_export_scan_results_to_csv(tmp_path: Path):
    """Scan results should be exported to CSV."""

    results = [
        ScanResult(
            symbol="AAA",
            above_sma20=True,
            rsi_above_50=True,
            macd_bullish=True,
            close=106,
            sma20=100,
            rsi14=65,
            histogram=0.6,
        ),
        ScanResult(
            symbol="BBB",
            above_sma20=False,
            rsi_above_50=False,
            macd_bullish=False,
            close=98,
            sma20=100,
            rsi14=40,
            histogram=-0.2,
        ),
    ]

    output_path = tmp_path / "scan_results.csv"

    export_scan_results_to_csv(
        results=results,
        output_path=output_path,
    )

    assert output_path.exists()

    df = pd.read_csv(
        output_path,
        sep= ";"
    )
    assert list(df.columns) == [
    "Symbol",
    "Close",
    "SMA20",
    "RSI14",
    "MACD",
    "Signal",
    "Histogram",
    
    "ADX14",
    "ADX Comment",
    
    "Volume Ratio",
    "Volume Confirm",
    
    "Momentum 5",
    "Momentum 5 Comment",
    "Momentum 20",
    "Momentum 20 Comment",
    
    "52W Position",
    "52W High Distance",
    "52W Comment",
    
    "ATR14",
    "ATR Percent",
    "Volatility",
    
    "SMA Score",
    "RSI Score",
    "MACD Score",
    "Total Score",
    "Rating",
    "KAP News",
    "KAP Importance",
    "KAP Title",
    ]

    assert list(df["Symbol"]) == ["AAA", "BBB"]
    assert list(df["Total Score"]) == [100, 0]
    assert list(df["Rating"]) == ["STRONG", "FAIL"]