
from datetime import date

import pandas as pd


class BISTTradingCalendar:
    """Basic trading-day calendar for Borsa Istanbul."""


    def is_half_day(self, day: date) -> bool:
        """Check known BIST half trading days."""
        fixed_half_days = {
            (10, 28),  # Cumhuriyet Bayrami arifesi
        }

        variable_half_days: dict[int, set[date]] = {
            2026: {
                date(2026, 3, 19),  # Ramazan Bayrami arifesi
                date(2026, 5, 26),  # Kurban Bayrami arifesi
            },
        }

        return (
            (day.month, day.day) in fixed_half_days
            or day in variable_half_days.get(day.year, set())
        )


    def is_holiday(self, day: date) -> bool:
        """Check known full-day BIST holidays."""
        fixed_holidays = {
            (1, 1),    # Yilbasi
            (4, 23),   # Ulusal Egemenlik ve Cocuk Bayrami
            (5, 1),    # Emek ve Dayanisma Gunu
            (5, 19),   # Ataturk'u Anma, Genclik ve Spor Bayrami
            (7, 15),   # Demokrasi ve Milli Birlik Gunu
            (8, 30),   # Zafer Bayrami
            (10, 29),  # Cumhuriyet Bayrami
        }


        
        variable_holidays: dict[int, set[date]] = {
            2026: {
                # Ramazan Bayrami
                date(2026, 3, 20),
                date(2026, 3, 21),
                date(2026, 3, 22),

                # Kurban Bayrami
                date(2026, 5, 27),
                date(2026, 5, 28),
                date(2026, 5, 29),
                date(2026, 5, 30),
            },
        }


        if day in variable_holidays.get(day.year, set()):
            return True


        return (day.month, day.day) in fixed_holidays


    
    def is_trading_day(self, day: date) -> bool:
        """Check whether a date is a potential BIST trading day."""
        is_weekday = day.weekday() < 5
        is_not_holiday = not self.is_holiday(day)

        return is_weekday and is_not_holiday


    
    def get_trading_days(
        self,
        start: date,
        end: date,
    ) -> list[date]:
        """Return potential BIST trading days; end is exclusive."""
        if start >= end:
            return []

        days = pd.bdate_range(
            start=start,
            end=end - pd.Timedelta(days=1),
        )

        return [
            day.date()
            for day in days
            if self.is_trading_day(day.date())
        ]

