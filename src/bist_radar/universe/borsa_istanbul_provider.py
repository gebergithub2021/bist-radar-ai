"""Borsa Istanbul stock universe provider."""

import json
from datetime import date
from pathlib import Path

from bist_radar.universe.provider import UniverseProvider


class BorsaIstanbulUniverseProvider(UniverseProvider):
    """Provide stock symbols from Borsa Istanbul."""

    EXPECTED_SYMBOL_COUNT = 100

    def __init__(
        self,
        snapshot_path: Path | None = None,
    ) -> None:
        self.snapshot_path = snapshot_path
        self.snapshot_date: date | None = None

    def _normalize_symbols(
        self,
        raw_symbols: list[str],
    ) -> list[str]:
        """Normalize and deduplicate stock symbols."""

        normalized = [
            symbol.strip().upper()
            for symbol in raw_symbols
            if symbol.strip()
        ]

        return list(dict.fromkeys(normalized))

    def _fetch_symbols(self) -> list[str]:
        """Read raw BIST 100 symbols from JSON snapshot."""

        if self.snapshot_path is None:
            return []

        content = self.snapshot_path.read_text(
            encoding="utf-8",
        )

        data = json.loads(content)

        snapshot_date = data.get("snapshot_date")

        if snapshot_date:
            self.snapshot_date = date.fromisoformat(
                snapshot_date
            )

        return data.get("symbols", [])

    def get_symbols(self) -> list[str]:
        """Return validated BIST 100 stock symbols."""

        raw_symbols = self._fetch_symbols()

        symbols = self._normalize_symbols(
            raw_symbols
        )

        if not symbols:
            raise RuntimeError(
                "BIST 100 universe is empty"
            )

        if len(symbols) != self.EXPECTED_SYMBOL_COUNT:
            raise RuntimeError(
                "Expected 100 BIST 100 symbols, "
                f"got {len(symbols)}"
            )

        return symbols