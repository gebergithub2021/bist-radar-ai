from abc import ABC

from bist_radar.universe.provider import UniverseProvider


def test_universe_provider_is_abstract() -> None:
    assert issubclass(UniverseProvider, ABC)