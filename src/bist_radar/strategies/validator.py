"""Validate strategy definitions before execution."""
import math

from bist_radar.strategies.models import (
    ComparisonOperator, Condition, LogicOperator, RuleGroup, StrategyDefinition,
)
from bist_radar.strategies.registry import ALLOWED_METRICS

MAX_DEPTH = 5
MAX_CONDITIONS = 30


def validate_strategy(strategy: StrategyDefinition) -> None:
    if not isinstance(strategy.name, str) or not strategy.name.strip() or len(strategy.name) > 100:
        raise ValueError("Strategy name must contain 1-100 characters.")
    if strategy.universe != "BIST100":
        raise ValueError("Only BIST100 is supported.")
    if not isinstance(strategy.rules, RuleGroup):
        raise ValueError("Strategy root must be a rule group.")

    count = 0

    def visit(node: Condition | RuleGroup, depth: int) -> None:
        nonlocal count
        if depth > MAX_DEPTH:
            raise ValueError("Strategy nesting limit exceeded.")
        if isinstance(node, RuleGroup):
            if not isinstance(node.operator, LogicOperator) or not node.children:
                raise ValueError("Rule group needs an operator and children.")
            for child in node.children:
                visit(child, depth + 1)
            return
        if not isinstance(node, Condition):
            raise ValueError("Unknown rule type.")
        count += 1
        if count > MAX_CONDITIONS:
            raise ValueError("Too many conditions.")
        if node.metric not in ALLOWED_METRICS:
            raise ValueError(f"Unsupported metric: {node.metric}")
        if not isinstance(node.operator, ComparisonOperator):
            raise ValueError("Unsupported comparison operator.")
        if (node.value is None) == (node.compare_to is None):
            raise ValueError("Exactly one of value or compare_to is required.")
        if node.compare_to is not None and node.compare_to not in ALLOWED_METRICS:
            raise ValueError(f"Unsupported comparison metric: {node.compare_to}")
        if node.value is not None and (isinstance(node.value, bool) or not isinstance(node.value, (int, float)) or not math.isfinite(node.value)):
            raise ValueError("Condition value must be a finite number.")

    visit(strategy.rules, 1)
