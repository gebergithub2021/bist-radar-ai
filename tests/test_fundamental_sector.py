from bist_radar.fundamentals.sector import (
    FundamentalSector,
    resolve_fundamental_sector,
)
import pytest


def test_resolve_bank_sector() -> None:
    assert (
        resolve_fundamental_sector("HALKB")
        == FundamentalSector.BANK
    )


def test_resolve_standard_sector() -> None:
    assert (
        resolve_fundamental_sector("ENERY")
        == FundamentalSector.STANDARD
    )

def test_resolve_isctr_as_bank_sector() -> None:
    assert (
        resolve_fundamental_sector("ISCTR")
        == FundamentalSector.BANK
    )
def test_resolve_garan_as_bank_sector() -> None:
    assert (
        resolve_fundamental_sector("GARAN")
        == FundamentalSector.BANK
    )

def test_resolve_akbnk_as_bank_sector() -> None:
    assert (
        resolve_fundamental_sector("AKBNK")
        == FundamentalSector.BANK
    )

@pytest.mark.parametrize(
    "symbol",
    [
        "SKBNK",
        "TSKB",
        "VAKBN",
        "YKBNK",
    ],
)
def test_resolve_verified_banks_as_bank_sector(
    symbol: str,
) -> None:
    assert (
        resolve_fundamental_sector(symbol)
        == FundamentalSector.BANK
    )