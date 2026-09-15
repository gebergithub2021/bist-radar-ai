"""BIST 100 stock universe."""

from bist_radar.universe.borsa_istanbul_provider import (
    BorsaIstanbulUniverseProvider,
)
from bist_radar.universe.provider import UniverseProvider


class Bist100Universe(UniverseProvider):
    """Provide symbols belonging to the BIST 100 universe."""

    def __init__(
        self,
        provider: UniverseProvider | None = None,
    ) -> None:
        if provider is None:
            provider = BorsaIstanbulUniverseProvider()

        self.provider = provider

    def get_symbols(self) -> list[str]:
        """Return BIST 100 stock symbols."""

        return self.provider.get_symbols()