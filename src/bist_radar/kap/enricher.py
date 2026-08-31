"""KAP enrichment for scan results."""

from datetime import datetime

from bist_radar.kap.classifier import (
    classify_disclosure,
    classify_disclosure_with_reason,
)
from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.service import KapService
from bist_radar.models.scan_result import ScanResult


GENERIC_TITLES = (
    "özel durum açıklaması (genel)",
    "özel durum açıklaması",
)


class KapEnricher:
    """Attach KAP disclosure context to scan results."""

    def __init__(
        self,
        service: KapService,
    ) -> None:
        self.service = service

    def _get_display_title(
        self,
        disclosure: KapDisclosure,
    ) -> str:
        """Return the most useful text for terminal/report display."""

        title = (
            disclosure.title
            or ""
        ).strip()

        summary = (
            disclosure.summary
            or ""
        ).strip()

        normalized_title = title.lower()

        if (
            normalized_title in GENERIC_TITLES
            and summary
        ):
            return summary

        if title:
            return title

        if summary:
            return summary

        return "KAP bildirimi"

    def enrich(
        self,
        result: ScanResult,
        start: datetime,
        end: datetime,
    ) -> ScanResult:
        """Attach latest relevant KAP information to a scan result."""

        try:
            disclosures = self.service.get_disclosures(
                symbol=result.symbol,
                start=start,
                end=end,
            )

        except RuntimeError as exc:
            if "rate limit" not in str(exc).lower():
                raise

            result.kap_has_news = False
            result.kap_importance = "UNAVAILABLE"
            result.kap_title = "KAP rate limit"
            result.kap_reason = "rate limit"
            result.kap_url = ""

            return result

        if not disclosures:
            result.kap_has_news = False
            result.kap_importance = "NONE"
            result.kap_title = ""
            result.kap_reason = ""
            result.kap_url = ""

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

            importance, reason = (
                classify_disclosure_with_reason(
                    latest
                )
            )

            result.kap_has_news = True
            result.kap_importance = importance
            result.kap_title = self._get_display_title(
                latest
            )
            result.kap_reason = reason
            result.kap_url = latest.url

            return result

        latest = disclosures[0]

        importance, reason = (
            classify_disclosure_with_reason(
                latest
            )
        )

        result.kap_has_news = True
        result.kap_importance = importance
        result.kap_title = self._get_display_title(
            latest
        )
        result.kap_reason = reason
        result.kap_url = latest.url

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