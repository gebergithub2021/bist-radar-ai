"""Tests for fundamental data models."""

from bist_radar.fundamentals.models import FundamentalSnapshot


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