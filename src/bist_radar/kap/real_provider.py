"""Official KAP REST API provider."""

from datetime import datetime

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class RealKapProvider(KapProvider):
    """Provider for the official KAP Data Distribution Service."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key cannot be empty.")

        if not base_url.strip():
            raise ValueError("base_url cannot be empty.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """
        Fetch disclosures from the official KAP REST API.

        HTTP integration will be implemented after the official
        subscriber documentation and credentials are available.
        """

        raise NotImplementedError(
            "Official KAP API subscriber credentials and "
            "endpoint documentation are required."
        )