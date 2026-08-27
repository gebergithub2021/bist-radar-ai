"""Application entry point."""

import logging
from datetime import date, timedelta
from pathlib import Path
from bist_radar.reports.csv_report import export_scan_results_to_csv
from bist_radar.core.config import AppConfig
from bist_radar.core.logging import configure_logging
from bist_radar.data.yahoo_provider import YahooFinanceProvider
from bist_radar.indicators.ema import calculate_ema
from bist_radar.indicators.macd import calculate_macd
from bist_radar.indicators.rsi import calculate_rsi
from bist_radar.indicators.sma import calculate_sma
from bist_radar.scanner.engine import ScannerEngine
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_macd_bullish,
    is_rsi_above_50,
    passes_basic_strategy,
)
from bist_radar.reports.excel_report import export_scan_results_to_excel


def main() -> None:
    """Run the application."""

    config = AppConfig()
    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)
    logger.info("%s v%s started.", config.app_name, config.version)

    provider = YahooFinanceProvider()

    print("=" * 50)
    print(config.app_name)
    print(f"Version : {config.version}")
    print("Status  : Foundation")
    print("=" * 50)

    end = date.today()
    start = end - timedelta(days=365)

    print("\nTHYAO Örnek Verisi:")

    df = provider.get_history(
        symbol="THYAO",
        start=start,
        end=end,
    )

    print(df.head())

    # Teknik göstergeler
    df["SMA20"] = calculate_sma(df, period=20)
    df["EMA20"] = calculate_ema(df, period=20)
    df["RSI14"] = calculate_rsi(df, period=14)

    macd_df = calculate_macd(df)
    df = df.join(macd_df)

    print("\nTHYAO Teknik Göstergeler:")

    print(
        df[
            [
                "Date",
                "Close",
                "SMA20",
                "EMA20",
                "RSI14",
                "MACD",
                "Signal",
                "Histogram",
            ]
        ].tail()
    )

    print("\nScanner Sonucu")

    print(
        "Close > SMA20:",
        is_above_sma20(df),
    )

    print(
        "RSI14 > 50:",
        is_rsi_above_50(df),
    )

    print(
        "MACD > Signal:",
        is_macd_bullish(df),
    )

    print(
        "Basic Strategy:",
        passes_basic_strategy(df),
    )

    symbols = [
        "THYAO",
        "ASELS",
        "TUPRS",
        "KRDMD",
        "EREGL",
    ]

    engine = ScannerEngine(provider)

    passed_symbols = engine.scan_symbols(
        symbols=symbols,
        start=start,
        end=end,
    )

    print("\nToplu Tarama Sonucu")
    print("Taranan hisseler:", symbols)
    print("Geçen hisseler:", passed_symbols)

    detailed_results = engine.get_ranked_scan_results(
    symbols=symbols,
    start=start,
    end=end,
    )

    output_path = Path("reports") / "scan_results.csv"

    output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
    )

    export_scan_results_to_csv(
    results=detailed_results,
    output_path=output_path,
    )

    print(f"\nCSV raporu oluşturuldu: {output_path}")

    excel_output_path = Path("reports") / "scan_results.xlsx"

    export_scan_results_to_excel(
    results=detailed_results,
    output_path=excel_output_path,
)

    if excel_output_path.exists():
        print(
            f"Excel raporu oluşturuldu: "
            f"{excel_output_path.resolve()}"
        )
    else:
        print("HATA: Excel raporu oluşturulamadı.")

    print("\nDetaylı Tarama Sonuçları")

    for result in detailed_results:
        status = result.rating

        sma_status = "✓" if result.above_sma20 else "✗"
        rsi_status = "✓" if result.rsi_above_50 else "✗"
        macd_status = "✓" if result.macd_bullish else "✗"
        vol_confirm = "✓" if result.volume_confirms_trend else "✗"

        print(
            f"{result.symbol:<6} "
            f"SMA:{result.sma_score:>2}/30 "
            f"RSI:{result.rsi_score:>2}/30 "
            f"MACD:{result.macd_score:>2}/40 "
            f"VOL:{result.volume_ratio:>4.2f}x "
            f"VOLCONF:{vol_confirm} "
            f"TOTAL:{result.weighted_score:>3}/100 "
            f"{result.rating}"
        )

if __name__ == "__main__":
    main()