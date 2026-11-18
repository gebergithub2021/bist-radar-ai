
from datetime import date

import pandas as pd

from bist_radar.data.price_cache import PriceCache


def test_price_cache_save_and_load(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame(
        {
            "Date": ["2026-11-02", "2026-11-03"],
            "Open": [300, 305],
            "High": [310, 312],
            "Low": [295, 301],
            "Close": [307, 309],
            "Volume": [1000000, 1200000],
        }
    )

    cache.save("THYAO", prices)

    loaded = cache.load("THYAO")

    assert loaded is not None
    assert len(loaded) == 2
    assert loaded["Close"].tolist() == [307, 309]
    assert loaded["Volume"].tolist() == [1000000, 1200000]

    assert (
        loaded["Date"].dt.date.tolist()
        == [date(2026, 11, 2), date(2026, 11, 3)]
    )


def test_price_cache_updates_existing_date(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    original = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-03"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    cache.save("THYAO", original)

    updated = pd.DataFrame({
        "Date": ["2026-11-03"],
        "Open": [306],
        "High": [315],
        "Low": [302],
        "Close": [311],
        "Volume": [1500000],
    })

    cache.save("THYAO", updated)

    loaded = cache.load("THYAO")

    assert loaded is not None
    assert len(loaded) == 2

    assert loaded["Close"].tolist() == [307, 311]
    assert loaded["Volume"].tolist() == [
        1000000, 1500000
    ]

def test_price_cache_load_range(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": [
            "2026-11-02",
            "2026-11-03",
            "2026-11-04",
            "2026-11-05",
            "2026-11-06",
        ],
        "Open": [300, 305, 310, 315, 320],
        "High": [310, 312, 315, 320, 325],
        "Low": [295, 301, 307, 312, 317],
        "Close": [307, 309, 314, 318, 322],
        "Volume": [
            1000000, 1200000, 1400000,
            1600000, 1800000,
        ],
    })

    cache.save("THYAO", prices)

    result = cache.load_range(
        "THYAO",
        date(2026, 11, 3),
        date(2026, 11, 6),
    )

    assert result is not None
    assert len(result) == 3

    assert result["Close"].tolist() == [
        309, 314, 318
    ]

    assert result["Date"].dt.date.tolist() == [
        date(2026, 11, 3),
        date(2026, 11, 4),
        date(2026, 11, 5),
    ]

def test_price_cache_detects_missing_trading_day(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": [
            "2026-11-02",
            "2026-11-03",
            "2026-11-05",
        ],
        "Open": [300, 305, 315],
        "High": [310, 312, 320],
        "Low": [295, 301, 312],
        "Close": [307, 309, 318],
        "Volume": [1000000, 1200000, 1600000],
    })

    cache.save("THYAO", prices)

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 6),
    )

    assert missing_days == [
        date(2026, 11, 4)
    ]

def test_price_cache_groups_missing_trading_days(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-05"],
        "Open": [300, 315],
        "High": [310, 320],
        "Low": [295, 312],
        "Close": [307, 318],
        "Volume": [1000000, 1600000],
    })

    cache.save("THYAO", prices)

    missing_ranges = cache.get_missing_weekday_ranges(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 6),
    )

    assert missing_ranges == [
        (
            date(2026, 11, 3),
            date(2026, 11, 5),
        )
    ]

def test_price_cache_ignores_bist_holidays(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-10-28", "2026-10-30"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    cache.save("THYAO", prices)

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 10, 28),
        date(2026, 10, 31),
    )

    assert missing_days == []

def test_price_cache_detects_missing_half_trading_day(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-10-27", "2026-10-30"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    cache.save("THYAO", prices)

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 10, 27),
        date(2026, 10, 31),
    )

    assert missing_days == [
        date(2026, 10, 28)
    ]

def test_price_cache_handles_ramadan_holiday_2026(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-03-18", "2026-03-23"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    cache.save("THYAO", prices)

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 3, 18),
        date(2026, 3, 24),
    )

    assert missing_days == [
        date(2026, 3, 19)
    ]

def test_price_cache_handles_eid_al_adha_2026(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-05-25"],
        "Open": [300],
        "High": [310],
        "Low": [295],
        "Close": [307],
        "Volume": [1000000],
    })

    cache.save("THYAO", prices)

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 5, 25),
        date(2026, 6, 1),
    )

    assert missing_days == [
        date(2026, 5, 26)
    ]

def test_price_cache_keeps_symbols_separate(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    thyao_prices = pd.DataFrame({
        "Date": ["2026-11-02"],
        "Open": [300],
        "High": [310],
        "Low": [295],
        "Close": [307],
        "Volume": [1000000],
    })

    asels_prices = pd.DataFrame({
        "Date": ["2026-11-02"],
        "Open": [175],
        "High": [185],
        "Low": [172],
        "Close": [180],
        "Volume": [2000000],
    })

    cache.save("THYAO", thyao_prices)
    cache.save("ASELS", asels_prices)

    thyao_loaded = cache.load("THYAO")
    asels_loaded = cache.load("ASELS")

    assert thyao_loaded is not None
    assert asels_loaded is not None

    assert thyao_loaded["Close"].tolist() == [307]
    assert asels_loaded["Close"].tolist() == [180]

    assert (tmp_path / "THYAO.csv").exists()
    assert (tmp_path / "ASELS.csv").exists()

def test_price_cache_returns_none_for_unknown_symbol(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    result = cache.load("TUPRS")

    assert result is None
    assert not (tmp_path / "TUPRS.csv").exists()

def test_price_cache_detects_all_days_when_empty(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    missing_days = cache.get_missing_weekdays(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 7),
    )

    assert missing_days == [
        date(2026, 11, 2),
        date(2026, 11, 3),
        date(2026, 11, 4),
        date(2026, 11, 5),
        date(2026, 11, 6),
    ]

    assert not (tmp_path / "THYAO.csv").exists()

def test_price_cache_creates_download_ranges(tmp_path):
    cache = PriceCache(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-05"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    cache.save("THYAO", prices)

    download_ranges = cache.get_download_ranges(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 7),
    )

    assert download_ranges == [
        (date(2026, 11, 3), date(2026, 11, 5)),
        (date(2026, 11, 6), date(2026, 11, 7)),
    ]

def test_yahoo_provider_skips_download_when_cached(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-03"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    provider.price_cache.save("THYAO", prices)

    mock_download = Mock()
    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 4),
    )

    mock_download.assert_not_called()

    assert len(result) == 2
    assert result["Close"].tolist() == [307, 309]

def test_yahoo_provider_downloads_only_missing_day(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-04"],
        "Open": [300, 310],
        "High": [310, 320],
        "Low": [295, 305],
        "Close": [307, 315],
        "Volume": [1000000, 1300000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    downloaded_prices = pd.DataFrame({
        "Open": [305],
        "High": [312],
        "Low": [301],
        "Close": [309],
        "Volume": [1200000],
    }, index=pd.DatetimeIndex(
        ["2026-11-03"], name="Date"
    ))

    mock_download = Mock(return_value=downloaded_prices)

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 1

    call_kwargs = mock_download.call_args.kwargs

    assert str(call_kwargs["start"])[:10] == "2026-11-03"
    assert str(call_kwargs["end"])[:10] == "2026-11-04"

    assert len(result) == 3
    assert result["Close"].tolist() == [307, 309, 315]

def test_yahoo_provider_uses_cache_when_download_fails(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-03"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    mock_download = Mock(
        side_effect=ConnectionError("Yahoo Finance unavailable")
    )

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 1

    assert len(result) == 2
    assert result["Close"].tolist() == [307, 309]
    assert result["Volume"].tolist() == [1000000, 1200000]

def test_yahoo_provider_uses_cache_when_download_empty(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02", "2026-11-03"],
        "Open": [300, 305],
        "High": [310, 312],
        "Low": [295, 301],
        "Close": [307, 309],
        "Volume": [1000000, 1200000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    mock_download = Mock(return_value=pd.DataFrame())

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 1

    assert len(result) == 2
    assert result["Close"].tolist() == [307, 309]
    assert result["Volume"].tolist() == [1000000, 1200000]

def test_yahoo_provider_saves_partial_download(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02"],
        "Open": [300],
        "High": [310],
        "Low": [295],
        "Close": [307],
        "Volume": [1000000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    downloaded_prices = pd.DataFrame({
        "Open": [305],
        "High": [312],
        "Low": [301],
        "Close": [309],
        "Volume": [1200000],
    }, index=pd.DatetimeIndex(
        ["2026-11-03"], name="Date"
    ))

    mock_download = Mock(return_value=downloaded_prices)

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 1

    assert len(result) == 2
    assert result["Close"].tolist() == [307, 309]

    cached_result = provider.price_cache.load("THYAO")

    assert cached_result is not None
    assert len(cached_result) == 2
    assert cached_result["Volume"].tolist() == [
        1000000, 1200000
    ]

    assert provider.price_cache.get_missing_weekdays(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    ) == [date(2026, 11, 4)]

def test_yahoo_provider_retries_only_remaining_missing_day(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02"],
        "Open": [300],
        "High": [310],
        "Low": [295],
        "Close": [307],
        "Volume": [1000000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    first_download = pd.DataFrame({
        "Open": [305],
        "High": [312],
        "Low": [301],
        "Close": [309],
        "Volume": [1200000],
    }, index=pd.DatetimeIndex(
        ["2026-11-03"], name="Date"
    ))

    second_download = pd.DataFrame({
        "Open": [310],
        "High": [320],
        "Low": [305],
        "Close": [315],
        "Volume": [1300000],
    }, index=pd.DatetimeIndex(
        ["2026-11-04"], name="Date"
    ))

    mock_download = Mock(
        side_effect=[first_download, second_download]
    )

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    first_result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert len(first_result) == 2

    second_result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 2

    second_call = mock_download.call_args_list[1].kwargs

    assert str(second_call["start"])[:10] == "2026-11-04"
    assert str(second_call["end"])[:10] == "2026-11-05"

    assert len(second_result) == 3
    assert second_result["Close"].tolist() == [307, 309, 315]

    assert provider.price_cache.get_missing_weekdays(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    ) == []

def test_yahoo_provider_skips_download_after_cache_filled(
    tmp_path, monkeypatch
):
    from unittest.mock import Mock
    from bist_radar.data.yahoo_provider import YahooFinanceProvider

    provider = YahooFinanceProvider(cache_dir=str(tmp_path))

    cached_prices = pd.DataFrame({
        "Date": ["2026-11-02"],
        "Open": [300],
        "High": [310],
        "Low": [295],
        "Close": [307],
        "Volume": [1000000],
    })

    provider.price_cache.save("THYAO", cached_prices)

    downloaded_prices = pd.DataFrame({
        "Open": [305, 310],
        "High": [312, 320],
        "Low": [301, 305],
        "Close": [309, 315],
        "Volume": [1200000, 1300000],
    }, index=pd.DatetimeIndex(
        ["2026-11-03", "2026-11-04"],
        name="Date",
    ))

    mock_download = Mock(return_value=downloaded_prices)

    monkeypatch.setattr(
        "bist_radar.data.yahoo_provider.yf.download",
        mock_download,
    )

    first_result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert len(first_result) == 3
    assert mock_download.call_count == 1

    second_result = provider.get_history(
        "THYAO",
        date(2026, 11, 2),
        date(2026, 11, 5),
    )

    assert mock_download.call_count == 1

    assert len(second_result) == 3
    assert second_result["Close"].tolist() == [
        307, 309, 315
    ]
