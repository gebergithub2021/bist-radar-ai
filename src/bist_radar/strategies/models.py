"""Typed strategy rule definitions and evaluation outcomes."""
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


class MatchStatus(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"


class LogicOperator(str, Enum):
    AND = "AND"
    OR = "OR"


class ComparisonOperator(str, Enum):
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    EQ = "EQ"
    NE = "NE"


@dataclass(frozen=True)
class Condition:
    metric: str
    operator: ComparisonOperator
    value: float | None = None
    compare_to: str | None = None


@dataclass(frozen=True)
class RuleGroup:
    operator: LogicOperator
    children: tuple["Rule", ...]


Rule: TypeAlias = Condition | RuleGroup


@dataclass(frozen=True)
class StrategyDefinition:
    name: str
    rules: RuleGroup
    universe: str = "BIST100"


@dataclass(frozen=True)
class ConditionResult:
    condition: Condition
    status: MatchStatus
    actual: float | None
    expected: float | None


@dataclass(frozen=True)
class StrategyResult:
    status: MatchStatus
    conditions: tuple[ConditionResult, ...]
