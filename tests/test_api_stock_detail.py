from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from bist_radar.api.app import (
    app,
    get_kap_enricher,
    get_scanner_engine,
)
from bist_radar.models.scan_result import ScanResult


class FakeStockDetailScannerEngine:
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


class FakeStockDetailKapEnricher:
    def enrich_all(
        self,
        results: list[ScanResult],
        start: datetime,
        end: datetime,
    ) -> list[ScanResult]:
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


def override_stock_detail_scanner() -> (
    FakeStockDetailScannerEngine
):
    return FakeStockDetailScannerEngine()


def override_stock_detail_kap_enricher() -> (
    FakeStockDetailKapEnricher
):
    return FakeStockDetailKapEnricher()


@pytest.fixture(autouse=True)
def override_dependencies():
    original_scanner = app.dependency_overrides.get(
        get_scanner_engine
    )
    original_kap = app.dependency_overrides.get(
        get_kap_enricher
    )

    app.dependency_overrides[
        get_scanner_engine
    ] = override_stock_detail_scanner

    app.dependency_overrides[
        get_kap_enricher
    ] = override_stock_detail_kap_enricher

    yield

    if original_scanner is None:
        app.dependency_overrides.pop(
            get_scanner_engine,
            None,
        )
    else:
        app.dependency_overrides[
            get_scanner_engine
        ] = original_scanner

    if original_kap is None:
        app.dependency_overrides.pop(
            get_kap_enricher,
            None,
        )
    else:
        app.dependency_overrides[
            get_kap_enricher
        ] = original_kap


client = TestClient(app)


def test_stock_detail_endpoint_exists() -> None:
    response = client.get(
        "/stocks/ASELS"
    )

    assert response.status_code == 200


def test_stock_detail_returns_scan_result() -> None:
    response = client.get(
        "/stocks/asels"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["symbol"] == "ASELS"
    assert result["score"] == 90
    assert result["rating"] == "STRONG"

    assert result["scores"] == {
        "sma": 20,
        "rsi": 30,
        "macd": 40,
        "total": 90,
    }

    assert result["technical"]["close"] == 220.0


def test_stock_detail_returns_kap_data() -> None:
    response = client.get(
        "/stocks/ASELS"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["kap"] == {
        "has_news": True,
        "importance": "HIGH",
        "title": "Yeni İş İlişkisi",
        "url": (
            "https://www.kap.org.tr/"
            "tr/Bildirim/1655510"
        ),
    }