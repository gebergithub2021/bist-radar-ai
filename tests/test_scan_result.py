"""Tests for ScanResult model."""

from bist_radar.models.scan_result import ScanResult


def test_weighted_score_returns_100_when_all_rules_pass():
    result = ScanResult(
        symbol="TEST",
        above_sma20=True,
        rsi_above_50=True,
        macd_bullish=True,
        close=100,
        sma20=94,
        rsi14=65,
        histogram=0.6,
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

def test_sma_score_returns_zero_when_close_is_below_sma():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
        close=98,
        sma20=100,
    )

    assert result.sma_score == 0


def test_sma_score_returns_10_when_close_is_less_than_2_percent_above_sma():
    result = ScanResult(
        symbol="TEST",
        above_sma20=True,
        rsi_above_50=False,
        macd_bullish=False,
        close=101,
        sma20=100,
    )

    assert result.sma_score == 10


def test_sma_score_returns_20_when_close_is_between_2_and_5_percent_above_sma():
    result = ScanResult(
        symbol="TEST",
        above_sma20=True,
        rsi_above_50=False,
        macd_bullish=False,
        close=103,
        sma20=100,
    )

    assert result.sma_score == 20


def test_sma_score_returns_30_when_close_is_at_least_5_percent_above_sma():
    result = ScanResult(
        symbol="TEST",
        above_sma20=True,
        rsi_above_50=False,
        macd_bullish=False,
        close=106,
        sma20=100,
    )

    assert result.sma_score == 30

def test_rsi_score_returns_zero_below_45():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
        rsi14=40,
    )

    assert result.rsi_score == 0


def test_rsi_score_returns_10_between_45_and_50():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
        rsi14=47,
    )

    assert result.rsi_score == 10


def test_rsi_score_returns_20_between_50_and_60():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=True,
        macd_bullish=False,
        rsi14=55,
    )

    assert result.rsi_score == 20


def test_rsi_score_returns_30_between_60_and_70():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=True,
        macd_bullish=False,
        rsi14=65,
    )

    assert result.rsi_score == 30


def test_rsi_score_returns_15_at_or_above_70():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=True,
        macd_bullish=False,
        rsi14=75,
    )

    assert result.rsi_score == 15
def test_macd_score_returns_zero_when_histogram_is_negative():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
        close=100,
        histogram=-0.5,
    )

    assert result.macd_score == 0


def test_macd_score_returns_10_for_weak_positive_histogram():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=True,
        close=100,
        histogram=0.05,
    )

    assert result.macd_score == 10


def test_macd_score_returns_20_for_moderate_histogram():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=True,
        close=100,
        histogram=0.15,
    )

    assert result.macd_score == 20


def test_macd_score_returns_30_for_strong_histogram():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=True,
        close=100,
        histogram=0.30,
    )

    assert result.macd_score == 30


def test_macd_score_returns_40_for_very_strong_histogram():
    result = ScanResult(
        symbol="TEST",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=True,
        close=100,
        histogram=0.60,
    )

    assert result.macd_score == 40