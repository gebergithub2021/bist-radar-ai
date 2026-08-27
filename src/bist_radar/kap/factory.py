"""KAP provider factory."""

import os

from bist_radar.kap.fake_provider import FakeKapProvider
from bist_radar.kap.provider import KapProvider
from bist_radar.kap.real_provider import RealKapProvider


def create_kap_provider() -> KapProvider | None:
    """Create KAP provider based on environment configuration."""

    mode = os.getenv(
        "BIST_RADAR_KAP_MODE",
        "off",
    ).lower()

    if mode == "off":
        return None

    if mode == "fake":
        return FakeKapProvider()

    if mode == "real":
        api_key = os.getenv("KAP_API_KEY")
        base_url = os.getenv("KAP_BASE_URL")

        if not api_key:
            raise ValueError(
                "KAP_API_KEY is required when "
                "BIST_RADAR_KAP_MODE=real."
            )

        if not base_url:
            raise ValueError(
                "KAP_BASE_URL is required when "
                "BIST_RADAR_KAP_MODE=real."
            )

        return RealKapProvider(
            api_key=api_key,
            base_url=base_url,
        )

    raise ValueError(
        f"Unknown BIST_RADAR_KAP_MODE: {mode}"
    )