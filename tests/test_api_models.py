from bist_radar.api.models import (
    KapResponse,
    ScanItemResponse,
    ScanResponse,
    ScoreBreakdownResponse,
    TechnicalResponse,
)
from fastapi.testclient import TestClient

from bist_radar.api.app import app


def test_scan_response_model() -> None:
    response = ScanResponse(
        symbols=["ASELS"],
        results=[
            ScanItemResponse(
                symbol="ASELS",
                score=90,
                rating="STRONG",
                technical=TechnicalResponse(
                    close=220.0,
                    sma20=210.0,
                    rsi14=62.0,
                    macd=3.2,
                    signal=2.0,
                    histogram=1.2,
                    volume_ratio=1.4,
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
                ),
                scores=ScoreBreakdownResponse(
                    sma=20,
                    rsi=30,
                    macd=40,
                    total=90,
                ),
                kap=KapResponse(
                    has_news=True,
                    importance="HIGH",
                    title="Yeni İş İlişkisi",
                    url=(
                        "https://www.kap.org.tr/"
                        "tr/Bildirim/1655510"
                    ),
                ),
            )
        ],
    )

    assert response.symbols == ["ASELS"]
    assert len(response.results) == 1

    result = response.results[0]

    assert result.symbol == "ASELS"
    assert result.score == 90
    assert result.rating == "STRONG"

    assert result.scores.total == 90
    assert result.kap.importance == "HIGH"


def test_scan_openapi_uses_scan_response() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    scan_schema = schema["paths"]["/scan"]["get"]

    response_schema = (
        scan_schema["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )

    assert response_schema == {
        "$ref": "#/components/schemas/ScanResponse"
    }