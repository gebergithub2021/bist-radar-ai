
"""Apply user-defined strategies to existing technical scan results."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from bist_radar.strategies.evaluator import evaluate_strategy
from bist_radar.strategies.models import (
    MatchStatus,
    StrategyDefinition,
    StrategyResult,
)


@dataclass(frozen=True)
class StockStrategyResult:
    symbol: str
    evaluation: StrategyResult


def scan_with_strategy(
    strategy: StrategyDefinition,
    stocks: Iterable[tuple[str, Mapping[str, object]]],
) -> list[StockStrategyResult]:
    """Evaluate a strategy against stock indicator values."""

    matches = []

    for symbol, metrics in stocks:
        evaluation = evaluate_strategy(strategy, metrics)

        if evaluation.status == MatchStatus.MATCH:
            matches.append(
                StockStrategyResult(
                    symbol=symbol,
                    evaluation=evaluation,
                )
            )

    return matches

def scan_engine_results_with_strategy(
    strategy: StrategyDefinition,
    scan_results: Iterable["ScanResult"],
) -> list[StockStrategyResult]:
    """Evaluate a strategy using existing ScannerEngine results."""

    from bist_radar.strategies.metric_adapter import (
        scan_result_to_metrics,
    )

    stocks = (
        (result.symbol, scan_result_to_metrics(result))
        for result in scan_results
    )

    return scan_with_strategy(
        strategy=strategy,
        stocks=stocks,
    )

def scan_bist100_with_strategy(
    strategy: StrategyDefinition,
    engine: object,
    universe: object = None,
) -> list[StockStrategyResult]:
    """Scan the full BIST 100 universe with a user strategy."""

    from bist_radar.api.bist100_scan_service import (
        build_bist100_scan_results,
    )

    scan_results = build_bist100_scan_results(
        engine=engine,
        kap_enricher=None,
        universe=universe,
    )

    return scan_engine_results_with_strategy(
        strategy=strategy,
        scan_results=scan_results,
    )
