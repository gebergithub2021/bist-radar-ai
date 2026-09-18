"""KAP fundamental data provider."""

from typing import Any

from bist_radar.fundamentals.models import FundamentalSnapshot
from bist_radar.fundamentals.provider import FundamentalProvider


class KapFundamentalProvider(FundamentalProvider):
    """Fundamental data provider backed by KAP."""

    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        """Return a fundamental snapshot for a symbol."""

        return self._build_snapshot(
            symbol=symbol,
            raw_data={},
        )

    def _build_snapshot(
        self,
        symbol: str,
        raw_data: dict[str, Any],
    ) -> FundamentalSnapshot:
        """Build a fundamental snapshot from raw KAP data."""

        return FundamentalSnapshot(
            symbol=symbol,
            revenue=raw_data.get("revenue"),
            net_income=raw_data.get("net_income"),
            total_assets=raw_data.get("total_assets"),
            total_equity=raw_data.get("total_equity"),
            total_debt=raw_data.get("total_debt"),
            cash=raw_data.get("cash"),
            previous_revenue=raw_data.get("previous_revenue"),
            previous_net_income=raw_data.get("previous_net_income"),
        )