
from bist_radar.strategies.models import (
    ComparisonOperator,
    Condition,
    LogicOperator,
    RuleGroup,
    StrategyDefinition,
)
from bist_radar.strategies.strategy_scan_service import (
    scan_with_strategy,
)


def test_scan_returns_only_matching_stocks():
    strategy = StrategyDefinition(
        name="Güçlü Momentum",
        rules=RuleGroup(
            operator=LogicOperator.AND,
            children=(
                Condition(
                    metric="rsi14",
                    operator=ComparisonOperator.GT,
                    value=55,
                ),
                Condition(
                    metric="macd",
                    operator=ComparisonOperator.GT,
                    compare_to="signal",
                ),
            ),
        ),
    )

    stocks = [
        (
            "THYAO",
            {
                "rsi14": 62,
                "macd": 1.5,
                "signal": 1.0,
            },
        ),
        (
            "ASELS",
            {
                "rsi14": 48,
                "macd": 1.2,
                "signal": 0.8,
            },
        ),
        (
            "TUPRS",
            {
                "rsi14": 60,
                "macd": None,
                "signal": 0.5,
            },
        ),
    ]

    results = scan_with_strategy(strategy, stocks)

    assert len(results) == 1
    assert results[0].symbol == "THYAO"

from bist_radar.models.scan_result import ScanResult
from bist_radar.strategies.strategy_scan_service import (
    scan_engine_results_with_strategy,
)


def test_scanner_results_work_with_user_strategy():
    strategy = StrategyDefinition(
        name="RSI ve MACD Stratejisi",
        rules=RuleGroup(
            operator=LogicOperator.AND,
            children=(
                Condition(
                    metric="rsi14",
                    operator=ComparisonOperator.GT,
                    value=55,
                ),
                Condition(
                    metric="macd",
                    operator=ComparisonOperator.GT,
                    compare_to="signal",
                ),
            ),
        ),
    )

    scan_results = [
        ScanResult(
            symbol="THYAO",
            above_sma20=True,
            rsi_above_50=True,
            macd_bullish=True,
            close=300,
            sma20=280,
            rsi14=62,
            macd=2.5,
            signal=1.8,
        ),
        ScanResult(
            symbol="ASELS",
            above_sma20=True,
            rsi_above_50=False,
            macd_bullish=True,
            close=120,
            sma20=115,
            rsi14=48,
            macd=1.5,
            signal=1.0,
        ),
    ]

    results = scan_engine_results_with_strategy(
        strategy=strategy,
        scan_results=scan_results,
    )

    assert len(results) == 1
    assert results[0].symbol == "THYAO"

from unittest.mock import patch

from bist_radar.strategies.strategy_scan_service import (
    scan_bist100_with_strategy,
)


def test_bist100_strategy_scans_without_score_filter():
    strategy = StrategyDefinition(
        name="Düşük RSI Stratejisi",
        rules=RuleGroup(
            operator=LogicOperator.AND,
            children=(
                Condition(
                    metric="rsi14",
                    operator=ComparisonOperator.LT,
                    value=30,
                ),
            ),
        ),
    )

    low_score_stock = ScanResult(
        symbol="TEST1",
        above_sma20=False,
        rsi_above_50=False,
        macd_bullish=False,
        close=100,
        sma20=110,
        rsi14=25,
        macd=-1,
        signal=0,
    )

    with patch(
        "bist_radar.api.bist100_scan_service.build_bist100_scan_results"
    ) as mock_scan:
        mock_scan.return_value = [low_score_stock]

        results = scan_bist100_with_strategy(
            strategy=strategy,
            engine=object(),
        )

    assert low_score_stock.weighted_score < 85
    assert len(results) == 1
    assert results[0].symbol == "TEST1"

    mock_scan.assert_called_once()
    assert mock_scan.call_args.kwargs["kap_enricher"] is None
