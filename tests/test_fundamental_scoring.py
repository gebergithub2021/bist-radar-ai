"""Tests for fundamental scoring."""

import pytest

from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
)
from bist_radar.fundamentals.scoring import (
    calculate_fundamental_score,
)


def test_bank_fundamental_score_uses_bank_metrics() -> None:
    result = FundamentalAnalysisResult(
        symbol="HALKB",
        roe=8.0,
        net_margin=None,
        revenue_growth=None,
        net_income_growth=35.0,
        debt_to_equity=None,
        net_debt=None,
        interest_income_growth=21.0,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        49.6
    )

def test_bank_fundamental_score_renormalizes_missing_metrics() -> None:
    result = FundamentalAnalysisResult(
        symbol="HALKB",
        roe=10.0,
        net_margin=None,
        revenue_growth=None,
        net_income_growth=25.0,
        debt_to_equity=None,
        net_debt=None,
        interest_income_growth=None,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        50.0,
    )

def test_standard_fundamental_score_uses_standard_metrics() -> None:
    result = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=20.0,
        net_margin=15.0,
        revenue_growth=24.0,
        net_income_growth=30.0,
        debt_to_equity=0.50,
        net_debt=5_000_000_000.0,
        interest_income_growth=None,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        81.0,
    )
def test_standard_fundamental_score_renormalizes_missing_metrics() -> None:
    result = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=12.5,
        net_margin=10.0,
        revenue_growth=None,
        net_income_growth=None,
        debt_to_equity=None,
        net_debt=None,
        interest_income_growth=None,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        50.0,
    )

def test_fundamental_score_caps_strong_metrics_at_100() -> None:
    result = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=100.0,
        net_margin=80.0,
        revenue_growth=200.0,
        net_income_growth=300.0,
        debt_to_equity=0.10,
        net_debt=None,
        interest_income_growth=None,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        100.0,
    )


def test_fundamental_score_floors_weak_metrics_at_zero() -> None:
    result = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=-10.0,
        net_margin=-5.0,
        revenue_growth=-20.0,
        net_income_growth=-30.0,
        debt_to_equity=3.0,
        net_debt=None,
        interest_income_growth=None,
    )

    score = calculate_fundamental_score(
        result=result,
    )

    assert score == pytest.approx(
        0.0,
    )