"""Fundamental data models."""

from dataclasses import dataclass


@dataclass
class FundamentalSnapshot:
    """Raw fundamental snapshot for a company."""

    symbol: str
    revenue: float | None
    net_income: float | None
    total_assets: float | None
    total_equity: float | None
    total_debt: float | None
    cash: float | None
    previous_revenue: float | None = None
    previous_net_income: float | None = None

@dataclass
class FundamentalAnalysisResult:
    """Calculated fundamental analysis metrics."""

    symbol: str
    roe: float | None
    net_margin: float | None
    revenue_growth: float | None
    net_income_growth: float | None
    debt_to_equity: float | None
    net_debt: float | None