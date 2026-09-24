"""FastAPI application."""

from fastapi import Depends, FastAPI, HTTPException, Query

from bist_radar.api.models import (
    ScanItemResponse,
    ScanResponse,
)
from bist_radar.api.scan_service import build_scan_results
from bist_radar.api.serializers import scan_result_to_dict
from bist_radar.data.yahoo_provider import YahooFinanceProvider
from bist_radar.kap.enricher import KapEnricher
from bist_radar.kap.factory import create_kap_provider
from bist_radar.kap.service import KapService
from bist_radar.scanner.engine import ScannerEngine
from bist_radar.api.scan_service import build_scan_results
from bist_radar.api.bist100_scan_service import (
    build_bist100_candidates, build_bist100_candidate_analysis,
)
from bist_radar.fundamentals.provider import FundamentalProvider
from bist_radar.fundamentals.analysis import analyze_fundamentals
import requests

from bist_radar.fundamentals.kap_financial_client import (
    KapFinancialClient,
)
from bist_radar.fundamentals.kap_http_financial_transport import (
    KapHttpFinancialTransport,
)
from bist_radar.fundamentals.kap_member_resolver import (
    KapMemberResolver,
)
from bist_radar.fundamentals.kap_provider import (
    KapFundamentalProvider,
)
from bist_radar.fundamentals.scoring import (
    calculate_fundamental_score,
)


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

def build_fundamental_provider(
    session: requests.Session,
) -> FundamentalProvider:
    """Build KAP fundamental data provider."""

    member_resolver = KapMemberResolver.from_kap(
        session=session,
    )

    transport = KapHttpFinancialTransport(
        session=session,
        member_resolver=member_resolver,
    )

    financial_client = KapFinancialClient(
        transport=transport,
    )

    return KapFundamentalProvider(
        financial_client=financial_client,
    )

def get_http_session() -> requests.Session:
    """Return HTTP session dependency."""

    return requests.Session()

def get_fundamental_provider(
    session: requests.Session = Depends(
        get_http_session
    ),
) -> FundamentalProvider:
    """Return KAP fundamental data provider dependency."""

    member_resolver = KapMemberResolver.from_kap(
        session=session,
    )

    transport = KapHttpFinancialTransport(
        session=session,
        member_resolver=member_resolver,
    )

    financial_client = KapFinancialClient(
        transport=transport,
    )

    return KapFundamentalProvider(
        financial_client=financial_client,
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

    try:
        scan_results = build_scan_results(
            engine=engine,
            kap_enricher=kap_enricher,
            symbols=parsed_symbols,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market data service is temporarily unavailable."
            ),
        ) from exc

    serialized_results = [
        scan_result_to_dict(result)
        for result in scan_results
    ]

    return {
        "symbols": parsed_symbols,
        "results": serialized_results,
    }


@app.get(
    "/stocks/{symbol}",
    response_model=ScanItemResponse,
)
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

    try:
        scan_results = build_scan_results(
            engine=engine,
            kap_enricher=kap_enricher,
            symbols=[parsed_symbol],
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market data service is temporarily unavailable."
            ),
        ) from exc

    if not scan_results:
        raise HTTPException(
            status_code=404,
            detail="Stock data not found.",
        )

    result = scan_results[0]

    return scan_result_to_dict(result)

@app.get("/bist100/candidates")
def bist100_candidates(
        engine: ScannerEngine = Depends(get_scanner_engine),
        kap_enricher: KapEnricher | None = Depends(get_kap_enricher),
    ) -> dict[str, object]:
        """Return BIST 100 candidates with technical score >= 85."""

        results = build_bist100_candidates(
            engine=engine,
            kap_enricher=kap_enricher,
        )

        serialized_results = [
            scan_result_to_dict(result)
            for result in results
        ]

        return {
            "minimum_score": 85,
            "count": len(serialized_results),
            "results": serialized_results,
        }

@app.get("/bist100/analysis")
def bist100_analysis(
    engine: ScannerEngine = Depends(get_scanner_engine),
    kap_enricher: KapEnricher | None = Depends(get_kap_enricher),
    fundamental_provider: FundamentalProvider = Depends(
        get_fundamental_provider
    ),
) -> dict[str, object]:
    """Return technical and fundamental analysis for BIST 100 candidates."""

    results = build_bist100_candidate_analysis(
        engine=engine,
        kap_enricher=kap_enricher,
        fundamental_provider=fundamental_provider,
    )

    serialized_results = []

    for result in results:
        fundamental = result.fundamental

        serialized_results.append(
            {
                "technical": scan_result_to_dict(
                    result.technical
                ),
                "fundamental": (
                    {
                        "symbol": fundamental.symbol,
                        "roe": fundamental.roe,
                        "roe_ttm": fundamental.roe_ttm,
                        "net_margin": fundamental.net_margin,
                        "revenue_growth": (
                            fundamental.revenue_growth
                        ),
                        "net_income_growth": (
                            fundamental.net_income_growth
                        ),
                        "interest_income_growth": (
                            fundamental.interest_income_growth
                        ),
                        "debt_to_equity": (
                            fundamental.debt_to_equity
                        ),
                        "net_debt": fundamental.net_debt,
                        "fundamental_score": (
                            calculate_fundamental_score(
                                fundamental
                            )
                        ),
                    }
                    if fundamental is not None
                    else None
                ),
            }
        )

    return {
        "minimum_score": 85,
        "count": len(serialized_results),
        "results": serialized_results,
    }

@app.get("/fundamentals/{symbol}")
def fundamentals(
    symbol: str,
    provider: FundamentalProvider = Depends(
        get_fundamental_provider
    ),
) -> dict[str, object]:
    """Return fundamental snapshot and analysis for a stock."""

    parsed_symbol = symbol.strip().upper()

    try:
        snapshot = provider.get_snapshot(
            symbol=parsed_symbol,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Fundamental data service is "
                "temporarily unavailable."
            ),
        ) from exc

    analysis = analyze_fundamentals(
        snapshot=snapshot,
    )

    return {
        "symbol": snapshot.symbol,
        "revenue": snapshot.revenue,
        "net_income": snapshot.net_income,
        "total_assets": snapshot.total_assets,
        "total_equity": snapshot.total_equity,
        "total_debt": snapshot.total_debt,
        "cash": snapshot.cash,
        "previous_revenue": snapshot.previous_revenue,
        "previous_net_income": snapshot.previous_net_income,
        "period_end": snapshot.period_end,
        "previous_period_end": snapshot.previous_period_end,
        "analysis": {
            "roe": analysis.roe,
            "net_margin": analysis.net_margin,
            "revenue_growth": analysis.revenue_growth,
            "net_income_growth": analysis.net_income_growth,
            "debt_to_equity": analysis.debt_to_equity,
            "net_debt": analysis.net_debt,
        },
    }