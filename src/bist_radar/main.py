"""Application entry point."""

import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from bist_radar.core.config import AppConfig
from bist_radar.core.logging import configure_logging
from bist_radar.data.yahoo_provider import YahooFinanceProvider
from bist_radar.indicators.calculator import add_indicators
from bist_radar.kap.enricher import KapEnricher
from bist_radar.kap.factory import create_kap_provider
from bist_radar.kap.service import KapService
from bist_radar.reports.csv_report import export_scan_results_to_csv
from bist_radar.reports.excel_report import export_scan_results_to_excel
from bist_radar.scanner.engine import ScannerEngine
from bist_radar.scanner.rules import (
    is_above_sma20,
    is_macd_bullish,
    is_rsi_above_50,
    passes_basic_strategy,
)


def main() -> None:
    """Run the application."""

    config = AppConfig()
    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)

    logger.info(
        "%s v%s started.",
        config.app_name,
        config.version,
    )

    provider = YahooFinanceProvider()

    print("=" * 50)
    print(config.app_name)
    print(f"Version : {config.version}")
    print("Status  : Foundation")
    print("=" * 50)

    end = date.today()
    start = end - timedelta(days=365)

    # -------------------------------------------------
    # THYAO sample data
    # -------------------------------------------------

    print("\nTHYAO Örnek Verisi:")

    raw_df = provider.get_history(
        symbol="THYAO",
        start=start,
        end=end,
    )

    print(raw_df.head())

    # -------------------------------------------------
    # Technical indicators
    #
    # Use the same calculator as ScannerEngine.
    # This also removes incomplete OHLC rows.
    # -------------------------------------------------

    df = add_indicators(raw_df)

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

    # -------------------------------------------------
    # Basic scanner example
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Symbols
    # -------------------------------------------------

    symbols = [
        "THYAO",
        "ASELS",
        "TUPRS",
        "KRDMD",
        "EREGL",
    ]

    engine = ScannerEngine(
        provider,
    )

    passed_symbols = engine.scan_symbols(
        symbols=symbols,
        start=start,
        end=end,
    )

    print("\nToplu Tarama Sonucu")
    print("Taranan hisseler:", symbols)
    print("Geçen hisseler:", passed_symbols)

    # -------------------------------------------------
    # Detailed scan
    # -------------------------------------------------

    detailed_results = engine.get_ranked_scan_results(
        symbols=symbols,
        start=start,
        end=end,
    )

    # -------------------------------------------------
    # KAP enrichment
    # -------------------------------------------------

    kap_provider = create_kap_provider()

    if kap_provider is not None:
        kap_service = KapService(
            provider=kap_provider,
        )

        kap_enricher = KapEnricher(
            service=kap_service,
        )

        kap_start = datetime.combine(
            start,
            datetime.min.time(),
        )

        kap_end = datetime.combine(
            end,
            datetime.max.time(),
        )

        detailed_results = kap_enricher.enrich_all(
            results=detailed_results,
            start=kap_start,
            end=kap_end,
        )

    # -------------------------------------------------
    # CSV report
    # -------------------------------------------------

    output_path = (
        Path("reports")
        / "scan_results.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    export_scan_results_to_csv(
        results=detailed_results,
        output_path=output_path,
    )

    print(
        f"\nCSV raporu oluşturuldu: "
        f"{output_path}"
    )

    # -------------------------------------------------
    # Excel report
    # -------------------------------------------------

    excel_output_path = (
        Path("reports")
        / "scan_results.xlsx"
    )

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
        print(
            "HATA: Excel raporu oluşturulamadı."
        )

    # -------------------------------------------------
    # Terminal results
    # -------------------------------------------------

    print(
        "\nDetaylı Tarama Sonuçları"
    )

    for result in detailed_results:
        vol_confirm = (
            "✓"
            if result.volume_confirms_trend
            else "✗"
        )

        ema_status = (
            "✓"
            if result.above_ema20
            else "✗"
        )

        trend_status = (
            "✓"
            if result.ema_above_sma20
            else "✗"
        )

        if result.kap_has_news:
                kap_status = (
                    f"✓ "
                    f"[{result.kap_importance}] "
                    f"{result.kap_title} "
                    f"[matched: {result.kap_reason}]"
            )

        elif result.kap_importance == "UNAVAILABLE":
            kap_status = (
                    f"✓ "
                    f"[{result.kap_importance}] "
                    f"{result.kap_title} "
                    f"[matched: {result.kap_reason}]"
                    )       

        else:
            kap_status = "✗"

        print(
            f"{result.symbol:<6} "
            f"SMA:{result.sma_score:>2}/30 "
            f"RSI:{result.rsi_score:>2}/30 "
            f"MACD:{result.macd_score:>2}/40 "
            f"EMA:{ema_status} "
            f"TREND:{trend_status} "
            f"ADX:{result.adx14:>5.2f} "
            f"[{result.adx_comment}] "
            f"M5:{result.momentum5:>+6.2f}% "
            f"[{result.momentum5_comment}] "
            f"M20:{result.momentum20:>+6.2f}% "
            f"[{result.momentum20_comment}] "
            f"52WPOS:{result.position_52w:>6.2f}% "
            f"52WHIGH:{result.high_52w_distance:>+6.2f}% "
            f"52W:[{result.position_52w_comment}] "
            f"ATR:{result.atr14:>5.2f} "
            f"ATR%:{result.atr_percent:>4.2f}% "
            f"RISK:[{result.volatility_comment}] "
            f"VOL:{result.volume_ratio:>4.2f}x "
            f"VOLCONF:{vol_confirm} "
            f"TOTAL:{result.weighted_score:>3}/100 "
            f"{result.rating} "
            f"KAP:{kap_status}"
            
        )


if __name__ == "__main__":
    main()