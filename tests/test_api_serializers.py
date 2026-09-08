from bist_radar.api.serializers import scan_result_to_dict
from bist_radar.models.scan_result import ScanResult


def test_scan_result_to_dict() -> None:
    result = ScanResult(
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
        kap_has_news=True,
        kap_importance="HIGH",
        kap_title="Yeni İş İlişkisi",
        kap_reason="yeni iş ilişkisi",
        kap_url=(
            "https://www.kap.org.tr/"
            "tr/Bildirim/1655510"
        ),
    )

    data = scan_result_to_dict(result)

    assert data["symbol"] == "ASELS"
    assert data["score"] == 90
    assert data["rating"] == "STRONG"

    assert data["technical"]["close"] == 220.0
    assert data["technical"]["sma20"] == 210.0
    assert data["technical"]["rsi14"] == 62.0
    assert data["technical"]["adx14"] == 35.0

    assert data["scores"] == {
        "sma": 20,
        "rsi": 30,
        "macd": 40,
        "total": 90,
    }

    assert data["kap"] == {
        "has_news": True,
        "importance": "HIGH",
        "title": "Yeni İş İlişkisi",
        "url": (
            "https://www.kap.org.tr/"
            "tr/Bildirim/1655510"
        ),
    }