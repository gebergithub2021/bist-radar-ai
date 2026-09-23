"""Fundamental analysis scoring."""

from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
)
from bist_radar.fundamentals.sector import (
    FundamentalSector,
    resolve_fundamental_sector,
)


def _score_positive_metric(
    value: float | None,
    maximum: float,
) -> float | None:
    """Normalize a positive metric to a 0-100 score."""

    if value is None:
        return None

    if value <= 0:
        return 0.0

    if value >= maximum:
        return 100.0

    return (value / maximum) * 100.0


def _score_debt_to_equity(
    value: float | None,
) -> float | None:
    """Score debt-to-equity where lower leverage is better."""

    if value is None:
        return None

    if value <= 0.50:
        return 100.0

    if value >= 2.00:
        return 0.0

    return (
        (2.00 - value)
        / (2.00 - 0.50)
    ) * 100.0


def _calculate_bank_score(
    result: FundamentalAnalysisResult,
) -> float:
    """Calculate fundamental score for a bank."""

    metrics = [
        (
            _score_positive_metric(
                value=result.roe,
                maximum=20.0,
            ),
            0.40,
        ),
        (
            _score_positive_metric(
                value=result.net_income_growth,
                maximum=50.0,
            ),
            0.30,
        ),
        (
            _score_positive_metric(
                value=result.interest_income_growth,
                maximum=50.0,
            ),
            0.30,
        ),
    ]

    available_metrics = [
        (score, weight)
        for score, weight in metrics
        if score is not None
    ]

    if not available_metrics:
        return 0.0

    available_weight = sum(
        weight
        for _, weight in available_metrics
    )

    weighted_total = sum(
        score * weight
        for score, weight in available_metrics
    )

    return weighted_total / available_weight


def _calculate_standard_score(
    result: FundamentalAnalysisResult,
) -> float:
    """Calculate fundamental score for a standard company."""

    metrics = [
        (
            _score_positive_metric(
                value=result.roe,
                maximum=25.0,
            ),
            0.25,
        ),
        (
            _score_positive_metric(
                value=result.net_margin,
                maximum=20.0,
            ),
            0.20,
        ),
        (
            _score_positive_metric(
                value=result.revenue_growth,
                maximum=30.0,
            ),
            0.20,
        ),
        (
            _score_positive_metric(
                value=result.net_income_growth,
                maximum=40.0,
            ),
            0.20,
        ),
        (
            _score_debt_to_equity(
                value=result.debt_to_equity,
            ),
            0.15,
        ),
    ]

    available_metrics = [
        (score, weight)
        for score, weight in metrics
        if score is not None
    ]

    if not available_metrics:
        return 0.0

    available_weight = sum(
        weight
        for _, weight in available_metrics
    )

    weighted_total = sum(
        score * weight
        for score, weight in available_metrics
    )

    return weighted_total / available_weight


def calculate_fundamental_score(
    result: FundamentalAnalysisResult,
) -> float:
    """Calculate sector-aware fundamental score."""

    sector = resolve_fundamental_sector(
        result.symbol,
    )

    if sector == FundamentalSector.BANK:
        return _calculate_bank_score(
            result=result,
        )

    return _calculate_standard_score(
        result=result,
    )