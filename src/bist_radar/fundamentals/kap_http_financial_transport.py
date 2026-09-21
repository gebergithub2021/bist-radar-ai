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

    def _extract_disclosure_id(
        self,
        html: str,
    ) -> int:
        """Extract the latest financial report disclosure ID."""

    # Current KAP Next.js payload format.
        payload_matches = re.findall(
            (
                r'\\"disclosureIndex\\":(\d+)'
                r'(?:(?!\\"disclosureIndex\\":).)*?'
                r'\\"title\\":\\"Finansal Rapor\\"'
            ),
            html,
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

        matches = payload_matches + anchor_matches

        if not matches:
            raise RuntimeError(
            "Financial disclosure ID not found"
            )

        return max(
            int(disclosure_id)
            for disclosure_id in matches
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

        disclosure_id = self._find_latest_financial_disclosure(
        symbol=symbol,
        )

        html = self._fetch_disclosure_page(
        disclosure_id=disclosure_id,
        )

        return self._build_report(
        html=html,
        )
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
        """Extract required financial rows from KAP HTML."""

        xbrl_codes = [
            "ifrs-full_Revenue",
            "ifrs-full_ProfitLoss",
            "ifrs-full_Assets",
            "ifrs-full_Equity",
            "kap-fr_CurrentBorowings",
            "kap-fr_CurrentPortionOfNoncurrentBorrowings",
            "ifrs-full_LongtermBorrowings",
            "ifrs-full_CashAndCashEquivalents",
        ]

        return {
            xbrl_code: self._extract_financial_row(
            html=html,
            xbrl_code=xbrl_code,
        )
            for xbrl_code in xbrl_codes
        }

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