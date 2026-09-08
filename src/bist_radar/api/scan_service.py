"""Shared scan orchestration service."""

from datetime import date, datetime, timedelta

from bist_radar.kap.enricher import KapEnricher
from bist_radar.models.scan_result import ScanResult
from bist_radar.scanner.engine import ScannerEngine


def build_scan_results(
    engine: ScannerEngine,
    kap_enricher: KapEnricher | None,
    symbols: list[str],
) -> list[ScanResult]:
    """Build scan results for API endpoints."""

    end = date.today()
    start = end - timedelta(days=365)

    results = engine.get_ranked_scan_results(
        symbols=symbols,
        start=start,
        end=end,
    )

    if kap_enricher is None:
        return results

    kap_start_date = end - timedelta(days=30)

    kap_start = datetime.combine(
        kap_start_date,
        datetime.min.time(),
    )

    kap_end = datetime.combine(
        end,
        datetime.max.time(),
    )

    try:
        return kap_enricher.enrich_all(
            results=results,
            start=kap_start,
            end=kap_end,
        )
    except RuntimeError:
        for result in results:
            result.kap_has_news = False
            result.kap_importance = "UNAVAILABLE"
            result.kap_title = "KAP service unavailable"
            result.kap_reason = "service error"
            result.kap_url = ""

        return results