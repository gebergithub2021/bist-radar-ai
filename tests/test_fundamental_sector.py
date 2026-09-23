from bist_radar.fundamentals.sector import (
    FundamentalSector,
    resolve_fundamental_sector,
)


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