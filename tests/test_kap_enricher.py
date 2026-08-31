"""Tests for KAP scan result enrichment."""

from datetime import datetime

from bist_radar.kap.enricher import KapEnricher
from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider
from bist_radar.kap.service import KapService
from bist_radar.models.scan_result import ScanResult


class FakeKapProvider(KapProvider):
    """Fake KAP provider for enrichment tests."""

    def __init__(
        self,
        disclosures_by_symbol: dict[str, list[KapDisclosure]],
    ) -> None:
        self.disclosures_by_symbol = disclosures_by_symbol

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        return self.disclosures_by_symbol.get(
            symbol,
            [],
        )


def make_scan_result(
    symbol: str = "ASELS",
) -> ScanResult:
    """Create a basic scan result."""

    return ScanResult(
        symbol=symbol,
        above_sma20=True,
        rsi_above_50=True,
        macd_bullish=True,
    )


def test_enrich_returns_none_when_no_disclosures():
    """Result should show no KAP news when nothing is returned."""

    provider = FakeKapProvider(
        disclosures_by_symbol={
            "ASELS": [],
        }
    )

    enricher = KapEnricher(
        service=KapService(provider),
    )

    result = enricher.enrich(
        result=make_scan_result(),
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert result.kap_has_news is False
    assert result.kap_importance == "NONE"
    assert result.kap_title == ""


def test_enrich_uses_latest_disclosure_when_no_high():
    """Latest disclosure should be used when no HIGH item exists."""

    provider = FakeKapProvider(
        disclosures_by_symbol={
            "ASELS": [
                KapDisclosure(
                    disclosure_id="1",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 10, 0),
                    title="Yatırım Hakkında",
                    summary="Yeni yatırım planlanmaktadır.",
                ),
                KapDisclosure(
                    disclosure_id="2",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 12, 0),
                    title="Özel Durum Açıklaması",
                    summary="Genel bilgilendirme yapılmıştır.",
                    url="https://www.kap.org.tr/tr/Bildirim/123456",
                ),
            ],
        }
    )

    enricher = KapEnricher(
        service=KapService(provider),
    )

    result = enricher.enrich(
        result=make_scan_result(),
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert result.kap_has_news is True
    assert result.kap_importance == "LOW"
    assert result.kap_title == "Genel bilgilendirme yapılmıştır."
    assert (result.kap_url== "https://www.kap.org.tr/tr/Bildirim/123456")


def test_enrich_prefers_latest_high_disclosure():
    """Latest HIGH disclosure should be preferred."""

    provider = FakeKapProvider(
        disclosures_by_symbol={
            "ASELS": [
                KapDisclosure(
                    disclosure_id="1",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 9, 0),
                    title="Yeni İş İlişkisi",
                    summary="Şirket yeni bir sözleşme imzaladı.",
                ),
                KapDisclosure(
                    disclosure_id="2",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 11, 0),
                    title="Yatırım Hakkında",
                    summary="Yeni yatırım planlanmaktadır.",
                ),
                KapDisclosure(
                    disclosure_id="3",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 13, 0),
                    title="Sözleşme Güncellemesi",
                    summary="Yeni sözleşme hakkında açıklama.",
                ),
            ],
        }
    )

    enricher = KapEnricher(
        service=KapService(provider),
    )

    result = enricher.enrich(
        result=make_scan_result(),
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert result.kap_has_news is True
    assert result.kap_importance == "HIGH"
    assert result.kap_title == "Sözleşme Güncellemesi"


def test_enrich_all_enriches_multiple_results():
    """Multiple scan results should be enriched by symbol."""

    provider = FakeKapProvider(
        disclosures_by_symbol={
            "ASELS": [
                KapDisclosure(
                    disclosure_id="1",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 10, 0),
                    title="Yeni İş İlişkisi",
                    summary="Şirket yeni bir sözleşme imzaladı.",
                ),
            ],
            "KRDMD": [],
        }
    )

    enricher = KapEnricher(
        service=KapService(provider),
    )

    results = [
        make_scan_result("ASELS"),
        make_scan_result("KRDMD"),
    ]

    enriched = enricher.enrich_all(
        results=results,
        start=datetime(2026, 8, 26),
        end=datetime(2026, 8, 27, 23, 59),
    )

    assert len(enriched) == 2

    assert enriched[0].symbol == "ASELS"
    assert enriched[0].kap_has_news is True
    assert enriched[0].kap_importance == "HIGH"

    assert enriched[1].symbol == "KRDMD"
    assert enriched[1].kap_has_news is False
    assert enriched[1].kap_importance == "NONE"