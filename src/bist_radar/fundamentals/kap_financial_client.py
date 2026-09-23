"""KAP financial report client."""


class KapFinancialClient:
    """Client for retrieving financial report data from KAP."""

    def __init__(
        self,
        transport=None,
    ) -> None:
        self.transport = transport

    def fetch_report(
        self,
        symbol: str,
    ) -> dict:
        """Fetch financial report data for a symbol."""

        if self.transport is None:
            raise RuntimeError(
                "KAP financial transport is not configured"
            )

        return self.transport.fetch_report(
            symbol=symbol,
        )

    def fetch_report_for_period(
        self,
        symbol: str,
        year: int,
        period: int,
    ) -> dict:
        """Fetch financial report data for a specific period."""

        if self.transport is None:
            raise RuntimeError(
                "KAP financial transport is not configured"
            )

        return self.transport.fetch_report_for_period(
            symbol=symbol,
            year=year,
            period=period,
        )