"""Scanner result model."""

from dataclasses import dataclass


@dataclass(slots=True)
class ScanResult:
    """Result of scanning a single symbol."""

    symbol: str
    above_sma20: bool
    rsi_above_50: bool
    macd_bullish: bool

    close: float = 0.0
    sma20: float = 0.0
    rsi14: float = 0.0
    macd: float = 0.0
    signal: float = 0.0
    histogram: float = 0.0

    @property
    def macd_score(self) -> int:
        """Return MACD score out of 40."""

        if self.close <= 0:
            return 0

        histogram_percent = (
            self.histogram
            / self.close
            * 100
        )

        if histogram_percent <= 0:
            return 0

        if histogram_percent < 0.10:
            return 10

        if histogram_percent < 0.25:
            return 20

        if histogram_percent < 0.50:
            return 30

        return 40

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

    @property
    def weighted_score(self) -> int:
        """Return weighted score out of 100."""

        return (
        self.sma_score
        + self.rsi_score
        + self.macd_score
    )
    
    @property
    def sma_score(self) -> int:
        """Return SMA score out of 30."""

        if self.sma20 <= 0:
            return 0

        distance_percent = (
        (self.close - self.sma20)
        / self.sma20
        * 100
        )

        if distance_percent <= 0:
            return 0

        if distance_percent < 2:
            return 10

        if distance_percent < 5:
            return 20

        return 30

    @property
    def rsi_score(self) -> int:
        """Return RSI score out of 30."""

        if self.rsi14 < 45:
            return 0

        if self.rsi14 < 50:
            return 10

        if self.rsi14 < 60:
            return 20

        if self.rsi14 < 70:
            return 30

        return 15
    @property
    def rating(self) -> str:
        """Return rating based on weighted score."""

        score = self.weighted_score

        if score >= 80:
            return "STRONG"

        if score >= 60:
            return "PASS"

        if score >= 40:
            return "WATCH"

        return "FAIL"