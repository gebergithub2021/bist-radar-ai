
from pathlib import Path

import pandas as pd
from datetime import date
from datetime import timedelta
from bist_radar.data.trading_calendar import BISTTradingCalendar


class PriceCache:
    """Store daily stock prices and volumes on disk."""

    
    def __init__(self, cache_dir: str = ".cache/prices") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.trading_calendar = BISTTradingCalendar()


    
    def save(self, symbol: str, df: pd.DataFrame) -> None:
        """Merge new prices with existing cached prices."""
        filename = f"{symbol.upper()}.csv"
        cache_path = self.cache_dir / filename

        existing = self.load(symbol)

        if existing is not None:
            df = pd.concat(
                [existing, df],
                ignore_index=True,
            )

        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        df = (
            df.drop_duplicates(
                subset=["Date"],
                keep="last",
            )
            .sort_values("Date")
            .reset_index(drop=True)
        )

        df.to_csv(cache_path, index=False)

    def load(self, symbol: str) -> pd.DataFrame | None:
        """Load cached prices for a stock."""
        filename = f"{symbol.upper()}.csv"
        cache_path = self.cache_dir / filename

        if not cache_path.exists():
            return None

        return pd.read_csv(
            cache_path,
            parse_dates=["Date"],
        )

    
    def load_range(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> pd.DataFrame | None:
        """Load cached prices within a date range."""
        df = self.load(symbol)

        if df is None:
            return None

        mask = (
            (df["Date"].dt.date >= start)
            & (df["Date"].dt.date < end)
        )

        return df.loc[mask].reset_index(drop=True)

    def get_date_bounds(
        self,
        symbol: str,
    ) -> tuple[date, date] | None:
        """Return the first and last cached dates."""
        df = self.load(symbol)

        if df is None or df.empty:
            return None

        dates = pd.to_datetime(df["Date"])

        return (
            dates.min().date(),
            dates.max().date(),
        )


    def get_stale_trading_days(
        self,
        symbol: str,
        as_of: date,
        market_closed: bool = True,
    ) -> int | None:
        """Count trading days since the latest cached price."""

        bounds = self.get_date_bounds(symbol)

        if bounds is None:
            return None

        last_cached_date = bounds[1]

        if last_cached_date >= as_of:
            return 0

        end_date = as_of + pd.Timedelta(days=1) if market_closed else as_of

        trading_days = self.trading_calendar.get_trading_days(
            start=last_cached_date + pd.Timedelta(days=1),
            end=end_date,
        )

        return len(trading_days)

    def get_missing_ranges(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> list[tuple[date, date]]:
        """Find missing ranges outside cached date bounds."""
        if start >= end:
            return []

        bounds = self.get_date_bounds(symbol)

        if bounds is None:
            return [(start, end)]

        first_cached, last_cached = bounds

        # Requested range does not overlap cached dates.
        if end <= first_cached:
            return [(start, end)]

        if start > last_cached:
            return [(start, end)]

        missing = []

        if start < first_cached:
            missing.append(
                (start, min(end, first_cached))
            )

        if end > last_cached + pd.Timedelta(days=1):
            missing.append(
                (
                    max(
                        start,
                        last_cached + pd.Timedelta(days=1),
                    ),
                    end,
                )
            )

        return missing
    
    
    def get_missing_weekdays(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> list[date]:
        """Find missing BIST trading days in cached prices."""
        if start >= end:
            return []

        trading_days = self.trading_calendar.get_trading_days(
            start,
            end,
        )

        df = self.load_range(symbol, start, end)

        if df is None:
            return trading_days

        cached_dates = set(df["Date"].dt.date)

        return [
            day
            for day in trading_days
            if day not in cached_dates
        ]

    
    def get_missing_weekday_ranges(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> list[tuple[date, date]]:
        """Group consecutive missing weekdays into date ranges."""
        missing_days = self.get_missing_weekdays(
            symbol, start, end
        )

        if not missing_days:
            return []

        ranges = []
        range_start = missing_days[0]
        previous = missing_days[0]

        
        
        for current in missing_days[1:]:
            days_between = (
                self.trading_calendar.get_trading_days(
                    previous + timedelta(days=1),
                    current,
                )
            )

            is_consecutive = len(days_between) == 0


            if not is_consecutive:

                ranges.append(
                    (range_start, previous + timedelta(days=1))
                )
                range_start = current

            previous = current

        ranges.append(
            (range_start, previous + timedelta(days=1))
        )

        return ranges

    
    def get_download_ranges(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> list[tuple[date, date]]:
        """Find candidate date ranges to download."""
        if start >= end:
            return []

        return self.get_missing_weekday_ranges(
            symbol,
            start,
            end,
        )



