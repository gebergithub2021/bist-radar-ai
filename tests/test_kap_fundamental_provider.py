"""Tests for KAP fundamental data provider."""

import pytest

from bist_radar.fundamentals.kap_provider import KapFundamentalProvider
from bist_radar.fundamentals.models import FundamentalSnapshot


def test_kap_fundamental_provider_returns_snapshot() -> None:
    class FakeFinancialClient:
        def fetch_report(
            self,
            symbol: str,
        ) -> dict:
            return {
                "scale_text": "TL",
                "period_end": None,
                "previous_period_end": None,
                "rows": {},
            }

    provider = KapFundamentalProvider(
        financial_client=FakeFinancialClient(),
    )

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


def test_kap_fundamental_provider_normalizes_thousand_try() -> None:
    provider = KapFundamentalProvider()

    normalized = provider._normalize_amount(
        value=88_494_252.0,
        scale=1_000,
    )

    assert normalized == 88_494_252_000.0


def test_kap_fundamental_provider_preserves_missing_amount() -> None:
    provider = KapFundamentalProvider()

    normalized = provider._normalize_amount(
        value=None,
        scale=1_000,
    )

    assert normalized is None


def test_kap_fundamental_provider_parses_thousand_try_scale() -> None:
    provider = KapFundamentalProvider()

    scale = provider._parse_scale("1000 TL")

    assert scale == 1_000

def test_kap_fundamental_provider_parses_dotted_thousand_try_scale() -> None:
    provider = KapFundamentalProvider()

    scale = provider._parse_scale("1.000 TL")

    assert scale == 1_000


def test_kap_fundamental_provider_parses_try_scale() -> None:
    provider = KapFundamentalProvider()

    scale = provider._parse_scale("TL")

    assert scale == 1


def test_kap_fundamental_provider_normalizes_snapshot_amounts() -> None:
    provider = KapFundamentalProvider()

    raw_data = {
        "scale_text": "1000 TL",
        "revenue": 88_494_252.0,
        "net_income": 14_449_834.0,
    }

    snapshot = provider._build_snapshot(
        symbol="ASELS",
        raw_data=raw_data,
    )

    assert snapshot.revenue == 88_494_252_000.0
    assert snapshot.net_income == 14_449_834_000.0

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


def test_kap_fundamental_provider_maps_revenue_xbrl_code() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_Revenue": {
            "current": 88_494_252.0,
            "previous": 74_000_000.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["revenue"] == 88_494_252.0
    assert raw_data["previous_revenue"] == 74_000_000.0


def test_kap_fundamental_provider_maps_net_income_xbrl_code() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_ProfitLoss": {
            "current": 14_449_834.0,
            "previous": 8_468_992.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["net_income"] == 14_449_834.0
    assert raw_data["previous_net_income"] == 8_468_992.0


def test_kap_fundamental_provider_maps_total_assets_xbrl_code() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_Assets": {
            "current": 549_748_035.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["total_assets"] == 549_748_035.0


def test_kap_fundamental_provider_maps_total_equity_xbrl_code() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_Equity": {
            "current": 308_524_609.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["total_equity"] == 308_524_609.0


def test_kap_fundamental_provider_maps_short_term_borrowings() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "kap-fr_CurrentBorowings": {
            "current": 10_000_000.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["short_term_borrowings"] == 10_000_000.0


def test_kap_fundamental_provider_maps_current_portion_of_long_term_borrowings() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
            "current": 4_000_000.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert (
        raw_data["current_portion_of_long_term_borrowings"]
        == 4_000_000.0
    )


def test_kap_fundamental_provider_maps_long_term_borrowings() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_LongtermBorrowings": {
            "current": 6_000_000.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["long_term_borrowings"] == 6_000_000.0


def test_kap_fundamental_provider_calculates_total_debt() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "kap-fr_CurrentBorowings": {
            "current": 10_000_000.0,
            "previous": 0.0,
        },
        "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
            "current": 4_000_000.0,
            "previous": 0.0,
        },
        "ifrs-full_LongtermBorrowings": {
            "current": 6_000_000.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["total_debt"] == 20_000_000.0


def test_kap_fundamental_provider_total_debt_is_none_when_component_missing() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "kap-fr_CurrentBorowings": {
            "current": 10_000_000.0,
            "previous": 0.0,
        },
        "ifrs-full_LongtermBorrowings": {
            "current": 6_000_000.0,
            "previous": 0.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["total_debt"] is None


def test_kap_fundamental_provider_maps_cash_and_equivalents() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_CashAndCashEquivalents": {
            "current": 12_000_000.0,
            "previous": 10_000_000.0,
        },
    }

    raw_data = provider._map_financial_rows(raw_rows)

    assert raw_data["cash"] == 12_000_000.0


def test_kap_fundamental_provider_builds_snapshot_from_financial_rows() -> None:
    provider = KapFundamentalProvider()

    raw_rows = {
        "ifrs-full_Revenue": {
            "current": 88_494_252.0,
            "previous": 74_000_000.0,
        },
        "ifrs-full_ProfitLoss": {
            "current": 14_449_834.0,
            "previous": 8_468_992.0,
        },
        "ifrs-full_Assets": {
            "current": 549_748_035.0,
            "previous": None,
        },
        "ifrs-full_Equity": {
            "current": 308_524_609.0,
            "previous": None,
        },
        "kap-fr_CurrentBorowings": {
            "current": 10_000_000.0,
            "previous": None,
        },
        "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
            "current": 4_000_000.0,
            "previous": None,
        },
        "ifrs-full_LongtermBorrowings": {
            "current": 6_000_000.0,
            "previous": None,
        },
        "ifrs-full_CashAndCashEquivalents": {
            "current": 12_000_000.0,
            "previous": None,
        },
    }

    snapshot = provider._build_snapshot_from_rows(
        symbol="ASELS",
        raw_rows=raw_rows,
        scale_text="1000 TL",
        period_end="2026-06-30",
        previous_period_end="2025-06-30",
    )

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue == 88_494_252_000.0
    assert snapshot.net_income == 14_449_834_000.0
    assert snapshot.previous_revenue == 74_000_000_000.0
    assert snapshot.previous_net_income == 8_468_992_000.0
    assert snapshot.total_assets == 549_748_035_000.0
    assert snapshot.total_equity == 308_524_609_000.0
    assert snapshot.total_debt == 20_000_000_000.0
    assert snapshot.cash == 12_000_000_000.0
    assert snapshot.period_end == "2026-06-30"
    assert snapshot.previous_period_end == "2025-06-30"


def test_kap_fundamental_provider_uses_financial_client() -> None:
    class FakeFinancialClient:
        def fetch_report(
            self,
            symbol: str,
        ) -> dict:
            assert symbol == "ASELS"

            return {
                "scale_text": "1000 TL",
                "period_end": "2026-06-30",
                "previous_period_end": "2025-06-30",
                "rows": {},
            }

    client = FakeFinancialClient()

    provider = KapFundamentalProvider(
        financial_client=client,
    )

    raw_report = provider._fetch_report_data(
        symbol="ASELS",
    )

    assert raw_report["scale_text"] == "1000 TL"
    assert raw_report["period_end"] == "2026-06-30"


def test_kap_fundamental_provider_get_snapshot_uses_financial_client() -> None:
    class FakeFinancialClient:
        def fetch_report(
            self,
            symbol: str,
        ) -> dict:
            assert symbol == "ASELS"

            return {
                "scale_text": "1000 TL",
                "period_end": "2026-06-30",
                "previous_period_end": "2025-06-30",
                "rows": {
                    "ifrs-full_Revenue": {
                        "current": 88_494_252.0,
                        "previous": 74_000_000.0,
                    },
                    "ifrs-full_ProfitLoss": {
                        "current": 14_449_834.0,
                        "previous": 8_468_992.0,
                    },
                    "ifrs-full_Assets": {
                        "current": 549_748_035.0,
                        "previous": None,
                    },
                    "ifrs-full_Equity": {
                        "current": 308_524_609.0,
                        "previous": None,
                    },
                    "kap-fr_CurrentBorowings": {
                        "current": 10_000_000.0,
                        "previous": None,
                    },
                    "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
                        "current": 4_000_000.0,
                        "previous": None,
                    },
                    "ifrs-full_LongtermBorrowings": {
                        "current": 6_000_000.0,
                        "previous": None,
                    },
                    "ifrs-full_CashAndCashEquivalents": {
                        "current": 12_000_000.0,
                        "previous": None,
                    },
                },
            }

    provider = KapFundamentalProvider(
        financial_client=FakeFinancialClient(),
    )

    snapshot = provider.get_snapshot("ASELS")

    assert snapshot.symbol == "ASELS"
    assert snapshot.revenue == 88_494_252_000.0
    assert snapshot.net_income == 14_449_834_000.0
    assert snapshot.previous_revenue == 74_000_000_000.0
    assert snapshot.previous_net_income == 8_468_992_000.0
    assert snapshot.total_debt == 20_000_000_000.0
    assert snapshot.cash == 12_000_000_000.0
    assert snapshot.period_end == "2026-06-30"
    assert snapshot.previous_period_end == "2025-06-30"


def test_kap_fundamental_provider_requires_financial_client() -> None:
    provider = KapFundamentalProvider()

    with pytest.raises(
        RuntimeError,
        match="Financial client is not configured",
    ):
        provider.get_snapshot("ASELS")


def test_kap_fundamental_provider_maps_real_kap_debt_xbrl_codes() -> None:
    provider = KapFundamentalProvider()

    rows = {
        "ifrs-full_Revenue": {
            "current": 88_494_252.0,
            "previous": 70_956_004.0,
        },
        "ifrs-full_ProfitLoss": {
            "current": 14_449_834.0,
            "previous": 8_468_992.0,
        },
        "ifrs-full_Assets": {
            "current": 549_748_035.0,
            "previous": 508_228_606.0,
        },
        "ifrs-full_Equity": {
            "current": 308_524_609.0,
            "previous": 296_498_504.0,
        },
        "kap-fr_CurrentBorowings": {
            "current": 25_398_173.0,
            "previous": 15_456_810.0,
        },
        "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
            "current": 39_308_899.0,
            "previous": 29_324_421.0,
        },
        "ifrs-full_LongtermBorrowings": {
            "current": 8_586_218.0,
            "previous": 5_921_301.0,
        },
        "ifrs-full_CashAndCashEquivalents": {
            "current": 39_468_926.0,
            "previous": 34_251_653.0,
        },
    }

    mapped = provider._map_financial_rows(
        raw_rows=rows,
    )

    assert mapped["short_term_borrowings"] == 25_398_173.0
    assert (
        mapped["current_portion_of_long_term_borrowings"]
        == 39_308_899.0
    )
    assert mapped["long_term_borrowings"] == 8_586_218.0
    assert mapped["total_debt"] == 73_293_290.0
    assert mapped["cash"] == 39_468_926.0