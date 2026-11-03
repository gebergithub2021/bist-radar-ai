"""Unit tests for the independent user strategy rule engine."""
import math
import pytest

from bist_radar.strategies.evaluator import evaluate_strategy
from bist_radar.strategies.models import (
    ComparisonOperator as C, Condition, LogicOperator as L,
    MatchStatus as S, RuleGroup, StrategyDefinition,
)


def strategy(*children, operator=L.AND):
    return StrategyDefinition("Test strategy", RuleGroup(operator, tuple(children)))


def condition(metric, op=C.GT, value=50, compare_to=None):
    return Condition(metric, op, None if compare_to else value, compare_to)


def test_all_conditions_match():
    result = evaluate_strategy(strategy(condition("rsi14"), condition("adx14", value=25)), {"rsi14": 60, "adx14": 30})
    assert result.status is S.MATCH
    assert len(result.conditions) == 2


def test_and_rejects_one_failure():
    result = evaluate_strategy(strategy(condition("rsi14"), condition("adx14", value=25)), {"rsi14": 45, "adx14": 30})
    assert result.status is S.NO_MATCH


def test_or_matches_with_unknown_child():
    result = evaluate_strategy(strategy(condition("roe_ttm"), condition("rsi14"), operator=L.OR), {"rsi14": 60})
    assert result.status is S.MATCH
    assert result.conditions[0].status is S.UNKNOWN


def test_and_unknown_when_no_failure():
    result = evaluate_strategy(strategy(condition("roe_ttm"), condition("rsi14")), {"rsi14": 60})
    assert result.status is S.UNKNOWN


def test_or_unknown_when_no_match():
    result = evaluate_strategy(strategy(condition("roe_ttm"), condition("rsi14")), {"rsi14": 40})
    assert result.status is S.NO_MATCH
    result = evaluate_strategy(strategy(condition("roe_ttm"), condition("rsi14"), operator=L.OR), {"rsi14": 40})
    assert result.status is S.UNKNOWN


def test_nested_groups():
    inner = RuleGroup(L.OR, (condition("roe_ttm", value=15), condition("rsi14")))
    result = evaluate_strategy(strategy(condition("adx14", value=25), inner), {"adx14": 30, "rsi14": 60})
    assert result.status is S.MATCH


def test_metric_to_metric_comparison():
    result = evaluate_strategy(strategy(condition("macd", compare_to="signal")), {"macd": 1.5, "signal": 1.0})
    assert result.status is S.MATCH


@pytest.mark.parametrize("missing", [None, float("nan"), float("inf"), "unavailable", True])
def test_invalid_market_values_are_unknown(missing):
    result = evaluate_strategy(strategy(condition("rsi14")), {"rsi14": missing})
    assert result.status is S.UNKNOWN


@pytest.mark.parametrize("bad", [
    strategy(condition("not_allowed")),
    strategy(condition("rsi14", value=float("nan"))),
    StrategyDefinition(" ", RuleGroup(L.AND, (condition("rsi14"),))),
    StrategyDefinition("Bad", RuleGroup(L.AND, ())),
    StrategyDefinition("Bad", RuleGroup(L.AND, (condition("rsi14", compare_to="unknown"),))),
])
def test_invalid_strategy_rejected(bad):
    with pytest.raises(ValueError):
        evaluate_strategy(bad, {"rsi14": 60})
