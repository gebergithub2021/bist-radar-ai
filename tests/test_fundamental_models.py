"""Tests for fundamental data models."""

from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
    FundamentalSnapshot,
)


def test_fundamental_snapshot_stores_company_metrics() -> None:
    snapshot = FundamentalSnapshot(
        symbol="ASELS",
        revenue=120_000_000_000.0,
        net_income=15_000_000_000.0,
        total_assets=180_000_000_000.0,
        total_equity=75_000_000_000.0,
        total_debt=20_000_000_000.0,
        cash=12_000_000_000.0,
    )

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue == 120_000_000_000.0
    assert snapshot.net_income == 15_000_000_000.0
    assert snapshot.total_assets == 180_000_000_000.0
    assert snapshot.total_equity == 75_000_000_000.0
    assert snapshot.total_debt == 20_000_000_000.0
    assert snapshot.cash == 12_000_000_000.0


def test_fundamental_snapshot_allows_missing_metrics() -> None:
    snapshot = FundamentalSnapshot(
        symbol="ASELS",
        revenue=None,
        net_income=None,
        total_assets=None,
        total_equity=None,
        total_debt=None,
        cash=None,
    )

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue is None
    assert snapshot.net_income is None
    assert snapshot.total_assets is None
    assert snapshot.total_equity is None
    assert snapshot.total_debt is None
    assert snapshot.cash is None


def test_fundamental_snapshot_stores_previous_period_metrics() -> None:
    snapshot = FundamentalSnapshot(
        symbol="ASELS",
        revenue=120_000_000_000.0,
        net_income=15_000_000_000.0,
        total_assets=180_000_000_000.0,
        total_equity=75_000_000_000.0,
        total_debt=20_000_000_000.0,
        cash=12_000_000_000.0,
        previous_revenue=100_000_000_000.0,
        previous_net_income=12_000_000_000.0,
    )

    assert snapshot.previous_revenue == 100_000_000_000.0
    assert snapshot.previous_net_income == 12_000_000_000.0

def test_fundamental_analysis_result_stores_metrics() -> None:
    result = FundamentalAnalysisResult(
        symbol="ASELS",
        roe=20.0,
        net_margin=12.5,
        revenue_growth=20.0,
        net_income_growth=25.0,
        debt_to_equity=0.25,
        net_debt=8_000_000_000.0,
    )

    assert result.symbol == "ASELS"
    assert result.roe == 20.0
    assert result.net_margin == 12.5
    assert result.revenue_growth == 20.0
    assert result.net_income_growth == 25.0
    assert result.debt_to_equity == 0.25
    assert result.net_debt == 8_000_000_000.0