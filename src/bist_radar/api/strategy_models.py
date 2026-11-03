
"""API request models for user-defined strategies."""

from __future__ import annotations

from typing import Annotated, Union

from pydantic import BaseModel, Field

from bist_radar.strategies.models import (
    ComparisonOperator,
    LogicOperator,
)


class ConditionRequest(BaseModel):
    metric: str
    operator: ComparisonOperator
    value: float | None = None
    compare_to: str | None = None


class RuleGroupRequest(BaseModel):
    operator: LogicOperator
    children: list["RuleRequest"]


RuleRequest = Annotated[
    Union[ConditionRequest, RuleGroupRequest],
    Field(union_mode="left_to_right"),
]


class StrategyRequest(BaseModel):
    name: str
    rules: RuleGroupRequest
    universe: str = "BIST100"


RuleGroupRequest.model_rebuild()


from bist_radar.strategies.models import (
    Condition,
    RuleGroup,
    StrategyDefinition,
)


def to_strategy_definition(
    request: StrategyRequest,
) -> StrategyDefinition:
    """Convert an API request into a strategy definition."""

    def convert_rule(
        rule: ConditionRequest | RuleGroupRequest,
    ) -> Condition | RuleGroup:
        if isinstance(rule, ConditionRequest):
            return Condition(
                metric=rule.metric,
                operator=rule.operator,
                value=rule.value,
                compare_to=rule.compare_to,
            )

        return RuleGroup(
            operator=rule.operator,
            children=tuple(
                convert_rule(child)
                for child in rule.children
            ),
        )

    return StrategyDefinition(
        name=request.name,
        universe=request.universe,
        rules=convert_rule(request.rules),
    )

