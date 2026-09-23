"""Fundamental sector classification."""

from enum import Enum


class FundamentalSector(str, Enum):
    """Fundamental analysis sector types."""

    STANDARD = "STANDARD"
    BANK = "BANK"


_BANK_SYMBOLS = {
    "HALKB", "ISCTR",
}


def resolve_fundamental_sector(
    symbol: str,
) -> FundamentalSector:
    """Return the fundamental analysis sector for a symbol."""

    parsed_symbol = symbol.strip().upper()

    if parsed_symbol in _BANK_SYMBOLS:
        return FundamentalSector.BANK

    return FundamentalSector.STANDARD