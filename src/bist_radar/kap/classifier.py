"""KAP disclosure classifier."""

from bist_radar.kap.models import KapDisclosure


HIGH_KEYWORDS = (
    "yeni iş ilişkisi",
    "sözleşme",
    "ihale",
    "sermaye artırımı",
    "sermaye azaltımı",
    "birleşme",
    "devralma",
    "satın alma",
    "ortaklık",
    "temettü",
    "kar payı",
    "finansal sonuç",
    "dava",
    "ceza",
)

MEDIUM_KEYWORDS = (
    "yatırım",
    "geri alım",
    "pay geri alım",
    "yönetim kurulu",
    "genel kurul",
    "kredi",
    "borçlanma",
)


def classify_disclosure(
    disclosure: KapDisclosure,
) -> str:
    """Classify KAP disclosure importance."""

    text = (
        f"{disclosure.title} "
        f"{disclosure.summary}"
    ).lower()

    if any(
        keyword in text
        for keyword in HIGH_KEYWORDS
    ):
        return "HIGH"

    if any(
        keyword in text
        for keyword in MEDIUM_KEYWORDS
    ):
        return "MEDIUM"

    return "LOW"