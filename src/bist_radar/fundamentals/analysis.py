"""Fundamental analysis calculations."""
from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
    FundamentalSnapshot,
)

def calculate_roe(
    net_income: float | None,
    total_equity: float | None,
) -> float | None:
    """Calculate return on equity as a percentage."""

    if net_income is None:
        return None

    if total_equity is None or total_equity == 0:
        return None

    return (net_income / total_equity) * 100

def calculate_net_margin(
    net_income: float | None,
    revenue: float | None,
) -> float | None:
    """Calculate net profit margin as a percentage."""

    if net_income is None:
        return None

    if revenue is None or revenue == 0:
        return None

    return (net_income / revenue) * 100

def calculate_debt_to_equity(
    total_debt: float | None,
    total_equity: float | None,
    ) -> float | None:
    """Calculate total debt to equity ratio."""

    if total_debt is None:
        return None

    if total_equity is None or total_equity == 0:
        return None

    return total_debt / total_equity

def calculate_net_debt(
    total_debt: float | None,
    cash: float | None,
    ) -> float | None:
    """Calculate net debt."""

    if total_debt is None or cash is None:
        return None

    return total_debt - cash

def calculate_growth_rate(
    current_value: float | None,
    previous_value: float | None,
    ) -> float | None:
    """Calculate percentage growth from previous to current value."""

    if current_value is None:
        return None

    if previous_value is None or previous_value == 0:
        return None

    return (
        (current_value - previous_value)
        / previous_value
    ) * 100

def calculate_ttm_value(
    current_interim: float | None,
    previous_interim: float | None,
    previous_full_year: float | None,
) -> float | None:
    """Calculate trailing twelve-month value."""

    if current_interim is None:
        return None

    if previous_interim is None:
        return None

    if previous_full_year is None:
        return None

    return (
        previous_full_year
        - previous_interim
        + current_interim
    )

def analyze_fundamentals(
    snapshot: FundamentalSnapshot,
    ) -> FundamentalAnalysisResult:
    """Calculate fundamental metrics from a raw snapshot."""

    return FundamentalAnalysisResult(
        symbol=snapshot.symbol,
        roe=calculate_roe(
        net_income=snapshot.net_income,
        total_equity=snapshot.total_equity,
        ),
        net_margin=calculate_net_margin(
        net_income=snapshot.net_income,
        revenue=snapshot.revenue,
        ),
        revenue_growth=calculate_growth_rate(
        current_value=snapshot.revenue,
        previous_value=snapshot.previous_revenue,
        ),
        net_income_growth=calculate_growth_rate(
        current_value=snapshot.net_income,
        previous_value=snapshot.previous_net_income,
        ),
        debt_to_equity=calculate_debt_to_equity(
        total_debt=snapshot.total_debt,
        total_equity=snapshot.total_equity,
        ),
        net_debt=calculate_net_debt(
        total_debt=snapshot.total_debt,
        cash=snapshot.cash,
        ),
        interest_income_growth=calculate_growth_rate(
        current_value=snapshot.interest_income,
        previous_value=snapshot.previous_interest_income,
        ),
        roe_ttm=calculate_roe(
        net_income=snapshot.ttm_net_income,
        total_equity=snapshot.total_equity,
),
)
