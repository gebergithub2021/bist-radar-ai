"""BIST 100 scan service."""

from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

from bist_radar.api.scan_service import build_scan_results
from bist_radar.ranking import select_candidates_by_score
from bist_radar.universe.bist100 import Bist100Universe
from bist_radar.universe.provider import UniverseProvider
from bist_radar.fundamentals.analysis import (
    analyze_fundamentals,
)
from bist_radar.models.candidate_analysis import (
    CandidateAnalysis,
)


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
    """Return technical candidates and enrich only them with KAP."""

    results = build_bist100_scan_results(
        engine=engine,
        kap_enricher=None,
        universe=universe,
        scan_builder=scan_builder,
    )

    candidates = select_candidates_by_score(
        results,
        minimum_score=minimum_score,
    )

    if kap_enricher is None or not candidates:
        return candidates

    end = date.today()
    start = end - timedelta(days=30)

    kap_start = datetime.combine(
        start,
        datetime.min.time(),
    )
    kap_end = datetime.combine(
        end,
        datetime.max.time(),
    )

    try:
        return kap_enricher.enrich_all(
            results=candidates,
            start=kap_start,
            end=kap_end,
        )
    except RuntimeError:
        for result in candidates:
            result.kap_has_news = False
            result.kap_importance = "UNAVAILABLE"
            result.kap_title = "KAP service unavailable"
            result.kap_reason = "service error"
            result.kap_url = ""

        return candidates

def build_bist100_candidate_analysis(
    engine: Any,
    kap_enricher: Any,
    fundamental_provider: Any,
    universe: UniverseProvider | None = None,
    scan_builder: ScanBuilder = build_scan_results,
    minimum_score: int = 85,
) -> list[CandidateAnalysis]:
    """Build fundamental analysis for technical candidates only."""

    candidates = build_bist100_candidates(
        engine=engine,
        kap_enricher=kap_enricher,
        universe=universe,
        scan_builder=scan_builder,
        minimum_score=minimum_score,
    )

    results: list[CandidateAnalysis] = []

    for candidate in candidates:
        try:
            snapshot = fundamental_provider.get_snapshot(
            symbol=candidate.symbol,
            )

            fundamental = analyze_fundamentals(
            snapshot,
        )
        except RuntimeError:
            continue

        results.append(
            CandidateAnalysis(
            technical=candidate,
            fundamental=fundamental,
        )
    )

    return results