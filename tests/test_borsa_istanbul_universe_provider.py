import pytest
import json
from datetime import date

from bist_radar.universe.borsa_istanbul_provider import (
    BorsaIstanbulUniverseProvider,
)


def test_provider_extracts_bist100_symbols() -> None:
    provider = BorsaIstanbulUniverseProvider()

    raw_symbols = [
        "ASELS",
        "THYAO",
        "TUPRS",
    ]

    symbols = provider._normalize_symbols(
        raw_symbols
    )

    assert symbols == [
        "ASELS",
        "THYAO",
        "TUPRS",
    ]


def test_provider_normalizes_symbols() -> None:
    provider = BorsaIstanbulUniverseProvider()

    raw_symbols = [
        " asels ",
        "THYAO",
        "",
        "   ",
        "tuprs",
        "ASELS",
    ]

    symbols = provider._normalize_symbols(
        raw_symbols
    )

    assert symbols == [
        "ASELS",
        "THYAO",
        "TUPRS",
    ]


def test_provider_returns_fetched_symbols() -> None:
    provider = BorsaIstanbulUniverseProvider()

    raw_symbols = [
        f"test{i:03d}"
        for i in range(100)
    ]

    provider._fetch_symbols = lambda: raw_symbols

    symbols = provider.get_symbols()

    assert len(symbols) == 100
    assert symbols[0] == "TEST000"
    assert symbols[-1] == "TEST099"


def test_provider_rejects_empty_universe() -> None:
    provider = BorsaIstanbulUniverseProvider()

    provider._fetch_symbols = lambda: []

    with pytest.raises(
        RuntimeError,
        match="BIST 100 universe is empty",
    ):
        provider.get_symbols()


def test_provider_rejects_incomplete_bist100() -> None:
    provider = BorsaIstanbulUniverseProvider()

    provider._fetch_symbols = lambda: [
        f"TEST{i:03d}"
        for i in range(99)
    ]

    with pytest.raises(
        RuntimeError,
        match="Expected 100 BIST 100 symbols",
    ):
        provider.get_symbols()

def test_provider_can_read_snapshot_file(
    tmp_path,
    ) -> None:
    snapshot_path = (
        tmp_path / "bist100_snapshot.json"
    )

    symbols = [
        f"TEST{i:03d}"
        for i in range(100)
    ]

    import json

    snapshot_path.write_text(
        json.dumps(
            {
                "index": "XU100",
                "snapshot_date": "2026-09-15",
                "symbols": symbols,
            }
        ),
        encoding="utf-8",
    )

    provider = BorsaIstanbulUniverseProvider(
        snapshot_path=snapshot_path,
    )

    result = provider.get_symbols()

    assert len(result) == 100
    assert result[0] == "TEST000"
    assert result[-1] == "TEST099"

def test_provider_reads_snapshot_date_from_file(
    tmp_path,
    ) -> None:
    snapshot_path = (
        tmp_path / "bist100_snapshot.json"
    )

    symbols = [
        f"TEST{i:03d}"
        for i in range(100)
    ]

    snapshot_path.write_text(
        json.dumps(
            {
                "index": "XU100",
                "snapshot_date": "2026-09-15",
                "symbols": symbols,
            }
        ),
        encoding="utf-8",
    )

    provider = BorsaIstanbulUniverseProvider(
        snapshot_path=snapshot_path,
    )

    provider.get_symbols()

    assert provider.snapshot_date == date(
        2026,
        9,
        15,
    )