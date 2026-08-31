"""Inspect raw KAP response for selected symbols."""

from datetime import datetime

from bist_radar.kap.public_provider import PublicKapProvider


provider = PublicKapProvider(timeout=15.0)

start = datetime(2026, 7, 28)
end = datetime(2026, 8, 27)

symbols = [
    "ASELS",
    "TUPRS",
    "KRDMD",
    "THYAO",
    "EREGL",
]

print("Ham KAP verisi çekiliyor...")

raw = provider._fetch_raw_disclosures(
    start=start,
    end=end,
)

print(f"Toplam ham kayıt: {len(raw)}")
print()

for symbol in symbols:
    print("=" * 70)
    print(symbol)

    matches = []

    for item in raw:
        stock_codes = str(
            item.get("stockCodes") or ""
        ).upper()

        kap_title = str(
            item.get("kapTitle") or ""
        ).upper()

        subject = str(
            item.get("subject") or ""
        ).upper()

        if (
            symbol in stock_codes
            or symbol in kap_title
            or symbol in subject
        ):
            matches.append(item)

    print(f"Eşleşen ham kayıt: {len(matches)}")

    for item in matches[:5]:
        print()
        print(
            "publishDate :",
            item.get("publishDate"),
        )
        print(
            "stockCodes  :",
            repr(item.get("stockCodes")),
        )
        print(
            "kapTitle    :",
            item.get("kapTitle"),
        )
        print(
            "subject     :",
            item.get("subject"),
        )
        print(
            "summary     :",
            item.get("summary"),
        )

print()
print("=" * 70)

dates = [
    item.get("publishDate")
    for item in raw
    if item.get("publishDate")
]

print("İlk kayıt tarihi :", dates[0] if dates else None)
print("Son kayıt tarihi :", dates[-1] if dates else None)