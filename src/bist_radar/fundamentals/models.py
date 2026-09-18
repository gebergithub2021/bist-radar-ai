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