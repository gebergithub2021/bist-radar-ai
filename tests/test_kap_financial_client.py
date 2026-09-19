from bist_radar.fundamentals.kap_financial_client import (
    KapFinancialClient,
)


def test_kap_financial_client_can_be_created() -> None:
    client = KapFinancialClient()

    assert client is not None

import pytest


def test_kap_financial_client_fetch_report_requires_transport() -> None:
    client = KapFinancialClient()

    with pytest.raises(
        RuntimeError,
        match="KAP financial transport is not configured",
    ):
        client.fetch_report("ASELS")

def test_kap_financial_client_uses_transport() -> None:
    class FakeTransport:
        def fetch_report(
            self,
            symbol: str,
        ) -> dict:
            assert symbol == "ASELS"

            return {
                "scale_text": "1000 TL",
                "period_end": "2026-06-30",
                "previous_period_end": "2025-06-30",
                "rows": {},
            }

    client = KapFinancialClient(
        transport=FakeTransport(),
    )

    report = client.fetch_report("ASELS")

    assert report["scale_text"] == "1000 TL"
    assert report["period_end"] == "2026-06-30"
    assert report["previous_period_end"] == "2025-06-30"
    assert report["rows"] == {}