"""Scanner result model."""

from dataclasses import dataclass


@dataclass(slots=True)
class ScanResult:
    """Result of scanning a single symbol."""

    symbol: str
    above_sma20: bool
    rsi_above_50: bool
    macd_bullish: bool

    @property
    def score(self) -> int:
        """Return the number of passed rules."""
        return sum(
            [
                self.above_sma20,
                self.rsi_above_50,
                self.macd_bullish,
            ]
        )

    @property
    def passed(self) -> bool:
        """Return True when all rules pass."""
        return self.score == 3