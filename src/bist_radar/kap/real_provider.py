"""Real KAP REST API provider."""

from datetime import datetime

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class RealKapProvider(KapProvider):
    """KAP provider backed by the official KAP REST API."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """
        Return disclosures from the official KAP API.

        HTTP integration will be implemented once
        official API credentials and endpoint details
        are configured.
        """

        raise NotImplementedError(
            "Official KAP API credentials are required."
        )