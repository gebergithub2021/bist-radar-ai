"""Logging configuration."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
    )