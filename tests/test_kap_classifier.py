"""Tests for KAP disclosure classifier."""

from datetime import datetime

from bist_radar.kap.classifier import classify_disclosure
from bist_radar.kap.models import KapDisclosure


def make_disclosure(
    title: str,
    summary: str = "",
) -> KapDisclosure:
    """Create a KAP disclosure for classifier tests."""

    return KapDisclosure(
        disclosure_id="1",
        symbol="TEST",
        published_at=datetime(2026, 8, 27, 12, 0),
        title=title,
        summary=summary,
    )


def test_classify_disclosure_returns_high():
    disclosure = make_disclosure(
        title="Yeni İş İlişkisi",
        summary="Şirket önemli bir sözleşme imzaladı.",
    )

    assert classify_disclosure(disclosure) == "HIGH"


def test_classify_disclosure_returns_medium():
    disclosure = make_disclosure(
        title="Yatırım Hakkında",
        summary="Yeni üretim hattı yatırımı planlanmaktadır.",
    )

    assert classify_disclosure(disclosure) == "MEDIUM"


def test_classify_disclosure_returns_low():
    disclosure = make_disclosure(
        title="Özel Durum Açıklaması",
        summary="Genel bilgilendirme yapılmıştır.",
    )

    assert classify_disclosure(disclosure) == "LOW"