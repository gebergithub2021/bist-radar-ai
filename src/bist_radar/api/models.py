"""Pydantic response models for the API."""

from pydantic import BaseModel


class TechnicalResponse(BaseModel):
    close: float
    sma20: float
    rsi14: float
    macd: float
    signal: float
    histogram: float
    volume_ratio: float
    volume_confirms_trend: bool
    momentum5: float
    momentum20: float
    above_ema20: bool
    ema_above_sma20: bool
    position_52w: float
    high_52w_distance: float
    atr14: float
    atr_percent: float
    adx14: float


class ScoreBreakdownResponse(BaseModel):
    sma: int
    rsi: int
    macd: int
    total: int


class KapResponse(BaseModel):
    has_news: bool
    importance: str
    title: str
    url: str


class ScanItemResponse(BaseModel):
    symbol: str
    score: int
    rating: str
    technical: TechnicalResponse
    scores: ScoreBreakdownResponse
    kap: KapResponse


class ScanResponse(BaseModel):
    symbols: list[str]
    results: list[ScanItemResponse]