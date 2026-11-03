"""Evaluate user rules using three-valued logic (MATCH/NO_MATCH/UNKNOWN)."""
import math
from collections.abc import Mapping

from bist_radar.strategies.models import (
    ComparisonOperator, Condition, ConditionResult, LogicOperator,
    MatchStatus, RuleGroup, StrategyDefinition, StrategyResult,
)
from bist_radar.strategies.validator import validate_strategy


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _compare(left: float, operator: ComparisonOperator, right: float) -> bool:
    return {
        ComparisonOperator.GT: lambda: left > right,
        ComparisonOperator.GTE: lambda: left >= right,
        ComparisonOperator.LT: lambda: left < right,
        ComparisonOperator.LTE: lambda: left <= right,
        ComparisonOperator.EQ: lambda: left == right,
        ComparisonOperator.NE: lambda: left != right,
    }[operator]()


def evaluate_strategy(strategy: StrategyDefinition, metrics: Mapping[str, object]) -> StrategyResult:
    """Return a status and individual condition explanations.

    Missing, nonnumeric, and nonfinite metrics yield UNKNOWN. Group semantics:
    AND: any NO_MATCH wins; otherwise UNKNOWN if any unknown.
    OR: any MATCH wins; otherwise UNKNOWN if any unknown.
    """
    validate_strategy(strategy)
    details: list[ConditionResult] = []

    def visit(node: Condition | RuleGroup) -> MatchStatus:
        if isinstance(node, Condition):
            actual = _number(metrics.get(node.metric))
            expected = _number(metrics.get(node.compare_to)) if node.compare_to is not None else _number(node.value)
            if actual is None or expected is None:
                status = MatchStatus.UNKNOWN
            else:
                status = MatchStatus.MATCH if _compare(actual, node.operator, expected) else MatchStatus.NO_MATCH
            details.append(ConditionResult(node, status, actual, expected))
            return status

        # Evaluate all children to provide a complete per-condition explanation.
        statuses = [visit(child) for child in node.children]
        if node.operator is LogicOperator.AND:
            if MatchStatus.NO_MATCH in statuses:
                return MatchStatus.NO_MATCH
            if MatchStatus.UNKNOWN in statuses:
                return MatchStatus.UNKNOWN
            return MatchStatus.MATCH
        if MatchStatus.MATCH in statuses:
            return MatchStatus.MATCH
        if MatchStatus.UNKNOWN in statuses:
            return MatchStatus.UNKNOWN
        return MatchStatus.NO_MATCH

    status = visit(strategy.rules)
    return StrategyResult(status=status, conditions=tuple(details))
