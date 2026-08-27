"""KAP disclosure service."""

from datetime import datetime

from bist_radar.kap.classifier import classify_disclosure
from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class KapService:
    """Service for evaluating KAP disclosures."""

    def __init__(
        self,
        provider: KapProvider,
    ) -> None:
        self.provider = provider

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """Return disclosures for a symbol."""

        return self.provider.get_disclosures(
            symbol=symbol,
            start=start,
            end=end,
        )

    def get_important_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """Return HIGH importance disclosures."""

        disclosures = self.get_disclosures(
            symbol=symbol,
            start=start,
            end=end,
        )

        return [
            disclosure
            for disclosure in disclosures
            if classify_disclosure(disclosure) == "HIGH"
        ]

    def has_important_disclosure(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> bool:
        """Return whether symbol has a HIGH importance disclosure."""

        return bool(
            self.get_important_disclosures(
                symbol=symbol,
                start=start,
                end=end,
            )
        )