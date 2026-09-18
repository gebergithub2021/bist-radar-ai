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

        scale = self._parse_scale(
        raw_data.get("scale_text", "TL")
        )

        return FundamentalSnapshot(
            symbol=symbol,
            revenue=self._normalize_amount(
            raw_data.get("revenue"),
            scale,
        ),
        net_income=self._normalize_amount(
            raw_data.get("net_income"),
            scale,
        ),
        total_assets=self._normalize_amount(
            raw_data.get("total_assets"),
            scale,
        ),
        total_equity=self._normalize_amount(
            raw_data.get("total_equity"),
            scale,
        ),
        total_debt=self._normalize_amount(
            raw_data.get("total_debt"),
            scale,
        ),
        cash=self._normalize_amount(
            raw_data.get("cash"),
            scale,
        ),
        previous_revenue=self._normalize_amount(
            raw_data.get("previous_revenue"),
            scale,
        ),
        previous_net_income=self._normalize_amount(
            raw_data.get("previous_net_income"),
            scale,
        ),
        period_end=raw_data.get("period_end"),
        previous_period_end=raw_data.get(
            "previous_period_end"
        ),
    )
    def _normalize_amount(
        self,
        value: float | None,
        scale: int,
    ) -> float | None:
        """Normalize a KAP financial amount to TRY."""

        if value is None:
            return None

        return value * scale

    def _parse_scale(
        self,
        scale_text: str,
    ) -> int:
        """Parse KAP presentation scale."""

        normalized = scale_text.strip().upper()

        if normalized == "1000 TL":
            return 1_000

        return 1

def test_kap_fundamental_provider_maps_period_metadata() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "period_end": "2026-06-30",
        "previous_period_end": "2025-06-30",
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.period_end == "2026-06-30"
    assert snapshot.previous_period_end == "2025-06-30"

def test_kap_fundamental_provider_maps_period_metadata() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "period_end": "2026-06-30",
        "previous_period_end": "2025-06-30",
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.period_end == "2026-06-30"
    assert snapshot.previous_period_end == "2025-06-30"