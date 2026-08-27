"""Tests for KAP provider interface."""

from datetime import datetime

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class FakeKapProvider(KapProvider):
    """Fake KAP provider for tests."""

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        return [
            KapDisclosure(
                disclosure_id="12345",
                symbol=symbol,
                published_at=datetime(2026, 8, 27, 10, 30),
                title="Yeni İş İlişkisi",
                summary="Şirket yeni bir sözleşme imzaladı.",
                url="https://example.com/kap/12345",
            )
        ]


def test_fake_kap_provider_returns_disclosures():
    """Fake provider should return KAP disclosures."""

    provider = FakeKapProvider()

    result = provider.get_disclosures(
        symbol="KRDMD",
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert len(result) == 1

    disclosure = result[0]

    assert disclosure.disclosure_id == "12345"
    assert disclosure.symbol == "KRDMD"
    assert disclosure.title == "Yeni İş İlişkisi"
    assert disclosure.summary == "Şirket yeni bir sözleşme imzaladı."