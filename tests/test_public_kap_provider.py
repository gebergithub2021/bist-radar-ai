"""Tests for PublicKapProvider."""

from datetime import datetime

import pytest

from bist_radar.kap.public_provider import PublicKapProvider


def test_default_base_url() -> None:
    provider = PublicKapProvider(
        cache_dir=".cache/test_kap_public",
    )

    assert provider.base_url == "https://www.kap.org.tr"


def test_base_url_trailing_slash_is_removed() -> None:
    provider = PublicKapProvider(
        base_url="https://www.kap.org.tr/",
        cache_dir=".cache/test_kap_public",
    )

    assert provider.base_url == "https://www.kap.org.tr"


def test_empty_base_url_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="base_url",
    ):
        PublicKapProvider(
            base_url="",
        )


def test_filters_disclosures_by_symbol(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    provider = PublicKapProvider(
        cache_dir=str(tmp_path),
    )

    raw_disclosures = [
        {
            "publishDate": "27.08.2026 12:30:00",
            "stockCodes": "ASELS",
            "subject": "Yeni İş İlişkisi",
            "summary": "Yeni sözleşme imzalanmıştır.",
            "disclosureIndex": 1655510,
        },
        { 
            "publishDate": "27.08.2026 13:00:00",
            "stockCodes": "THYAO",
            "subject": "Özel Durum Açıklaması",
            "summary": "Genel bilgilendirme.",
            "disclosureIndex": 1655511,
        },
    ]

    monkeypatch.setattr(
        provider,
        "_fetch_raw_disclosures",
        lambda start, end: raw_disclosures,
    )

    disclosures = provider.get_disclosures(
        symbol="ASELS",
        start=datetime(
            2026,
            8,
            27,
            0,
            0,
            0,
        ),
        end=datetime(
            2026,
            8,
            27,
            23,
            59,
            59,
        ),
    )

    assert len(disclosures) == 1

    disclosure = disclosures[0]

    assert disclosure.symbol == "ASELS"
    assert disclosure.title == "Yeni İş İlişkisi"
    assert disclosure.summary == "Yeni sözleşme imzalanmıştır."

    assert (
        disclosure.url
        == "https://www.kap.org.tr/tr/Bildirim/1655510"
    )


def test_ignores_records_without_stock_codes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    provider = PublicKapProvider(
        cache_dir=str(tmp_path),
    )

    raw_disclosures = [
        {
            "publishDate": "27.08.2026 10:00:00",
            "stockCodes": None,
            "kapTitle": "SPK Bülteni",
            "summary": "",
            "disclosureIndex": 1655000,
        },
        {
            "publishDate": "27.08.2026 11:00:00",
            "stockCodes": "ASELS",
            "kapTitle": "Yeni İş İlişkisi",
            "summary": "Yeni sözleşme.",
            "disclosureIndex": 1655001,
        },
    ]

    monkeypatch.setattr(
        provider,
        "_fetch_raw_disclosures",
        lambda start, end: raw_disclosures,
    )

    disclosures = provider.get_disclosures(
        symbol="ASELS",
        start=datetime(
            2026,
            8,
            27,
        ),
        end=datetime(
            2026,
            8,
            27,
            23,
            59,
            59,
        ),
    )

    assert len(disclosures) == 1
    assert disclosures[0].symbol == "ASELS"


def test_raw_disclosures_are_cached_in_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    provider = PublicKapProvider(
        cache_dir=str(tmp_path),
    )

    call_count = 0

    def fake_fetch_range(
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        nonlocal call_count

        call_count += 1

        return [
            {
                "publishDate": "27.08.2026 12:00:00",
                "stockCodes": "ASELS",
                "kapTitle": "Yeni İş İlişkisi",
                "summary": "",
                "disclosureIndex": 1655510,
            }
        ]

    monkeypatch.setattr(
        provider,
        "_fetch_raw_disclosures_for_range",
        fake_fetch_range,
    )

    start = datetime(
        2026,
        8,
        27,
    )

    end = datetime(
        2026,
        8,
        27,
        23,
        59,
        59,
    )

    first = provider._fetch_raw_disclosures(
        start=start,
        end=end,
    )

    second = provider._fetch_raw_disclosures(
        start=start,
        end=end,
    )

    assert first == second
    assert call_count == 1


def test_disk_cache_is_reused_across_provider_instances(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    start = datetime(
        2026,
        8,
        27,
    )

    end = datetime(
        2026,
        8,
        27,
        23,
        59,
        59,
    )

    provider_one = PublicKapProvider(
        cache_dir=str(tmp_path),
    )

    raw_disclosures = [
        {
            "publishDate": "27.08.2026 12:00:00",
            "stockCodes": "ASELS",
            "kapTitle": "Yeni İş İlişkisi",
            "summary": "",
            "disclosureIndex": 1655510,
        }
    ]

    monkeypatch.setattr(
        provider_one,
        "_fetch_raw_disclosures_for_range",
        lambda start, end: raw_disclosures,
    )

    first = provider_one._fetch_raw_disclosures(
        start=start,
        end=end,
    )

    provider_two = PublicKapProvider(
        cache_dir=str(tmp_path),
    )

    def fail_fetch(
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        raise AssertionError(
            "HTTP fetch should not be called when disk cache exists."
        )

    monkeypatch.setattr(
        provider_two,
        "_fetch_raw_disclosures_for_range",
        fail_fetch,
    )

    second = provider_two._fetch_raw_disclosures(
        start=start,
        end=end,
    )

    assert second == first