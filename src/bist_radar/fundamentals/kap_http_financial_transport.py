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

        matches = re.findall(
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

        if not matches:
            raise RuntimeError(
            "Financial disclosure ID not found"
        )

        return max(
            int(disclosure_id)
            for disclosure_id in matches
        )