
"""Convert existing scanner results into strategy metrics."""

from bist_radar.models.scan_result import ScanResult


def scan_result_to_metrics(
    result: ScanResult,
) -> dict[str, float]:
    """Extract technical indicators for user strategies."""

    return {
        "close": result.close,
        "sma20": result.sma20,
        "rsi14": result.rsi14,
        "macd": result.macd,
        "signal": result.signal,
        "histogram": result.histogram,
        "volume_ratio": result.volume_ratio,
        "momentum5": result.momentum5,
        "momentum20": result.momentum20,
        "atr_percent": result.atr_percent,
        "adx14": result.adx14,
        "position_52w": result.position_52w,
        "high_52w_distance": result.high_52w_distance,
        "weighted_score": result.weighted_score,
    }
