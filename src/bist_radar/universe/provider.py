"""Stock universe provider interface."""

from abc import ABC, abstractmethod


class UniverseProvider(ABC):
    """Abstract provider for a stock universe."""

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """Return stock symbols in the universe."""

        raise NotImplementedError