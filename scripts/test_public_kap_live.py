"""Live test for PublicKapProvider."""

from datetime import datetime

from bist_radar.kap.classifier import classify_disclosure
from bist_radar.kap.public_provider import PublicKapProvider


provider = PublicKapProvider(
    timeout=15.0,
)

start = datetime(2026, 7, 28)
end = datetime(2026, 8, 27)

symbols = [
    "ASELS",
    "TUPRS",
    "KRDMD",
    "THYAO",
    "EREGL",
]

print("Gerçek KAP bildirimleri")
print("=" * 70)

for symbol in symbols:
    print()
    print(f"{symbol}:")

    try:
        disclosures = provider.get_disclosures(
            symbol=symbol,
            start=start,
            end=end,
        )

        print(
            f"Bulunan bildirim: {len(disclosures)}"
        )

        for disclosure in disclosures:
            importance = classify_disclosure(
                disclosure
            )

            print(
                f"  {disclosure.published_at} "
                f"[{importance}] "
                f"{disclosure.title}"
            )

            if disclosure.summary:
                print(
                    f"    {disclosure.summary}"
                )

    except Exception as exc:
        print(
            f"  HATA: "
            f"{type(exc).__name__}: {exc}"
        )