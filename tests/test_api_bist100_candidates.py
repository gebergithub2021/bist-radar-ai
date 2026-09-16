"""Tests for BIST 100 candidates API endpoint."""

from datetime import date

from fastapi.testclient import TestClient

from bist_radar.api.app import (
    app,
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