"""Tests for fundamental analysis."""

from bist_radar.fundamentals.analysis import (
    analyze_fundamentals,
    calculate_debt_to_equity,
    calculate_growth_rate,
    calculate_net_debt,
    calculate_net_margin,
    calculate_roe,
)
from bist_radar.fundamentals.models import FundamentalSnapshot


def test_calculate_roe() -> None:
    roe = calculate_roe(
        net_income=15_000_000_000.0,
        total_equity=75_000_000_000.0,
    )

    assert roe == 20.0

def test_calculate_roe_returns_none_when_equity_is_zero() -> None:
    roe = calculate_roe(
        net_income=15_000_000_000.0,
        total_equity=0.0,
    )

    assert roe is None


def test_calculate_roe_returns_none_when_data_is_missing() -> None:
    assert calculate_roe(
        net_income=None,
        total_equity=75_000_000_000.0,
    ) is None

    assert calculate_roe(
        net_income=15_000_000_000.0,
        total_equity=None,
    ) is None

def test_calculate_net_margin() -> None:
    net_margin = calculate_net_margin(
        net_income=15_000_000_000.0,
        revenue=120_000_000_000.0,
    )

    assert net_margin == 12.5

def test_calculate_net_margin_returns_none_when_revenue_is_zero() -> None:
    net_margin = calculate_net_margin(
        net_income=15_000_000_000.0,
        revenue=0.0,
    )

    assert net_margin is None


def test_calculate_net_margin_returns_none_when_data_is_missing() -> None:
    assert calculate_net_margin(
        net_income=None,
        revenue=120_000_000_000.0,
    ) is None

    assert calculate_net_margin(
        net_income=15_000_000_000.0,
        revenue=None,
    ) is None

def test_calculate_debt_to_equity() -> None:
    debt_to_equity = calculate_debt_to_equity(
        total_debt=20_000_000_000.0,
        total_equity=80_000_000_000.0,
    )

    assert debt_to_equity == 0.25

def test_calculate_debt_to_equity_returns_none_when_equity_is_zero() -> None:
    debt_to_equity = calculate_debt_to_equity(
        total_debt=20_000_000_000.0,
        total_equity=0.0,
    )

    assert debt_to_equity is None


def test_calculate_debt_to_equity_returns_none_when_data_is_missing() -> None:
    assert calculate_debt_to_equity(
        total_debt=None,
        total_equity=80_000_000_000.0,
    ) is None

    assert calculate_debt_to_equity(
        total_debt=20_000_000_000.0,
        total_equity=None,
    ) is None

def test_calculate_net_debt() -> None:
    net_debt = calculate_net_debt(
        total_debt=20_000_000_000.0,
        cash=12_000_000_000.0,
    )

    assert net_debt == 8_000_000_000.0

def test_calculate_net_debt_can_be_negative() -> None:
    net_debt = calculate_net_debt(
        total_debt=20_000_000_000.0,
        cash=30_000_000_000.0,
    )

    assert net_debt == -10_000_000_000.0


def test_calculate_net_debt_returns_none_when_data_is_missing() -> None:
    assert calculate_net_debt(
        total_debt=None,
        cash=12_000_000_000.0,
    ) is None

    assert calculate_net_debt(
        total_debt=20_000_000_000.0,
        cash=None,
    ) is None

def test_calculate_growth_rate() -> None:
    growth = calculate_growth_rate(
        current_value=120_000_000_000.0,
        previous_value=100_000_000_000.0,
    )

    assert growth == 20.0

def test_calculate_growth_rate_can_be_negative() -> None:
    growth = calculate_growth_rate(
        current_value=80_000_000_000.0,
        previous_value=100_000_000_000.0,
    )

    assert growth == -20.0


def test_calculate_growth_rate_returns_none_when_previous_is_zero() -> None:
    growth = calculate_growth_rate(
        current_value=120_000_000_000.0,
        previous_value=0.0,
    )

    assert growth is None


def test_calculate_growth_rate_returns_none_when_data_is_missing() -> None:
    assert calculate_growth_rate(
        current_value=None,
        previous_value=100_000_000_000.0,
    ) is None

    assert calculate_growth_rate(
        current_value=120_000_000_000.0,
        previous_value=None,
    ) is None

def test_analyze_fundamentals_builds_analysis_result() -> None:
    snapshot = FundamentalSnapshot(
        symbol="ASELS",
        revenue=120_000_000_000.0,
        net_income=15_000_000_000.0,
        total_assets=180_000_000_000.0,
        total_equity=75_000_000_000.0,
        total_debt=20_000_000_000.0,
        cash=12_000_000_000.0,
        previous_revenue=100_000_000_000.0,
        previous_net_income=12_000_000_000.0,
    )

    result = analyze_fundamentals(snapshot)

    assert result.symbol == "ASELS"
    assert result.roe == 20.0
    assert result.net_margin == 12.5
    assert result.revenue_growth == 20.0
    assert result.net_income_growth == 25.0
    assert result.debt_to_equity == 20_000_000_000.0 / 75_000_000_000.0
    assert result.net_debt == 8_000_000_000.0

def test_analyze_fundamentals_handles_missing_data() -> None:
    snapshot = FundamentalSnapshot(
        symbol="ASELS",
        revenue=None,
        net_income=None,
        total_assets=None,
        total_equity=None,
        total_debt=None,
        cash=None,
        previous_revenue=None,
        previous_net_income=None,
    )

    result = analyze_fundamentals(snapshot)

    assert result.symbol == "ASELS"
    assert result.roe is None
    assert result.net_margin is None
    assert result.revenue_growth is None
    assert result.net_income_growth is None
    assert result.debt_to_equity is None
    assert result.net_debt is None

