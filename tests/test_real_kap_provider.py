"""Tests for real KAP provider."""

import pytest

from bist_radar.kap.real_provider import RealKapProvider


def test_real_kap_provider_requires_api_integration():
    provider = RealKapProvider(
        api_key="test-key",
        base_url="https://example.com",
    )

    with pytest.raises(NotImplementedError):
        provider.get_disclosures(
            symbol="ASELS",
            start=None,
            end=None,
        )