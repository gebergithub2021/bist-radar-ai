"""API serialization helpers."""

from bist_radar.models.scan_result import ScanResult


def scan_result_to_dict(
    result: ScanResult,
) -> dict[str, object]:
    """Convert ScanResult into API-friendly JSON data."""

    return {
        "symbol": result.symbol,
        "score": result.weighted_score,
        "rating": result.rating,
        "technical": {
            "close": result.close,
            "sma20": result.sma20,
            "rsi14": result.rsi14,
            "macd": result.macd,
            "signal": result.signal,
            "histogram": result.histogram,
            "volume_ratio": result.volume_ratio,
            "volume_confirms_trend": (
                result.volume_confirms_trend
            ),
            "momentum5": result.momentum5,
            "momentum20": result.momentum20,
            "above_ema20": result.above_ema20,
            "ema_above_sma20": (
                result.ema_above_sma20
            ),
            "position_52w": result.position_52w,
            "high_52w_distance": (
                result.high_52w_distance
            ),
            "atr14": result.atr14,
            "atr_percent": result.atr_percent,
            "adx14": result.adx14,
        },
        "scores": {
            "sma": result.sma_score,
            "rsi": result.rsi_score,
            "macd": result.macd_score,
            "total": result.weighted_score,
        },
        "kap": {
            "has_news": result.kap_has_news,
            "importance": result.kap_importance,
            "title": result.kap_title,
            "url": result.kap_url,
        },
    }