"""KAP data provider interface."""

from abc import ABC, abstractmethod
from datetime import datetime

from bist_radar.kap.models import KapDisclosure


class KapProvider(ABC):
    """Provide KAP disclosures."""

    @abstractmethod
    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """Return disclosures for a symbol."""