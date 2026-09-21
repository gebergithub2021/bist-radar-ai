"""Tests for candidate analysis models."""

from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
)
from bist_radar.models.scan_result import ScanResult
from bist_radar.models.candidate_analysis import (
    CandidateAnalysis,
)


def test_candidate_analysis_keeps_technical_and_fundamental_separate() -> None:
    technical = ScanResult(
        symbol="ASELS",
        above_sma20=True,
        rsi_above_50=True,
        macd_bullish=True,
        close=110.0,
        sma20=100.0,
        rsi14=65.0,
        histogram=1.0,
    )

    fundamental = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=12.5,
        net_margin=16.0,
        revenue_growth=24.0,
        net_income_growth=30.0,
        debt_to_equity=0.25,
        net_debt=10_000_000_000.0,
    )

    result = CandidateAnalysis(
        technical=technical,
        fundamental=fundamental,
    )

    assert result.technical is technical
    assert result.fundamental is fundamental
    assert result.technical.weighted_score == 100