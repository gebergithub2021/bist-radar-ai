"""KAP member ID resolver."""

import re


class KapMemberResolver:
    """Resolve stock symbols to KAP member IDs."""

    def __init__(
        self,
        members: dict[str, str],
    ) -> None:
        self.members = {
            symbol.strip().upper(): member_id
            for symbol, member_id in members.items()
        }

    @classmethod
    def from_html(
        cls,
        html: str,
    ) -> "KapMemberResolver":
        """Build a resolver from KAP BIST companies HTML."""

        matches = re.findall(
            (
                r'\\"mkkMemberOid\\":\\"([^"]+)\\"'
                r'.{0,1000}?'
                r'\\"stockCode\\":\\"([^"]+)\\"'
            ),
            html,
            flags=re.DOTALL,
        )

        members: dict[str, str] = {}

        for member_id, stock_codes in matches:
            for stock_code in stock_codes.split(","):
                parsed_stock_code = stock_code.strip().upper()

                if parsed_stock_code:
                    members[parsed_stock_code] = member_id

        return cls(
        members=members,
    )

    @classmethod
    def from_kap(
        cls,
        session,
    ) -> "KapMemberResolver":
        """Load BIST company member IDs from KAP."""

        url = "https://www.kap.org.tr/tr/bist-sirketler"

        response = session.get(
            url,
            timeout=30,
        )
        response.raise_for_status()

        return cls.from_html(
            html=response.text,
        )

    def resolve(
        self,
        symbol: str,
    ) -> str:
        """Return the KAP member ID for a stock symbol."""

        parsed_symbol = symbol.strip().upper()

        try:
            return self.members[parsed_symbol]
        except KeyError as exc:
            raise RuntimeError(
                "KAP member ID not found for symbol: "
                f"{parsed_symbol}"
            ) from exc