"""Allowlisted metrics supported by the initial strategy engine."""

TECHNICAL_METRICS = frozenset({
    "close", "sma20", "ema20", "rsi14", "macd", "signal",
    "histogram", "volume_ratio", "momentum5", "momentum20",
    "atr_percent", "adx14", "position_52w", "high_52w_distance",
    "weighted_score",
})

FUNDAMENTAL_METRICS = frozenset({
    "roe", "roe_ttm", "net_margin", "revenue_growth",
    "net_income_growth", "interest_income_growth",
    "debt_to_equity", "net_debt", "fundamental_score",
    "pe_ratio", "price_to_book", "ev_to_sales", "ev_to_ebitda",
})

ALLOWED_METRICS = TECHNICAL_METRICS | FUNDAMENTAL_METRICS
