"""Tests for BIST 100 candidates API endpoint."""

from datetime import date

from fastapi.testclient import TestClient

from bist_radar.api.app import (
    app,
    get_fundamental_provider,
    get_kap_enricher,
    get_scanner_engine,
)
from bist_radar.models.scan_result import ScanResult


class FakeScannerEngine:
    def get_ranked_scan_results(
        self,
        symbols: list[str],
        start: date,
        end: date,
    ) -> list[ScanResult]:
        return [
            ScanResult(
                symbol="ASELS",
                above_sma20=True,
                rsi_above_50=True,
                macd_bullish=True,
                close=220.0,
                sma20=210.0,
                rsi14=62.0,
                macd=3.2,
                signal=2.0,
                histogram=1.2,
                adx14=35.0,
            )
        ]


def override_scanner_engine() -> FakeScannerEngine:
    return FakeScannerEngine()


def override_kap_enricher() -> None:
    return None


app.dependency_overrides[
    get_scanner_engine
] = override_scanner_engine

app.dependency_overrides[
    get_kap_enricher
] = override_kap_enricher


client = TestClient(app)


def test_bist100_candidates_endpoint_exists() -> None:
    response = client.get(
        "/bist100/candidates"
    )

    assert response.status_code == 200

def test_bist100_candidates_returns_candidate_response() -> None:
    response = client.get(
        "/bist100/candidates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["minimum_score"] == 85
    assert data["count"] == 1
    assert len(data["results"]) == 1

    result = data["results"][0]

    assert result["symbol"] == "ASELS"
    assert result["score"] == 90
    assert result["rating"] == "STRONG"

    assert result["scores"] == {
        "sma": 20,
        "rsi": 30,
        "macd": 40,
        "total": 90,
    }

class FakeCandidatesKapEnricher:
    def enrich_all(
        self,
        results,
        start,
        end,
    ):
        for result in results:
            result.kap_has_news = True
            result.kap_importance = "HIGH"
            result.kap_title = "Yeni İş İlişkisi"
            result.kap_reason = "yeni iş ilişkisi"
            result.kap_url = (
                "https://www.kap.org.tr/"
                "tr/Bildirim/1655510"
            )

        return results


def override_candidates_kap_enricher():
    return FakeCandidatesKapEnricher()


def test_bist100_candidates_returns_kap_data() -> None:
    original_override = app.dependency_overrides[
        get_kap_enricher
    ]

    app.dependency_overrides[
        get_kap_enricher
    ] = override_candidates_kap_enricher

    try:
        response = client.get(
            "/bist100/candidates"
        )

        assert response.status_code == 200

        data = response.json()
        result = data["results"][0]

        assert result["symbol"] == "ASELS"

        assert result["kap"] == {
            "has_news": True,
            "importance": "HIGH",
            "title": "Yeni İş İlişkisi",
            "url": (
                "https://www.kap.org.tr/"
                "tr/Bildirim/1655510"
            ),
        }
    finally:
        app.dependency_overrides[
            get_kap_enricher
        ] = original_override

class FailingCandidatesKapEnricher:
    def enrich_all(
        self,
        results,
        start,
        end,
    ):
        raise RuntimeError("KAP service failed")


def override_failing_candidates_kap_enricher():
    return FailingCandidatesKapEnricher()


def test_bist100_candidates_survives_kap_failure() -> None:
    original_override = app.dependency_overrides[
        get_kap_enricher
    ]

    app.dependency_overrides[
        get_kap_enricher
    ] = override_failing_candidates_kap_enricher

    try:
        response = client.get(
            "/bist100/candidates"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["minimum_score"] == 85
        assert data["count"] == 1

        result = data["results"][0]

        assert result["symbol"] == "ASELS"
        assert result["score"] == 90

        assert result["kap"] == {
            "has_news": False,
            "importance": "UNAVAILABLE",
            "title": "KAP service unavailable",
            "url": "",
        }
    finally:
        app.dependency_overrides[
            get_kap_enricher
        ] = original_override

from bist_radar.fundamentals.models import (
    FundamentalSnapshot,
)


class FakeFundamentalProvider:
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        return FundamentalSnapshot(
            symbol=symbol,
            revenue=200.0,
            net_income=20.0,
            total_assets=300.0,
            total_equity=100.0,
            total_debt=40.0,
            cash=10.0,
            previous_revenue=160.0,
            previous_net_income=10.0,
            period_end="30.06.2026",
            previous_period_end="30.06.2025",
            ttm_net_income=25.0,
        )


def override_fundamental_provider():
    return FakeFundamentalProvider()


def test_bist100_analysis_returns_technical_and_fundamental_data() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_fundamental_provider

    try:
        response = client.get(
            "/bist100/analysis"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["minimum_score"] == 85
        assert data["count"] == 1

        result = data["results"][0]

        assert result["technical"]["symbol"] == "ASELS"
        assert result["technical"]["score"] == 90

        assert result["fundamental"] == {
            "symbol": "ASELS",
            "roe": 20.0,
            "roe_ttm": 25.0,
            "net_margin": 10.0,
            "revenue_growth": 25.0,
            "net_income_growth": 100.0,
            "interest_income_growth": None,
            "debt_to_equity": 0.4,
            "net_debt": 30.0,
            "fundamental_score": 86.66666666666667,
        }
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
    ):
        raise RuntimeError(
            "Fundamental data unavailable"
        )


def override_failing_fundamental_provider():
    return FailingFundamentalProvider()


def test_bist100_analysis_preserves_candidate_when_fundamental_unavailable() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_failing_fundamental_provider

    try:
        response = client.get(
            "/bist100/analysis"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["minimum_score"] == 85
        assert data["count"] == 1

        result = data["results"][0]

        assert result["technical"]["symbol"] == "ASELS"
        assert result["technical"]["score"] == 90
        assert result["fundamental"] is None
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

class FakeBankFundamentalProvider:
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        return FundamentalSnapshot(
            symbol=symbol,
            revenue=None,
            net_income=20.0,
            total_assets=300.0,
            total_equity=100.0,
            total_debt=None,
            cash=None,
            previous_revenue=None,
            previous_net_income=10.0,
            period_end="30.06.2026",
            previous_period_end="30.06.2025",
        )


def override_bank_fundamental_provider():
    return FakeBankFundamentalProvider()

def test_bist100_analysis_serializes_partial_bank_fundamentals() -> None:
    original_override = app.dependency_overrides.get(
        get_fundamental_provider
    )

    app.dependency_overrides[
        get_fundamental_provider
    ] = override_bank_fundamental_provider

    try:
        response = client.get(
            "/bist100/analysis"
        )

        assert response.status_code == 200

        data = response.json()
        result = data["results"][0]

        assert result["fundamental"] == {
            "symbol": "ASELS",
            "roe": 20.0,
            "roe_ttm": None,
            "net_margin": None,
            "revenue_growth": None,
            "net_income_growth": 100.0,
            "interest_income_growth": None,
            "debt_to_equity": None,
            "net_debt": None,
            "fundamental_score": 88.88888888888889,
        }
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