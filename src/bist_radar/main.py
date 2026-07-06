"""Application entry point."""

import logging

from bist_radar.core.config import AppConfig
from bist_radar.core.logging import configure_logging


def main() -> None:
    """Run the application."""

    config = AppConfig()

    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info("%s v%s started.", config.app_name, config.version)

    print("=" * 50)
    print(config.app_name)
    print(f"Version : {config.version}")
    print("Status  : Foundation")
    print("=" * 50)


if __name__ == "__main__":
    main()