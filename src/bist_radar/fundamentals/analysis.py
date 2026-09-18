"""Fundamental analysis calculations."""


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