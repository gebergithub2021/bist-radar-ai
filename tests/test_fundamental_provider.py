"""Tests for fundamental data provider."""

from bist_radar.fundamentals.models import FundamentalSnapshot
from bist_radar.fundamentals.provider import FundamentalProvider


class FakeFundamentalProvider(FundamentalProvider):
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        return FundamentalSnapshot(
            symbol=symbol,
            revenue=120_000_000_000.0,
            net_income=15_000_000_000.0,
            total_assets=180_000_000_000.0,
            total_equity=75_000_000_000.0,
            total_debt=20_000_000_000.0,
            cash=12_000_000_000.0,
        )


def test_fundamental_provider_returns_snapshot() -> None:
    provider = FakeFundamentalProvider()

    snapshot = provider.get_snapshot("ASELS")

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue == 120_000_000_000.0
    assert snapshot.net_income == 15_000_000_000.0