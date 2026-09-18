"""Fundamental data provider interface."""

from abc import ABC, abstractmethod

from bist_radar.fundamentals.models import FundamentalSnapshot


class FundamentalProvider(ABC):
    """Interface for fundamental data providers."""

    @abstractmethod
    def get_snapshot(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:
        """Return a fundamental snapshot for a symbol."""