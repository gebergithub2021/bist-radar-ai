"""Rule-based KAP disclosure importance classifier."""

import unicodedata

from bist_radar.kap.models import KapDisclosure


HIGH_KEYWORDS = (
    "yeni iş ilişkisi",
    "iş ilişkisi",
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
    "kâr payı",
    "finansal sonuç",
    "finansal sonuçlar",
    "finansal tabloların açıklanması",
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
    "kredi derecelendirmesi",
)

LOW_TITLE_KEYWORDS = (
    "kurumsal yönetim ilkelerine uyum derecelendirmesi",
    "kurumsal yönetim uyum raporu",
    "şirket genel bilgi formu",
    "sorumluluk beyanı",
    "katılım finans ilkeleri",
    "faaliyet raporu",
)

LOW_KEYWORDS = (
    "özel durum açıklaması",
    "kurumsal yönetim",
    "uyum derecelendirmesi",
    "sorumluluk beyanı",
    "şirket genel bilgi formu",
    "katılım finans",
    "faaliyet raporu",
)


def normalize_text(
    text: str,
) -> str:
    """Normalize Turkish/Unicode text for reliable matching."""

    text = text.casefold()

    # Turkish dotless i
    text = text.replace(
        "ı",
        "i",
    )

    # Split accented characters into base character + mark.
    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    # Remove combining marks.
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    return text


def contains_keyword(
    text: str,
    keyword: str,
) -> bool:
    """Return whether normalized keyword exists in normalized text."""

    return (
        normalize_text(keyword)
        in normalize_text(text)
    )


def classify_disclosure_with_reason(
    disclosure: KapDisclosure,
) -> tuple[str, str]:
    """Classify disclosure and return matched rule."""

    title = (
        disclosure.title
        or ""
    ).strip()

    summary = (
        disclosure.summary
        or ""
    ).strip()

    combined_text = (
        f"{title} {summary}"
    )

    # -------------------------------------------------
    # Routine title overrides
    # -------------------------------------------------

    for keyword in LOW_TITLE_KEYWORDS:
        if contains_keyword(
            title,
            keyword,
        ):
            return (
                "LOW",
                f"title override: {keyword}",
            )

    # -------------------------------------------------
    # High-impact keywords
    # -------------------------------------------------

    for keyword in HIGH_KEYWORDS:
        if contains_keyword(
            combined_text,
            keyword,
        ):
            return (
                "HIGH",
                keyword,
            )

    # -------------------------------------------------
    # Medium-impact keywords
    # -------------------------------------------------

    for keyword in MEDIUM_KEYWORDS:
        if contains_keyword(
            combined_text,
            keyword,
        ):
            return (
                "MEDIUM",
                keyword,
            )

    # -------------------------------------------------
    # Low-impact/general keywords
    # -------------------------------------------------

    for keyword in LOW_KEYWORDS:
        if contains_keyword(
            combined_text,
            keyword,
        ):
            return (
                "LOW",
                keyword,
            )

    return (
        "LOW",
        "no keyword matched",
    )


def classify_disclosure(
    disclosure: KapDisclosure,
) -> str:
    """Classify a KAP disclosure as HIGH, MEDIUM or LOW."""

    importance, _reason = (
        classify_disclosure_with_reason(
            disclosure
        )
    )

    return importance