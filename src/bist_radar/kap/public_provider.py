"""Public KAP website provider.

This provider uses KAP's public website endpoints.

It is intended for development and low-volume usage only.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import requests

from bist_radar.kap.models import KapDisclosure
from bist_radar.kap.provider import KapProvider


class PublicKapProvider(KapProvider):
    """Read disclosures from KAP's public website."""

    def __init__(
        self,
        base_url: str = "https://www.kap.org.tr",
        timeout: float = 10.0,
        cache_dir: str = ".cache/kap",
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url cannot be empty.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._cache: dict[
            tuple[str, str],
            list[dict],
        ] = {}

    def _fetch_raw_disclosures_for_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        """Fetch raw disclosures for a single date range."""

        url = (
            f"{self.base_url}"
            "/tr/api/disclosure/members/byCriteria"
        )

        payload = {
            "fromDate": start.strftime("%Y-%m-%d"),
            "toDate": end.strftime("%Y-%m-%d"),
            "mkkMemberOidList": [],
            "subjectList": [],
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": (
                f"{self.base_url}/tr/bildirim-sorgu"
            ),
            "User-Agent": "BistRadarAI/0.1",
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        if response.status_code == 429:
            raise RuntimeError(
                "KAP public endpoint rate limit exceeded."
            )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise ValueError(
                "Unexpected KAP response format."
            )

        return data

    def _build_cache_path(
        self,
        start: datetime,
        end: datetime,
    ) -> Path:
        """Build disk-cache path for the requested range."""

        start_text = start.strftime("%Y-%m-%d")
        end_text = end.strftime("%Y-%m-%d")

        filename = (
            f"disclosures_"
            f"{start_text}_"
            f"{end_text}.json"
        )

        return self.cache_dir / filename

    def _load_disk_cache(
        self,
        start: datetime,
        end: datetime,
    ) -> list[dict] | None:
        """Load cached disclosures from disk if available."""

        cache_path = self._build_cache_path(
            start=start,
            end=end,
        )

        if not cache_path.exists():
            return None

        try:
            content = cache_path.read_text(
                encoding="utf-8",
            )

            data = json.loads(content)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return None

        if not isinstance(data, list):
            return None

        return data

    def _save_disk_cache(
        self,
        start: datetime,
        end: datetime,
        data: list[dict],
    ) -> None:
        """Save disclosures to disk cache."""

        cache_path = self._build_cache_path(
            start=start,
            end=end,
        )

        content = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )

        cache_path.write_text(
            content,
            encoding="utf-8",
        )

    def _fetch_raw_disclosures(
        self,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        """Fetch disclosures using memory and disk cache."""

        cache_key = (
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
        )

        if cache_key in self._cache:
            return self._cache[cache_key]

        disk_data = self._load_disk_cache(
            start=start,
            end=end,
        )

        if disk_data is not None:
            self._cache[cache_key] = disk_data

            return disk_data

        all_disclosures: list[dict] = []

        current = start

        while current.date() <= end.date():
            chunk_start = datetime.combine(
                current.date(),
                datetime.min.time(),
            )

            chunk_end_date = min(
                current.date() + timedelta(days=6),
                end.date(),
            )

            chunk_end = datetime.combine(
                chunk_end_date,
                datetime.max.time(),
            )

            chunk = (
                self._fetch_raw_disclosures_for_range(
                    start=chunk_start,
                    end=chunk_end,
                )
            )

            all_disclosures.extend(
                chunk
            )

            current = datetime.combine(
                chunk_end_date
                + timedelta(days=1),
                datetime.min.time(),
            )

        self._cache[cache_key] = (
            all_disclosures
        )

        self._save_disk_cache(
            start=start,
            end=end,
            data=all_disclosures,
        )

        return all_disclosures

    def get_disclosures(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> list[KapDisclosure]:
        """Return disclosures matching the requested stock symbol."""

        raw_disclosures = (
            self._fetch_raw_disclosures(
                start=start,
                end=end,
            )
        )

        symbol = symbol.upper()

        results: list[KapDisclosure] = []

        for item in raw_disclosures:
            stock_codes = item.get(
                "stockCodes"
            )

            if not stock_codes:
                continue

            codes = {
                code.strip().upper()
                for code in stock_codes.split(",")
                if code.strip()
            }

            if symbol not in codes:
                continue

            publish_date = item.get(
                "publishDate"
            )

            disclosure_index = item.get(
                "disclosureIndex"
            )

            if (
                not publish_date
                or disclosure_index is None
            ):
                continue

            try:
                published_at = datetime.strptime(
                    publish_date,
                    "%d.%m.%Y %H:%M:%S",
                )

            except ValueError:
                continue

            disclosure_id = str(
                disclosure_index
            )

            url = (
                f"{self.base_url}"
                f"/tr/Bildirim/"
                f"{disclosure_id}"
            )

            disclosure = KapDisclosure(
                disclosure_id=disclosure_id,
                symbol=symbol,
                published_at=published_at,
                title=item.get("subject") or "",
                summary=item.get("summary") or "",
                url=url,
            )

            results.append(
                disclosure
            )

        return results