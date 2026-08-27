"""Tests for development KAP provider."""

from datetime import datetime

from bist_radar.kap.fake_provider import FakeKapProvider


def test_fake_kap_provider_returns_symbol_disclosures():
    provider = FakeKapProvider()

    result = provider.get_disclosures(
        symbol="ASELS",
        start=datetime(2026, 8, 27),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert len(result) == 1
    assert result[0].symbol == "ASELS"
    assert result[0].title == "Yeni İş İlişkisi"


def test_fake_kap_provider_returns_empty_for_symbol_without_news():
    provider = FakeKapProvider()

    result = provider.get_disclosures(
        symbol="KRDMD",
        start=datetime(2026, 8, 27),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert result == []


def test_fake_kap_provider_respects_date_range():
    provider = FakeKapProvider()

    result = provider.get_disclosures(
        symbol="ASELS",
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 26, 23, 59),
    )

    assert result == []