"""KAP fundamental data provider."""

from typing import Any

from bist_radar.fundamentals.models import FundamentalSnapshot
from bist_radar.fundamentals.provider import FundamentalProvider


class KapFundamentalProvider(FundamentalProvider):
    """Fundamental data provider backed by KAP."""
    def __init__(
        self,
        financial_client=None,
    ) -> None:
        self.financial_client = financial_client


    def _fetch_report_data(
        self,
        symbol: str,
    ) -> dict:
        """Fetch raw financial report data through the client."""

        if self.financial_client is None:
            raise RuntimeError(
            "Financial client is not configured"
        )

        return self.financial_client.fetch_report(
        symbol=symbol,
        )
    
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        """Return a fundamental snapshot for a symbol."""

        raw_report = self._fetch_report_data(
        symbol=symbol,
        )

        return self._build_snapshot_from_rows(
            symbol=symbol,
            raw_rows=raw_report["rows"],
            scale_text=raw_report["scale_text"],
            period_end=raw_report.get("period_end"),
            previous_period_end=raw_report.get(
            "previous_period_end"
            ),
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

    def _map_financial_rows(
        self,
        raw_rows: dict[str, dict[str, float | None]],
    ) -> dict[str, float | None]:
        """Map KAP financial rows to internal field names."""

        revenue_row = raw_rows.get(
            "ifrs-full_Revenue",
            {},
        )

        net_income_row = raw_rows.get(
            "ifrs-full_ProfitLoss",
            {},
        )

        assets_row = raw_rows.get(
            "ifrs-full_Assets",
            {},
        )

        equity_row = raw_rows.get(
            "ifrs-full_Equity",
            {},
        )

        short_term_borrowings_row = raw_rows.get(
            "ifrs-full_ShorttermBorrowings",
            {},
        )

        current_portion_row = raw_rows.get(
            "ifrs-full_CurrentPortionOfLongtermBorrowings",
            {},
        )

        long_term_borrowings_row = raw_rows.get(
            "ifrs-full_LongtermBorrowings",
            {},
        )

        short_term_borrowings = short_term_borrowings_row.get("current")
        current_portion = current_portion_row.get("current")
        long_term_borrowings = long_term_borrowings_row.get("current")

        if (
            short_term_borrowings is not None
            and current_portion is not None
            and long_term_borrowings is not None
        ):
            total_debt = (
                short_term_borrowings
                + current_portion
                + long_term_borrowings
        )
        else:
            total_debt = None

        cash_row = raw_rows.get(
            "ifrs-full_CashAndCashEquivalents",
             {},
        )

        return {
        "revenue": revenue_row.get("current"),
        "previous_revenue": revenue_row.get("previous"),
        "net_income": net_income_row.get("current"),
        "previous_net_income": net_income_row.get("previous"),
        "total_assets": assets_row.get("current"),
        "total_equity": equity_row.get("current"),
        "short_term_borrowings": short_term_borrowings_row.get("current"),
        "current_portion_of_long_term_borrowings": (current_portion_row.get("current")),
        "long_term_borrowings": long_term_borrowings_row.get("current"),
        "total_debt": total_debt,
        "cash": cash_row.get("current"),
        }

    def _build_snapshot_from_rows(
        self,
        symbol: str,
        raw_rows: dict[str, dict[str, float | None]],
        scale_text: str,
        period_end: str | None,
        previous_period_end: str | None,
    ) -> FundamentalSnapshot:
        """Build a snapshot from mapped KAP financial rows."""

        raw_data = self._map_financial_rows(raw_rows)

        raw_data["scale_text"] = scale_text
        raw_data["period_end"] = period_end
        raw_data["previous_period_end"] = previous_period_end

        return self._build_snapshot(
            symbol=symbol,
            raw_data=raw_data,
        )