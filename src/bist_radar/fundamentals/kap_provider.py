"""KAP fundamental data provider."""

from typing import Any

from bist_radar.fundamentals.models import FundamentalSnapshot
from bist_radar.fundamentals.provider import FundamentalProvider
from bist_radar.fundamentals.sector import (
    FundamentalSector,
    resolve_fundamental_sector,
)
from bist_radar.fundamentals.analysis import calculate_ttm_value


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

    def _previous_full_year_period(
        self,
        period_end: str,
    ) -> tuple[int, int] | None:
        """Return previous full-year KAP period for an interim report."""

        if "." in period_end:
            day_text, month_text, year_text = period_end.split(".")
        elif "-" in period_end:
            year_text, month_text, day_text = period_end.split("-")
        else:
            raise ValueError(
                f"Unsupported financial period date: {period_end}"
            )

        day = int(day_text)
        month = int(month_text)
        year = int(year_text)

        if day == 31 and month == 12:
            return None

        return year - 1, 4
    
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        """Return a fundamental snapshot for a symbol."""

        raw_report = self._fetch_report_data(
            symbol=symbol,
        )

        snapshot = self._build_snapshot_from_rows(
            symbol=symbol,
            raw_rows=raw_report["rows"],
            scale_text=raw_report["scale_text"],
            period_end=raw_report.get("period_end"),
            previous_period_end=raw_report.get(
                "previous_period_end"
            ),
        )

        period_end = snapshot.period_end

        if period_end is None:
            return snapshot

        previous_full_year_period = (
            self._previous_full_year_period(
                period_end=period_end,
            )
        )

        if previous_full_year_period is None:
            snapshot.ttm_net_income = snapshot.net_income
            return snapshot

        year, period = previous_full_year_period

        fetch_report_for_period = getattr(
            self.financial_client,
            "fetch_report_for_period",
            None,
        )

        if fetch_report_for_period is None:
            return snapshot

        previous_full_year_report = fetch_report_for_period(
            symbol=symbol,
            year=year,
            period=period,
        )

        previous_full_year_snapshot = (
            self._build_snapshot_from_rows(
                symbol=symbol,
                raw_rows=previous_full_year_report["rows"],
                scale_text=previous_full_year_report["scale_text"],
                period_end=previous_full_year_report.get(
                    "period_end"
                ),
                previous_period_end=previous_full_year_report.get(
                    "previous_period_end"
                ),
            )
        )

        snapshot.ttm_net_income = calculate_ttm_value(
            current_interim=snapshot.net_income,
            previous_interim=snapshot.previous_net_income,
            previous_full_year=(
                previous_full_year_snapshot.net_income
            ),
        )

        return snapshot

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
        interest_income=self._normalize_amount(
            raw_data.get("interest_income"),
            scale,
        ),
        previous_interest_income=self._normalize_amount(
            raw_data.get("previous_interest_income"),
            scale,
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
        """Parse KAP presentation currency scale."""

        normalized = (
            scale_text
            .upper()
            .replace("TL", "")
            .strip()
            .replace(".", "")
            .replace(",", "")
        )

        if not normalized:
            return 1

        try:
            return int(normalized)
        except ValueError:
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
            "kap-fr_CurrentBorowings",
            {},
        )

        current_portion_row = raw_rows.get(
            "kap-fr_CurrentPortionOfNoncurrentBorrowings",
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

    def _map_bank_financial_rows(
        self,
        raw_rows: dict[str, dict[str, float | None]],
    ) -> dict[str, float | None]:
        """Map KAP bank financial rows to internal field names."""

        interest_income_row = raw_rows.get(
            "kap-fr_InterestIncome",
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

        return {
            "revenue": None,
            "previous_revenue": None,
            "net_income": net_income_row.get("current"),
            "previous_net_income": net_income_row.get("previous"),
            "total_assets": assets_row.get("current"),
            "total_equity": equity_row.get("current"),
            "total_debt": None,
            "cash": None,
            "interest_income": interest_income_row.get("current"),
            "previous_interest_income": interest_income_row.get(
            "previous"
        ),
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

        sector = resolve_fundamental_sector(symbol)

        if sector == FundamentalSector.BANK:
            raw_data = self._map_bank_financial_rows(
            raw_rows,
        )
        else:
            raw_data = self._map_financial_rows(
            raw_rows,
        )

        raw_data["scale_text"] = scale_text
        raw_data["period_end"] = period_end
        raw_data["previous_period_end"] = previous_period_end

        return self._build_snapshot(
            symbol=symbol,
            raw_data=raw_data,
        )