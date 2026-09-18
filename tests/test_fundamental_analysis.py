"""Tests for fundamental analysis."""

from bist_radar.fundamentals.analysis import (
    calculate_net_margin,
    calculate_roe,
)


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