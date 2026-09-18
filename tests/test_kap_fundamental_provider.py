"""Tests for KAP fundamental data provider."""

from bist_radar.fundamentals.kap_provider import (
    KapFundamentalProvider,
)
from bist_radar.fundamentals.models import FundamentalSnapshot


def test_kap_fundamental_provider_returns_snapshot() -> None:
    provider = KapFundamentalProvider()

    snapshot = provider.get_snapshot("ASELS")

    assert isinstance(snapshot, FundamentalSnapshot)
    assert snapshot.symbol == "ASELS"

def test_kap_fundamental_provider_maps_revenue() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "revenue": 120_000_000_000.0,
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue == 120_000_000_000.0

def test_kap_fundamental_provider_maps_net_income() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "net_income": 15_000_000_000.0,
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.symbol == "ASELS"
    assert snapshot.net_income == 15_000_000_000.0
def test_kap_fundamental_provider_maps_balance_sheet_metrics() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "total_assets": 180_000_000_000.0,
        "total_equity": 75_000_000_000.0,
        "total_debt": 20_000_000_000.0,
        "cash": 12_000_000_000.0,
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.total_assets == 180_000_000_000.0
    assert snapshot.total_equity == 75_000_000_000.0
    assert snapshot.total_debt == 20_000_000_000.0
    assert snapshot.cash == 12_000_000_000.0

def test_kap_fundamental_provider_maps_previous_period_metrics() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "previous_revenue": 100_000_000_000.0,
        "previous_net_income": 12_000_000_000.0,
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.previous_revenue == 100_000_000_000.0
    assert snapshot.previous_net_income == 12_000_000_000.0