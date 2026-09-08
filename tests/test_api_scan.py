from datetime import date, datetime

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
                volume_ratio=1.40,
                volume_confirms_trend=True,
                momentum5=4.5,
                momentum20=12.0,
                above_ema20=True,
                ema_above_sma20=True,
                position_52w=85.0,
                high_52w_distance=-5.0,
                atr14=6.0,
                atr_percent=2.73,
                adx14=35.0,
            )
        ]


class FakeKapEnricher:
    last_start: datetime | None = None
    last_end: datetime | None = None

    def enrich_all(
        self,
        results: list[ScanResult],
        start: datetime,
        end: datetime,
    ) -> list[ScanResult]:
        self.last_start = start
        self.last_end = end

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


fake_kap_enricher = FakeKapEnricher()


def override_scanner_engine() -> FakeScannerEngine:
    return FakeScannerEngine()


def override_kap_enricher() -> FakeKapEnricher:
    return fake_kap_enricher


app.dependency_overrides[
    get_scanner_engine
] = override_scanner_engine

app.dependency_overrides[
    get_kap_enricher
] = override_kap_enricher


client = TestClient(app)


def test_scan_endpoint_exists() -> None:
    response = client.get("/scan")

    assert response.status_code == 200

    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)


def test_scan_accepts_symbols_query_parameter() -> None:
    response = client.get(
        "/scan?symbols=THYAO,ASELS,TUPRS"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbols"] == [
        "THYAO",
        "ASELS",
        "TUPRS",
    ]

    assert "results" in data


def test_scan_returns_serialized_results() -> None:
    response = client.get(
        "/scan?symbols=ASELS"
    )

    assert response.status_code == 200

    data = response.json()

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


def test_scan_returns_kap_data() -> None:
    response = client.get(
        "/scan?symbols=ASELS"
    )

    assert response.status_code == 200

    data = response.json()
    result = data["results"][0]

    assert result["kap"] == {
        "has_news": True,
        "importance": "HIGH",
        "title": "Yeni İş İlişkisi",
        "url": (
            "https://www.kap.org.tr/"
            "tr/Bildirim/1655510"
        ),
    }


def test_scan_uses_30_day_kap_window() -> None:
    response = client.get(
        "/scan?symbols=ASELS"
    )

    assert response.status_code == 200

    assert fake_kap_enricher.last_start is not None
    assert fake_kap_enricher.last_end is not None

    kap_days = (
        fake_kap_enricher.last_end.date()
        - fake_kap_enricher.last_start.date()
    ).days

    assert kap_days == 30