"""Tests for ScanResult model."""

from bist_radar.models.scan_result import ScanResult


def test_weighted_score_returns_100_when_all_rules_pass():
    result = ScanResult(
        symbol="TEST",
        above_sma20=True,
        rsi_above_50=True,
        macd_bullish=True,
    )

    assert result.weighted_score == 100

def test_weighted_score_returns_zero_when_all_rules_fail():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
    )

    assert result.weighted_score == 0