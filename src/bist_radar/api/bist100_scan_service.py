"""BIST 100 scan service."""

from collections.abc import Callable
from typing import Any

from bist_radar.api.scan_service import build_scan_results
from bist_radar.ranking import select_candidates_by_score
from bist_radar.universe.bist100 import Bist100Universe
from bist_radar.universe.provider import UniverseProvider


ScanBuilder = Callable[..., list]


def build_bist100_scan_results(
    engine: Any,
    kap_enricher: Any,
    universe: UniverseProvider | None = None,
    scan_builder: ScanBuilder = build_scan_results,
) -> list:
    """Scan all symbols in the BIST 100 universe."""

    if universe is None:
        universe = Bist100Universe()

    symbols = universe.get_symbols()

    return scan_builder(
        engine=engine,
        kap_enricher=kap_enricher,
        symbols=symbols,
    )


def build_bist100_candidates(
    engine: Any,
    kap_enricher: Any,
    universe: UniverseProvider | None = None,
    scan_builder: ScanBuilder = build_scan_results,
    minimum_score: int = 85,
) -> list:
    """Return BIST 100 candidates meeting the technical score threshold."""

    results = build_bist100_scan_results(
        engine=engine,
        kap_enricher=kap_enricher,
        universe=universe,
        scan_builder=scan_builder,
    )

    return select_candidates_by_score(
        results,
        minimum_score=minimum_score,
    )