"""Tests for RealKapProvider."""

from datetime import datetime

import pytest

from bist_radar.kap.real_provider import RealKapProvider


def test_real_provider_stores_configuration():
    provider = RealKapProvider(
        api_key="test-key",
        base_url="https://example.com/",
    )

    assert provider.api_key == "test-key"
    assert provider.base_url == "https://example.com"


def test_real_provider_requires_api_key():
    with pytest.raises(
        ValueError,
        match="api_key cannot be empty",
    ):
        RealKapProvider(
            api_key="",
            base_url="https://example.com",
        )


def test_real_provider_requires_base_url():
    with pytest.raises(
        ValueError,
        match="base_url cannot be empty",
    ):
        RealKapProvider(
            api_key="test-key",
            base_url="",
        )


def test_get_disclosures_not_implemented_yet():
    provider = RealKapProvider(
        api_key="test-key",
        base_url="https://example.com",
    )

    with pytest.raises(
        NotImplementedError,
        match="Official KAP API",
    ):
        provider.get_disclosures(
            symbol="ASELS",
            start=datetime(2026, 8, 1),
            end=datetime(2026, 8, 31),
        )