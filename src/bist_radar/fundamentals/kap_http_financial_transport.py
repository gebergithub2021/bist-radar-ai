"""HTTP transport for KAP financial reports."""
import re

class KapHttpFinancialTransport:
    """HTTP transport for retrieving KAP financial reports."""

    def __init__(
        self,
        session=None,
        member_resolver=None,
    ) -> None:
        self.session = session
        self.member_resolver = member_resolver

    def _resolve_member_id(
        self,
        symbol: str,
    ) -> str:
        """Resolve a stock symbol to its KAP member ID."""

        if self.member_resolver is None:
            raise RuntimeError(
            "KAP member resolver is not configured"
            )

        return self.member_resolver.resolve(
            symbol=symbol,
        )
    
    def _build_disclosure_url(
        self,
        disclosure_id: int,
    ) -> str:
        """Build the public KAP disclosure URL."""

        return (
            "https://www.kap.org.tr/tr/Bildirim/"
            f"{disclosure_id}"
        )

    def _build_financial_search_url(
        self,
        member_id: str,
    ) -> str:
        """Build the KAP financial report search URL."""

        return (
            "https://www.kap.org.tr/tr/bildirim-sorgu-sonuc"
            "?disclosureClass=FR"
            f"&member={member_id}"
        )

    def _find_latest_financial_disclosure_metadata(
        self,
        symbol: str,
    ) -> dict:
        """Find metadata for the latest financial disclosure."""

        if self.session is None:
            raise RuntimeError(
                "KAP HTTP session is not configured"
            )

        member_id = self._resolve_member_id(
            symbol=symbol,
        )

        url = self._build_financial_search_url(
            member_id=member_id,
        )

        response = self.session.get(url)
        response.raise_for_status()

        disclosures = self._extract_financial_disclosures(
            html=response.text,
        )

        return self._select_latest_financial_disclosure_metadata(
            disclosures
        )

    def _find_financial_disclosure_metadata_for_period(
        self,
        symbol: str,
        year: int,
        period: int,
    ) -> dict:
        """Find financial disclosure metadata for a specific period."""

        if self.session is None:
            raise RuntimeError(
            "KAP HTTP session is not configured"
            )

        member_id = self._resolve_member_id(
            symbol=symbol,
        )

        url = self._build_financial_search_url(
            member_id=member_id,
        )

        response = self.session.get(url)
        response.raise_for_status()

        disclosures = self._extract_financial_disclosures(
            html=response.text,
        )

        return self._select_financial_disclosure_metadata_for_period(
            disclosures=disclosures,
            year=year,
            period=period,
        )

    def _find_latest_financial_disclosure(
        self,
        symbol: str,
    ) -> int:
        """Find the latest financial disclosure ID for a symbol."""

        if self.session is None:
            raise RuntimeError(
                "KAP HTTP session is not configured"
            )

        member_id = self._resolve_member_id(
            symbol=symbol,
        )

        url = self._build_financial_search_url(
            member_id=member_id,
        )

        response = self.session.get(url)
        response.raise_for_status()

        return self._extract_disclosure_id(
            html=response.text,
        )
    
    def _extract_financial_disclosures(
        self,
        html: str,
    ) -> list[dict]:
        """Extract financial disclosure metadata from KAP payload."""

        payload_pattern = re.compile(
            (
                r'\\"disclosureIndex\\":(\d+)'
                r'(?:(?!\\"disclosureIndex\\":).)*?'
                r'\\"title\\":\\"Finansal Rapor\\"'
                r'(?:(?!\\"disclosureIndex\\":).)*?'
                r'\\"year\\":(\d{4})'
                r'(?:(?!\\"disclosureIndex\\":).)*?'
                r'\\"period\\":(\d+)'
            )
        )

        payload_matches = payload_pattern.findall(
            html
        )

        return [
            {
                "disclosureIndex": int(disclosure_id),
                "title": "Finansal Rapor",
                "year": int(year),
                "period": int(period),
            }
            for disclosure_id, year, period
            in payload_matches
        ]

    def _extract_disclosure_id(
        self,
        html: str,
    ) -> int:
        """Extract the latest financial report disclosure ID."""

        # Current KAP Next.js payload format.
        disclosures = self._extract_financial_disclosures(
            html=html,
        )

        if disclosures:
            return self._select_latest_financial_disclosure(
            disclosures
        )

        # Legacy/simple HTML format used by existing tests.
        anchor_matches = re.findall(
            (
                r'<a[^>]+href=["\']'
                r'/tr/Bildirim/(\d+)'
                r'["\'][^>]*>'
                r'\s*Finansal Rapor\s*'
                r'</a>'
            ),
            html,
            flags=re.IGNORECASE,
            )

        if not anchor_matches:
            raise RuntimeError(
            "Financial disclosure ID not found"
            )

        return max(
            int(disclosure_id)
            for disclosure_id in anchor_matches
            )

    def _fetch_disclosure_page(
        self,
        disclosure_id: int,
    ) -> str:
        """Fetch a KAP financial disclosure detail page."""

        if self.session is None:
            raise RuntimeError(
            "KAP HTTP session is not configured"
        )

        url = self._build_disclosure_url(
        disclosure_id=disclosure_id,
        )

        response = self.session.get(url)
        response.raise_for_status()

        return response.text

    def fetch_report(
        self,
        symbol: str,
    ) -> dict:
        """Fetch and build the latest KAP financial report."""

        selected = (
            self._find_latest_financial_disclosure_metadata(
            symbol=symbol,
            )
        )

        disclosure_id = int(
            selected["disclosureIndex"]
        )

        html = self._fetch_disclosure_page(
            disclosure_id=disclosure_id,
        )

        report = self._build_report(
            html=html,
        )

        self._validate_financial_period(
            year=int(selected["year"]),
            period=int(selected["period"]),
            actual_period_end=report["period_end"],
        )

        return report

    def fetch_report_for_period(
        self,
        symbol: str,
        year: int,
        period: int,
    ) -> dict:
        """Fetch a KAP financial report for a specific period."""

        metadata = (
            self._find_financial_disclosure_metadata_for_period(
                symbol=symbol,
                year=year,
                period=period,
            )
        )

        disclosure_id = int(
            metadata["disclosureIndex"]
        )

        html = self._fetch_disclosure_page(
            disclosure_id=disclosure_id,
        )

        report = self._build_report(
            html=html,
        )

        self._validate_financial_period(
            year=year,
            period=period,
            actual_period_end=report["period_end"],
        )

        return report
    
    def _extract_scale_text(
        self,
        html: str,
    ) -> str:
        """Extract the presentation currency scale from KAP HTML."""

        match = re.search(
            (
                r"Sunum Para Birimi"
                r".{0,500}?"
                r"((?:\d[\d.]*\s*)?TL)"
            ),
            html,
            flags=re.DOTALL,
        )

        if match is None:
            raise RuntimeError(
            "Financial report scale not found"
            )

        return match.group(1)

    def _extract_period_ends(
        self,
        html: str,
    ) -> tuple[str, str]:
        """Extract current and previous comparable period end dates."""

        match = re.search(
        (
            r"Cari Dönem"
            r".{0,500}?"
            r"(\d{2}\.\d{2}\.\d{4})"
            r"\s*-\s*"
            r"(\d{2}\.\d{2}\.\d{4})"
            r".{0,1000}?"
            r"Önceki Dönem"
            r".{0,500}?"
            r"(\d{2}\.\d{2}\.\d{4})"
            r"\s*-\s*"
            r"(\d{2}\.\d{2}\.\d{4})"
        ),
        html,
        flags=re.DOTALL,
        )

        if match is None:
            raise RuntimeError(
            "Financial report periods not found"
        )

        period_end = match.group(2)
        previous_period_end = match.group(4)

        return period_end, previous_period_end

    def _extract_financial_row(
        self,
        html: str,
        xbrl_code: str,
    ) -> dict[str, float]:
        """Extract current and previous values for an XBRL row."""

        row_start = html.find(
        f"{xbrl_code}|"
        )

        if row_start == -1:
            raise RuntimeError(
            f"Financial row not found: {xbrl_code}"
        )

        next_row_start = html.find(
            "taxonomy-field-name",
            row_start + len(xbrl_code),
        )

        if next_row_start == -1:
            row_html = html[row_start:]
        else:
            row_html = html[
            row_start:next_row_start
        ]

        current_match = re.search(
            (
                r'col-order-class-4'
                r'.*?'
                r'title=\\"(-?\d+(?:\.\d+)?)\\"'
            ),
            row_html,
            flags=re.DOTALL,
        )

        previous_match = re.search(
            (
                r'col-order-class-5'
                r'.*?'
                r'title=\\"(-?\d+(?:\.\d+)?)\\"'
            ),
            row_html,
            flags=re.DOTALL,
        )

        if current_match is None or previous_match is None:
            raise RuntimeError(
            f"Financial row values not found: {xbrl_code}"
        )

        return {
            "current": float(current_match.group(1)),
            "previous": float(previous_match.group(1)),
        }

    def _extract_financial_rows(
        self,
        html: str,
    ) -> dict[str, dict[str, float]]:
        """Extract available financial rows from KAP HTML."""

        xbrl_codes = [
            "ifrs-full_Revenue",
            "ifrs-full_ProfitLoss",
            "ifrs-full_Assets",
            "ifrs-full_Equity",
            "kap-fr_CurrentBorowings",
            "kap-fr_CurrentPortionOfNoncurrentBorrowings",
            "ifrs-full_LongtermBorrowings",
            "ifrs-full_CashAndCashEquivalents",
            "kap-fr_InterestIncome",
        ]

        rows: dict[str, dict[str, float]] = {}

        for xbrl_code in xbrl_codes:
            try:
                rows[xbrl_code] = self._extract_financial_row(
                html=html,
                xbrl_code=xbrl_code,
            )
            except RuntimeError:
                continue

        return rows

    def _build_report(
        self,
        html: str,
    ) -> dict:
        """Build structured financial report data from KAP HTML."""

        scale_text = self._extract_scale_text(
        html=html,
        )

        period_end, previous_period_end = (
            self._extract_period_ends(
            html=html,
        )
        )

        rows = self._extract_financial_rows(
        html=html,
        )

        return {
            "scale_text": scale_text,
            "period_end": period_end,
            "previous_period_end": previous_period_end,
            "rows": rows,
        }

    def _select_latest_financial_disclosure_metadata(
        self,
        disclosures: list[dict],
    ) -> dict:
        """Return metadata for the latest financial disclosure."""

        financial_reports = [
            disclosure
            for disclosure in disclosures
            if disclosure.get("title") == "Finansal Rapor"
            and disclosure.get("year") is not None
            and disclosure.get("period") is not None
            and disclosure.get("disclosureIndex") is not None
        ]

        if not financial_reports:
            raise RuntimeError(
                "Financial disclosure ID not found"
        )

        return max(
            financial_reports,
            key=lambda disclosure: (
            int(disclosure["year"]),
            int(disclosure["period"]),
            int(disclosure["disclosureIndex"]),
        ),
    )

    def _select_financial_disclosure_metadata_for_period(
        self,
        disclosures: list[dict],
        year: int,
        period: int,
    ) -> dict:
        """Return financial disclosure metadata for a specific period."""

        matching_disclosures = [
            disclosure
            for disclosure in disclosures
            if disclosure.get("title") == "Finansal Rapor"
            and disclosure.get("year") is not None
            and disclosure.get("period") is not None
            and int(disclosure["year"]) == year
            and int(disclosure["period"]) == period
        ]

        if not matching_disclosures:
            raise RuntimeError(
                "Financial disclosure not found for period: "
                f"{year}/{period}"
            )

        return max(
            matching_disclosures,
            key=lambda disclosure: int(
            disclosure["disclosureIndex"]
        ),
    )
    
    def _select_latest_financial_disclosure(
        self,
        disclosures: list[dict],
    ) -> int:
        """Return disclosure ID for the latest financial period."""

        selected = (
            self._select_latest_financial_disclosure_metadata(
                disclosures
            )
        )

        return int(selected["disclosureIndex"])

    def _financial_period_end(
        self,
        year: int,
        period: int,
    ) -> str:
        """Return the expected period-end date for a KAP period."""

        period_ends = {
            1: "31.03",
            2: "30.06",
            3: "30.09",
            4: "31.12",
        }

        period_end = period_ends.get(period)

        if period_end is None:
            raise RuntimeError(
                f"Unsupported financial period: {period}"
        )

        return f"{period_end}.{year}"

    def _validate_financial_period(
        self,
        year: int,
        period: int,
        actual_period_end: str,
    ) -> None:
        """Validate that the fetched report matches the selected KAP period."""

        expected_period_end = self._financial_period_end(
            year=year,
            period=period,
        )

        if actual_period_end != expected_period_end:
            raise RuntimeError(
                "Financial report period mismatch: "
                f"expected {expected_period_end}, "
                f"got {actual_period_end}"
            )