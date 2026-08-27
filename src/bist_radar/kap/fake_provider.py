"""Fake KAP provider for development."""

from datetime import datetime

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class FakeKapProvider(KapProvider):
    """Provide sample KAP disclosures during development."""

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:

        disclosures = {
            "ASELS": [
                KapDisclosure(
                    disclosure_id="dev-1",
                    symbol="ASELS",
                    published_at=datetime(2026, 8, 27, 10, 30),
                    title="Yeni İş İlişkisi",
                    summary=(
                        "Şirket yeni bir sözleşme "
                        "imzaladığını açıkladı."
                    ),
                ),
            ],
            "TUPRS": [
                KapDisclosure(
                    disclosure_id="dev-2",
                    symbol="TUPRS",
                    published_at=datetime(2026, 8, 27, 11, 0),
                    title="Yatırım Hakkında",
                    summary=(
                        "Şirket yeni yatırım planı "
                        "hakkında bilgi verdi."
                    ),
                ),
            ],
        }

        return [
            disclosure
            for disclosure in disclosures.get(symbol, [])
            if start <= disclosure.published_at <= end
        ]