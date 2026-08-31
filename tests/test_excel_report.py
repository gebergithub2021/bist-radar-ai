"""Tests for Excel report generator."""

from pathlib import Path

import pandas as pd

from bist_radar.models.scan_result import ScanResult
from bist_radar.reports.excel_report import export_scan_results_to_excel
from datetime import date


def test_export_scan_results_to_excel(tmp_path: Path):
    """Scan results should be exported to an Excel workbook."""

    results = [
        ScanResult(
            symbol="AAA",
            above_sma20=True,
            rsi_above_50=True,
            macd_bullish=True,
            close=106,
            sma20=100,
            rsi14=65,
            macd=2.5,
            signal=1.8,
            histogram=0.6,
            kap_url="https://www.kap.org.tr/tr/Bildirim/1655510",
        ),
        ScanResult(
            symbol="BBB",
            above_sma20=False,
            rsi_above_50=False,
            macd_bullish=False,
            close=98,
            sma20=100,
            rsi14=40,
            macd=-1.0,
            signal=-0.5,
            histogram=-0.5,
            kap_url="https://www.kap.org.tr/tr/Bildirim/1655510",
        ),
    ]

    output_path = tmp_path / "scan_results.xlsx"

    export_scan_results_to_excel(
        results=results,
        output_path=output_path,
    )

    assert output_path.exists()

    df = pd.read_excel(
        output_path,
        sheet_name="BIST Radar",
    )

    assert list(df["Symbol"]) == ["AAA", "BBB"]
    assert list(df["Total Score"]) == [100, 0]
    assert list(df["Rating"]) == ["STRONG", "FAIL"]
    

    excel_file = pd.ExcelFile(output_path)

    assert "BIST Radar" in excel_file.sheet_names
    assert "Summary" in excel_file.sheet_names
    assert "KAP URL" in df.columns

    summary_df = pd.read_excel(
    output_path,
    sheet_name="Summary",
    )

    assert summary_df.loc[0, "Metric"] == "Scan Date"
    assert summary_df.loc[0, "Value"] == date.today().isoformat()

    assert summary_df.loc[1, "Metric"] == "Total Scanned"
    assert summary_df.loc[1, "Value"] == 2
    assert (
        df.loc[0, "KAP URL"]
        == "https://www.kap.org.tr/tr/Bildirim/1655510"
        )