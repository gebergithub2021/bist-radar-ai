"""KAP enrichment for scan results."""

from datetime import datetime

from bist_radar.kap.classifier import classify_disclosure
from bist_radar.kap.service import KapService
from bist_radar.models.scan_result import ScanResult


class KapEnricher:
    """Attach KAP disclosure context to scan results."""

    def __init__(
        self,
        service: KapService,
    ) -> None:
        self.service = service

    def enrich(
        self,
        result: ScanResult,
        start: datetime,
        end: datetime,
    ) -> ScanResult:
        """Attach latest important KAP information to a scan result."""

        disclosures = self.service.get_disclosures(
            symbol=result.symbol,
            start=start,
            end=end,
        )

        if not disclosures:
            result.kap_has_news = False
            result.kap_importance = "NONE"
            result.kap_title = ""
            return result

        disclosures = sorted(
            disclosures,
            key=lambda item: item.published_at,
            reverse=True,
        )

        important = [
            disclosure
            for disclosure in disclosures
            if classify_disclosure(disclosure) == "HIGH"
        ]

        if important:
            latest = important[0]

            result.kap_has_news = True
            result.kap_importance = "HIGH"
            result.kap_title = latest.title
            return result

        latest = disclosures[0]

        result.kap_has_news = True
        result.kap_importance = classify_disclosure(latest)
        result.kap_title = latest.title

        return result
    
    def enrich_all(
    self,
    results: list[ScanResult],
    start: datetime,
    end: datetime,
    ) -> list[ScanResult]:
        """Attach KAP context to multiple scan results."""

        return [
        self.enrich(
            result=result,
            start=start,
            end=end,
        )
        for result in results
    ]