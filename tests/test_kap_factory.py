"""Tests for KAP provider factory."""

import pytest

from bist_radar.kap.fake_provider import FakeKapProvider
from bist_radar.kap.factory import create_kap_provider
from bist_radar.kap.real_provider import RealKapProvider


def test_create_kap_provider_defaults_to_off(
    monkeypatch,
):
    monkeypatch.delenv(
        "BIST_RADAR_KAP_MODE",
        raising=False,
    )

    provider = create_kap_provider()

    assert provider is None


def test_create_fake_kap_provider(
    monkeypatch,
):
    monkeypatch.setenv(
        "BIST_RADAR_KAP_MODE",
        "fake",
    )

    provider = create_kap_provider()

    assert isinstance(
        provider,
        FakeKapProvider,
    )


def test_create_real_kap_provider(
    monkeypatch,
):
    monkeypatch.setenv(
        "BIST_RADAR_KAP_MODE",
        "real",
    )
    monkeypatch.setenv(
        "KAP_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "KAP_BASE_URL",
        "https://example.com",
    )

    provider = create_kap_provider()

    assert isinstance(
        provider,
        RealKapProvider,
    )


def test_real_mode_requires_api_key(
    monkeypatch,
):
    monkeypatch.setenv(
        "BIST_RADAR_KAP_MODE",
        "real",
    )
    monkeypatch.delenv(
        "KAP_API_KEY",
        raising=False,
    )
    monkeypatch.setenv(
        "KAP_BASE_URL",
        "https://example.com",
    )

    with pytest.raises(
        ValueError,
        match="KAP_API_KEY",
    ):
        create_kap_provider()


def test_unknown_mode_raises_error(
    monkeypatch,
):
    monkeypatch.setenv(
        "BIST_RADAR_KAP_MODE",
        "something",
    )

    with pytest.raises(
        ValueError,
        match="Unknown BIST_RADAR_KAP_MODE",
    ):
        create_kap_provider()