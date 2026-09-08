"""FastAPI application."""

from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query

from bist_radar.api.models import (
    ScanItemResponse,
    ScanResponse,
)
from bist_radar.api.serializers import scan_result_to_dict
from bist_radar.data.yahoo_provider import YahooFinanceProvider
from bist_radar.kap.enricher import KapEnricher
from bist_radar.kap.factory import create_kap_provider
from bist_radar.kap.service import KapService
from bist_radar.scanner.engine import ScannerEngine


app = FastAPI(
    title="BistRadarAI API",
    version="0.1.0",
)


def get_scanner_engine() -> ScannerEngine:
    """Return scanner engine dependency."""

    provider = YahooFinanceProvider()

    return ScannerEngine(
        provider=provider,
    )


def get_kap_enricher() -> KapEnricher | None:
    """Return KAP enricher dependency."""

    kap_provider = create_kap_provider()

    if kap_provider is None:
        return None

    service = KapService(
        provider=kap_provider,
    )

    return KapEnricher(
        service=service,
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""

    return {
        "status": "ok",
        "service": "BistRadarAI",
    }


@app.get(
    "/scan",
    response_model=ScanResponse,
)
def scan(
    symbols: str = Query(
        default="THYAO,ASELS,TUPRS,KRDMD,EREGL",
    ),
    engine: ScannerEngine = Depends(
        get_scanner_engine
    ),
    kap_enricher: KapEnricher | None = Depends(
        get_kap_enricher
    ),
) -> dict[str, object]:
    """Run radar scan for requested symbols."""

    raw_symbols = [
        symbol.strip().upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]

    parsed_symbols = list(
        dict.fromkeys(raw_symbols)
    )

    if not parsed_symbols:
        raise HTTPException(
            status_code=422,
            detail="At least one symbol is required.",
        )

    if len(parsed_symbols) > 20:
        raise HTTPException(
            status_code=422,
            detail="A maximum of 20 symbols is allowed.",
        )

    end = date.today()
    start = end - timedelta(days=365)

    try:
        scan_results = engine.get_ranked_scan_results(
            symbols=parsed_symbols,
            start=start,
            end=end,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market data service is temporarily unavailable."
            ),
        ) from exc

    if kap_enricher is not None:
        kap_end_date = end
        kap_start_date = kap_end_date - timedelta(
            days=30,
        )

        kap_start = datetime.combine(
            kap_start_date,
            datetime.min.time(),
        )

        kap_end = datetime.combine(
            kap_end_date,
            datetime.max.time(),
        )

        try:
            scan_results = kap_enricher.enrich_all(
                results=scan_results,
                start=kap_start,
                end=kap_end,
            )
        except RuntimeError:
            for result in scan_results:
                result.kap_has_news = False
                result.kap_importance = "UNAVAILABLE"
                result.kap_title = (
                    "KAP service unavailable"
                )
                result.kap_reason = "service error"
                result.kap_url = ""

    serialized_results = [
        scan_result_to_dict(result)
        for result in scan_results
    ]

    return {
        "symbols": parsed_symbols,
        "results": serialized_results,
    }

@app.get("/stocks/{symbol}", response_model=ScanItemResponse,)
def stock_detail(
    symbol: str,
    engine: ScannerEngine = Depends(
        get_scanner_engine
    ),
    kap_enricher: KapEnricher | None = Depends(
        get_kap_enricher
        ),
    ) -> dict[str, object]:
    """Return scan detail for a single stock."""

    parsed_symbol = symbol.strip().upper()

    end = date.today()
    start = end - timedelta(days=365)

    try:
        scan_results = engine.get_ranked_scan_results(
            symbols=[parsed_symbol],
            start=start,
            end=end,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market data service is temporarily unavailable."
            ),
        ) from exc

    if kap_enricher is not None:
        kap_end_date = end
        kap_start_date = kap_end_date - timedelta(
            days=30,
        )

        kap_start = datetime.combine(
            kap_start_date,
            datetime.min.time(),
        )

        kap_end = datetime.combine(
            kap_end_date,
            datetime.max.time(),
        )

        try:
            scan_results = kap_enricher.enrich_all(
                results=scan_results,
                start=kap_start,
                end=kap_end,
            )
        except RuntimeError:
            for result in scan_results:
                result.kap_has_news = False
                result.kap_importance = "UNAVAILABLE"
                result.kap_title = (
                    "KAP service unavailable"
                )
                result.kap_reason = "service error"
                result.kap_url = ""

    result = scan_results[0]

    return scan_result_to_dict(result)