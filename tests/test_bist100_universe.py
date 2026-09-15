from bist_radar.universe.bist100 import Bist100Universe
from bist_radar.universe.provider import UniverseProvider


class FakeUniverseProvider(UniverseProvider):
    """Fake universe provider for tests."""

    def get_symbols(self) -> list[str]:
        return [
            "ASELS",
            "THYAO",
            "TUPRS",
        ]


def test_bist100_universe_is_universe_provider() -> None:
    universe = Bist100Universe()

    assert isinstance(universe, UniverseProvider)


def test_bist100_universe_uses_provider() -> None:
    provider = FakeUniverseProvider()

    universe = Bist100Universe(
        provider=provider,
    )

    symbols = universe.get_symbols()

    assert symbols == [
        "ASELS",
        "THYAO",
        "TUPRS",
    ]
    
def test_bist100_universe_uses_default_provider() -> None:
    universe = Bist100Universe()

    symbols = universe.get_symbols()

    assert len(symbols) == 100
    assert len(set(symbols)) == 100

    assert "ASELS" in symbols
    assert "THYAO" in symbols
    assert "TUPRS" in symbols