"""BIST 100 stock universe."""

from bist_radar.universe.provider import UniverseProvider


class Bist100Universe(UniverseProvider):
    """Provide symbols belonging to the BIST 100 universe."""

    def __init__(
        self,
        provider: UniverseProvider | None = None,
    ) -> None:
        self.provider = provider

    def get_symbols(self) -> list[str]:
        """Return BIST 100 stock symbols."""

        if self.provider is None:
            return []

        return self.provider.get_symbols()