"""Market data provider interface."""

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """Return all available stock symbols."""
        raise NotImplementedError

    @abstractmethod
    def get_history(
        self,
        symbol: str,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        """Return historical price data for the given symbol."""
        raise NotImplementedError