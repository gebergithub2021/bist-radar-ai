"""Tests for KAP disclosure service."""

from datetime import datetime

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider
from bist_radar.kap.service import KapService


class FakeKapProvider(KapProvider):
    """Fake KAP provider for service tests."""

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        return [
            KapDisclosure(
                disclosure_id="1",
                symbol=symbol,
                published_at=datetime(2026, 8, 27, 10, 0),
                title="Yeni İş İlişkisi",
                summary="Şirket yeni bir sözleşme imzaladı.",
            ),
            KapDisclosure(
                disclosure_id="2",
                symbol=symbol,
                published_at=datetime(2026, 8, 27, 11, 0),
                title="Yatırım Hakkında",
                summary="Yeni üretim hattı yatırımı planlanmaktadır.",
            ),
            KapDisclosure(
                disclosure_id="3",
                symbol=symbol,
                published_at=datetime(2026, 8, 27, 12, 0),
                title="Özel Durum Açıklaması",
                summary="Genel bilgilendirme yapılmıştır.",
            ),
        ]


def test_get_disclosures_returns_all_disclosures():
    """Service should return all disclosures."""

    service = KapService(
        provider=FakeKapProvider(),
    )

    result = service.get_disclosures(
        symbol="ASELS",
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert len(result) == 3


def test_get_important_disclosures_returns_only_high():
    """Service should return only HIGH importance disclosures."""

    service = KapService(
        provider=FakeKapProvider(),
    )

    result = service.get_important_disclosures(
        symbol="ASELS",
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert len(result) == 1
    assert result[0].disclosure_id == "1"
    assert result[0].title == "Yeni İş İlişkisi"


def test_has_important_disclosure_returns_true():
    """Service should detect an important disclosure."""

    service = KapService(
        provider=FakeKapProvider(),
    )

    result = service.has_important_disclosure(
        symbol="ASELS",
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert result is True