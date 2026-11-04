
"""Tests for user strategy API endpoints."""

from fastapi.testclient import TestClient

from bist_radar.api.app import app
from bist_radar.strategies.strategy_scan_service import StrategyScanReport


client = TestClient(app)


def test_strategy_metrics_endpoint():
    response = client.get("/strategies/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "technical" in data
    assert "fundamental" in data

    assert "rsi14" in data["technical"]
    assert "macd" in data["technical"]
    assert "sma20" in data["technical"]

    assert "ema20" not in data["technical"]
    assert data["fundamental"] == []

    assert len(data["technical"]) == 14

def test_validate_strategy_accepts_valid_rules():
    payload = {
        "name": "RSI ve MACD Stratejisi",
        "universe": "BIST100",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "rsi14",
                    "operator": "GT",
                    "value": 55,
                },
                {
                    "metric": "macd",
                    "operator": "GT",
                    "compare_to": "signal",
                },
            ],
        },
    }

    response = client.post(
        "/strategies/validate",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "name": "RSI ve MACD Stratejisi",
        "universe": "BIST100",
    }


def test_validate_strategy_rejects_unknown_metric():
    payload = {
        "name": "Geçersiz Strateji",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "unknown_indicator",
                    "operator": "GT",
                    "value": 50,
                },
            ],
        },
    }

    response = client.post(
        "/strategies/validate",
        json=payload,
    )

    assert response.status_code == 422
    assert "Unsupported metric" in response.json()["detail"]

import pytest

from bist_radar.api.strategy_models import (
    StrategyRequest,
    to_strategy_definition,
)
from bist_radar.strategies.validator import (
    validate_scannable_strategy,
)


def test_scannable_strategy_accepts_supported_metric():
    payload = {
        "name": "RSI Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "rsi14",
                    "operator": "GT",
                    "value": 55,
                },
            ],
        },
    }

    request = StrategyRequest.model_validate(payload)
    strategy = to_strategy_definition(request)

    validate_scannable_strategy(strategy)


def test_scannable_strategy_rejects_unavailable_metric():
    payload = {
        "name": "EMA Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "ema20",
                    "operator": "GT",
                    "value": 50,
                },
            ],
        },
    }

    request = StrategyRequest.model_validate(payload)
    strategy = to_strategy_definition(request)

    with pytest.raises(
        ValueError,
        match="Metric not available for scanning",
    ):
        validate_scannable_strategy(strategy)

from unittest.mock import patch

from bist_radar.strategies.models import (
    MatchStatus,
    StrategyResult,
)
from bist_radar.strategies.strategy_scan_service import (
    StockStrategyResult,
)


def test_strategy_scan_endpoint_returns_matches():
    payload = {
        "name": "RSI Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "rsi14",
                    "operator": "GT",
                    "value": 55,
                },
            ],
        },
    }

    fake_matches = [
        StockStrategyResult(
            symbol="THYAO",
            evaluation=StrategyResult(
                status=MatchStatus.MATCH,
                conditions=(),
            ),
        ),
    ]

    with patch(
        "bist_radar.api.app.scan_bist100_with_strategy_report",
        return_value=StrategyScanReport(
        matches=tuple(fake_matches),
        unknown=(),
        ),
    ) as mock_scan:
        response = client.post(
            "/strategies/scans",
            json=payload,
        )

    assert response.status_code == 200
    assert response.json() == {
        "strategy": "RSI Stratejisi",
        "universe": "BIST100",
        "count": 1,
        "results": [
            {
                "symbol": "THYAO",
                "status": "MATCH",
                "conditions": [],
            },
        ],
        "unknown_count": 0,
        "unknown_results": [],
    }

    mock_scan.assert_called_once()

def test_strategy_scan_rejects_unavailable_metric():
    payload = {
        "name": "EMA Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "ema20",
                    "operator": "GT",
                    "value": 50,
                },
            ],
        },
    }

    with patch(
        "bist_radar.api.app.scan_bist100_with_strategy_report"
    ) as mock_scan:
        response = client.post(
            "/strategies/scans",
            json=payload,
        )

    assert response.status_code == 422
    assert (
        "Metric not available for scanning"
        in response.json()["detail"]
    )

    mock_scan.assert_not_called()


from bist_radar.strategies.models import (
    ComparisonOperator,
    Condition,
    ConditionResult,
)


def test_strategy_scan_returns_condition_details():
    payload = {
        "name": "RSI Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "rsi14",
                    "operator": "GT",
                    "value": 55,
                },
            ],
        },
    }

    fake_matches = [
        StockStrategyResult(
            symbol="THYAO",
            evaluation=StrategyResult(
                status=MatchStatus.MATCH,
                conditions=(
                    ConditionResult(
                        condition=Condition(
                            metric="rsi14",
                            operator=ComparisonOperator.GT,
                            value=55,
                        ),
                        status=MatchStatus.MATCH,
                        actual=62.0,
                        expected=55.0,
                    ),
                ),
            ),
        ),
    ]

    with patch(
        "bist_radar.api.app.scan_bist100_with_strategy_report",
        return_value=StrategyScanReport(
        matches=tuple(fake_matches),
        unknown=(),
        ),
    ):
        response = client.post(
            "/strategies/scans",
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["results"][0]["symbol"] == "THYAO"

    conditions = data["results"][0]["conditions"]

    assert len(conditions) == 1
    assert conditions[0] == {
        "metric": "rsi14",
        "operator": "GT",
        "value": 55,
        "compare_to": None,
        "actual": 62.0,
        "expected": 55.0,
        "status": "MATCH",
    }

def test_strategy_scan_returns_unknown_results():
    payload = {
        "name": "RSI Stratejisi",
        "rules": {
            "operator": "AND",
            "children": [
                {
                    "metric": "rsi14",
                    "operator": "GT",
                    "value": 55,
                },
            ],
        },
    }

    fake_unknown = StockStrategyResult(
        symbol="TUPRS",
        evaluation=StrategyResult(
            status=MatchStatus.UNKNOWN,
            conditions=(
                ConditionResult(
                    condition=Condition(
                        metric="rsi14",
                        operator=ComparisonOperator.GT,
                        value=55,
                    ),
                    status=MatchStatus.UNKNOWN,
                    actual=None,
                    expected=55.0,
                ),
            ),
        ),
    )

    fake_report = StrategyScanReport(
        matches=(),
        unknown=(fake_unknown,),
    )

    with patch(
        "bist_radar.api.app.scan_bist100_with_strategy_report",
        return_value=fake_report,
    ):
        response = client.post(
            "/strategies/scans",
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["results"] == []
    assert data["unknown_count"] == 1

    unknown_result = data["unknown_results"][0]

    assert unknown_result["symbol"] == "TUPRS"
    assert unknown_result["status"] == "UNKNOWN"

    condition = unknown_result["conditions"][0]

    assert condition["metric"] == "rsi14"
    assert condition["actual"] is None
    assert condition["expected"] == 55.0
    assert condition["status"] == "UNKNOWN"

