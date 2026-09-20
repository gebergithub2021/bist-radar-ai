from fastapi.testclient import TestClient

from bist_radar.api.app import (
    app,
    get_fundamental_provider,
)
from bist_radar.fundamentals.models import FundamentalSnapshot


class FakeFundamentalProvider:
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        assert symbol == "ASELS"

        return FundamentalSnapshot(
            symbol="ASELS",
            revenue=88_494_252_000.0,
            net_income=14_449_834_000.0,
            total_assets=549_748_035_000.0,
            total_equity=308_524_609_000.0,
            total_debt=73_293_290_000.0,
            cash=39_468_926_000.0,
            previous_revenue=70_956_004_000.0,
            previous_net_income=8_468_992_000.0,
            period_end="30.06.2026",
            previous_period_end="30.06.2025",
        )


def override_fundamental_provider() -> (
    FakeFundamentalProvider
):
    return FakeFundamentalProvider()


client = TestClient(app)


def test_fundamentals_endpoint_returns_snapshot() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_fundamental_provider

    try:
        response = client.get(
            "/fundamentals/asels"
        )

        assert response.status_code == 200

        result = response.json()

        assert result["symbol"] == "ASELS"
        assert result["revenue"] == 88_494_252_000.0
        assert result["net_income"] == 14_449_834_000.0
        assert result["total_debt"] == 73_293_290_000.0
        assert result["cash"] == 39_468_926_000.0

        assert result["period_end"] == "30.06.2026"
        assert (
            result["previous_period_end"]
            == "30.06.2025"
        )
    finally:
        if original_override is None:
            app.dependency_overrides.pop(
                get_fundamental_provider,
                None,
            )
        else:
            app.dependency_overrides[
                get_fundamental_provider
            ] = original_override

def test_fundamentals_endpoint_returns_analysis() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_fundamental_provider

    try:
        response = client.get(
            "/fundamentals/ASELS"
        )

        assert response.status_code == 200

        result = response.json()

        assert "analysis" in result

        analysis = result["analysis"]

        assert analysis["roe"] is not None
        assert analysis["net_margin"] is not None
        assert analysis["revenue_growth"] is not None
        assert analysis["net_income_growth"] is not None
        assert analysis["debt_to_equity"] is not None
        assert analysis["net_debt"] is not None
    finally:
        if original_override is None:
            app.dependency_overrides.pop(
                get_fundamental_provider,
                None,
            )
        else:
            app.dependency_overrides[
                get_fundamental_provider
            ] = original_override

class FailingFundamentalProvider:
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        raise RuntimeError(
            "KAP financial service error"
        )


def override_failing_fundamental_provider() -> (
    FailingFundamentalProvider
):
    return FailingFundamentalProvider()


def test_fundamentals_returns_503_when_provider_fails() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_failing_fundamental_provider

    try:
        response = client.get(
            "/fundamentals/ASELS"
        )

        assert response.status_code == 503

        assert response.json()["detail"] == (
            "Fundamental data service is temporarily unavailable."
        )
    finally:
        if original_override is None:
            app.dependency_overrides.pop(
                get_fundamental_provider,
                None,
            )
        else:
            app.dependency_overrides[
                get_fundamental_provider
            ] = original_override

