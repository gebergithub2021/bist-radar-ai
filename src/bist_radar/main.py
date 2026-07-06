"""Application entry point."""

import logging

from bist_radar.core.config import AppConfig
from bist_radar.core.logging import configure_logging
from bist_radar.data import provider
from bist_radar.data.mock_provider import MockMarketDataProvider
from datetime import date, timedelta


def main() -> None:
    """Run the application."""

    config = AppConfig()

    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info("%s v%s started.", config.app_name, config.version)

    provider = MockMarketDataProvider()
   
    print("=" * 50)
    print(config.app_name)
    print(f"Version : {config.version}")
    print("Status  : Foundation")
    print("=" * 50)

    print("\nSemboller:")
    print(provider.get_symbols())
    end = date.today()
    start = end - timedelta(days=365)

    print("\nTHYAO Örnek Verisi:")

    df = provider.get_history(
    "THYAO",
    start,
    end,
    )
    print(df)
    

if __name__ == "__main__":
    main()