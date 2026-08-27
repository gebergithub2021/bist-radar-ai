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
    volume: float = 0.0
    volume_sma20: float = 0.0
    volume_ratio: float = 0.0
    volume_confirms_trend: bool = False
    momentum5: float = 0.0
    momentum20: float = 0.0
    above_ema20: bool = False
    ema_above_sma20: bool = False
    high_52w: float = 0.0
    low_52w: float = 0.0
    position_52w: float = 0.0
    high_52w_distance: float = 0.0
    atr14: float = 0.0
    atr_percent: float = 0.0
    adx14: float = 0.0
    kap_has_news: bool = False
    kap_importance: str = "NONE"
    kap_title: str = ""

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
    @property
    def momentum5_comment(self) -> str:
        """Return short-term momentum comment."""

        if self.momentum5 >= 5:
            return "STRONG POSITIVE"

        if self.momentum5 >= 1:
         return "POSITIVE"

        if self.momentum5 > -1:
         return "NEUTRAL"

        if self.momentum5 > -5:
            return "NEGATIVE"

        return "STRONG NEGATIVE"


    @property
    def momentum20_comment(self) -> str:
        """Return medium-term momentum comment."""

        if self.momentum20 >= 10:
            return "STRONG POSITIVE"

        if self.momentum20 >= 3:
            return "POSITIVE"

        if self.momentum20 > -3:
            return "NEUTRAL"

        if self.momentum20 > -10:
            return "NEGATIVE"

        return "STRONG NEGATIVE"
    
    @property
    def position_52w_comment(self) -> str:
        """Return 52-week position comment."""

        if self.position_52w >= 90:
            return "NEAR 52W HIGH"

        if self.position_52w >= 70:
            return "UPPER RANGE"

        if self.position_52w >= 40:
            return "MID RANGE"

        return "LOWER RANGE"

    @property
    def volatility_comment(self) -> str:
            """Return volatility comment based on ATR percentage."""

            if self.atr_percent < 2.5:
                return "LOW"

            if self.atr_percent < 4.0:
                return "MEDIUM"

            return "HIGH"
    @property
    def adx_comment(self) -> str:
        """Return trend strength comment based on ADX."""

        if self.adx14 < 20:
            return "WEAK"

        if self.adx14 < 25:
            return "DEVELOPING"

        if self.adx14 < 40:
            return "STRONG"

        return "VERY STRONG"