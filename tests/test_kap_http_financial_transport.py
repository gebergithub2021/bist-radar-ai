from bist_radar.fundamentals.kap_http_financial_transport import (
    KapHttpFinancialTransport,
)
import pytest
from bist_radar.fundamentals.kap_provider import KapFundamentalProvider


def test_kap_http_financial_transport_can_be_created() -> None:
    transport = KapHttpFinancialTransport()

    assert transport is not None
def test_kap_http_financial_transport_accepts_session() -> None:
    class FakeSession:
        pass

    session = FakeSession()

    transport = KapHttpFinancialTransport(
        session=session,
    )

    assert transport.session is session

def test_kap_http_financial_transport_builds_disclosure_url() -> None:
    transport = KapHttpFinancialTransport()

    url = transport._build_disclosure_url(
        disclosure_id=1651637,
    )

    assert url == (
        "https://www.kap.org.tr/tr/Bildirim/1651637"
    )

def test_kap_http_financial_transport_find_latest_disclosure_requires_session() -> None:
    transport = KapHttpFinancialTransport()

    try:
        transport._find_latest_financial_disclosure(
            symbol="ASELS",
        )
    except RuntimeError as exc:
        assert str(exc) == (
            "KAP HTTP session is not configured"
        )
    else:
        raise AssertionError(
            "Expected RuntimeError"
        )

def test_kap_http_financial_transport_accepts_member_resolver() -> None:
    class FakeMemberResolver:
        pass

    resolver = FakeMemberResolver()

    transport = KapHttpFinancialTransport(
        member_resolver=resolver,
    )

    assert transport.member_resolver is resolver

def test_kap_http_financial_transport_resolves_member_id() -> None:
    class FakeMemberResolver:
        def resolve(
            self,
            symbol: str,
        ) -> str:
            assert symbol == "ASELS"

            return "4028e4a1413b7ef401413bc2251e0047"

    transport = KapHttpFinancialTransport(
        member_resolver=FakeMemberResolver(),
    )

    member_id = transport._resolve_member_id(
        symbol="ASELS",
    )

    assert member_id == (
        "4028e4a1413b7ef401413bc2251e0047"
    )

def test_kap_http_financial_transport_requires_member_resolver() -> None:
    class FakeSession:
        pass

    transport = KapHttpFinancialTransport(
        session=FakeSession(),
    )

    with pytest.raises(
        RuntimeError,
        match="KAP member resolver is not configured",
    ):
        transport._resolve_member_id(
            symbol="ASELS",
        )
        
def test_kap_http_financial_transport_builds_financial_search_url() -> None:
    transport = KapHttpFinancialTransport()

    url = transport._build_financial_search_url(
        member_id="4028e4a1413b7ef401413bc2251e0047",
    )

    assert url == (
        "https://www.kap.org.tr/tr/bildirim-sorgu-sonuc"
        "?disclosureClass=FR"
        "&member=4028e4a1413b7ef401413bc2251e0047"
    )

def test_kap_http_financial_transport_requests_financial_search_page() -> None:
    expected_url = (
        "https://www.kap.org.tr/tr/bildirim-sorgu-sonuc"
        "?disclosureClass=FR"
        "&member=4028e4a1413b7ef401413bc2251e0047"
    )

    class FakeMemberResolver:
        def resolve(
            self,
            symbol: str,
        ) -> str:
            assert symbol == "ASELS"
            return "4028e4a1413b7ef401413bc2251e0047"

    class FakeResponse:
        text= (
            '<a href="/tr/Bildirim/1651637">'
            "Finansal Rapor"
            "</a>"
            )

        def raise_for_status(self) -> None:
            pass

    class FakeSession:
        def get(
            self,
            url: str,
        ) -> FakeResponse:
            assert url == expected_url
            return FakeResponse()

    transport = KapHttpFinancialTransport(
        session=FakeSession(),
        member_resolver=FakeMemberResolver(),
    )

    
    transport._find_latest_financial_disclosure(symbol="ASELS",)

def test_kap_http_financial_transport_extracts_disclosure_id() -> None:
    transport = KapHttpFinancialTransport()

    html = """
    <html>
        <body>
            <a href="/tr/Bildirim/1651637">
                Finansal Rapor
            </a>
        </body>
    </html>
    """

    disclosure_id = transport._extract_disclosure_id(
        html=html,
    )

    assert disclosure_id == 1651637

def test_kap_http_financial_transport_raises_when_disclosure_id_missing() -> None:
    transport = KapHttpFinancialTransport()

    html = """
    <html>
        <body>
            <p>Finansal rapor bulunamadı.</p>
        </body>
    </html>
    """

    with pytest.raises(
        RuntimeError,
        match="Financial disclosure ID not found",
    ):
        transport._extract_disclosure_id(
            html=html,
        )

def test_kap_http_financial_transport_extracts_latest_disclosure_id() -> None:
    transport = KapHttpFinancialTransport()

    html = html = """
        <html>
            <body>
            <a href="/tr/Bildirim/1600000">
            Finansal Rapor
            </a>

            <a href="/tr/Bildirim/1651637">
                Finansal Rapor
            </a>
        </body>
    </html>
    """

    disclosure_id = transport._extract_disclosure_id(
        html=html,
    )

    assert disclosure_id == 1651637

def test_kap_http_financial_transport_ignores_non_financial_disclosure() -> None:
    transport = KapHttpFinancialTransport()

    html = """
    <html>
        <body>
            <a href="/tr/Bildirim/1651637">
                Finansal Rapor
            </a>

            <a href="/tr/Bildirim/1700000">
                Özel Durum Açıklaması
            </a>
        </body>
    </html>
    """

    disclosure_id = transport._extract_disclosure_id(
        html=html,
    )

    assert disclosure_id == 1651637

def test_kap_http_financial_transport_extracts_disclosure_id_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_search.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    disclosure_id = transport._extract_disclosure_id(
        html=html,
    )

    assert disclosure_id == 1643141

def test_kap_http_financial_transport_fetches_disclosure_page():
    class FakeResponse:
        text = "<html>financial report detail</html>"

        def raise_for_status(self):
            pass

    class FakeSession:
        def __init__(self):
            self.requested_url = None

        def get(self, url):
            self.requested_url = url
            return FakeResponse()

    session = FakeSession()

    transport = KapHttpFinancialTransport(
        session=session,
    )

    html = transport._fetch_disclosure_page(
        disclosure_id=1643141,
    )

    assert html == "<html>financial report detail</html>"
    assert session.requested_url == (
        "https://www.kap.org.tr/tr/Bildirim/1643141"
    )

def test_kap_http_financial_transport_fetch_disclosure_requires_session():
    transport = KapHttpFinancialTransport()

    with pytest.raises(
        RuntimeError,
        match="KAP HTTP session is not configured",
    ):
        transport._fetch_disclosure_page(
            disclosure_id=1643141,
        )

def test_kap_http_financial_transport_fetch_report_builds_report():
    class FakeResponse:
        text = "<html>financial detail</html>"

        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url):
            return FakeResponse()

    transport = KapHttpFinancialTransport(
        session=FakeSession(),
    )

    transport._find_latest_financial_disclosure_metadata = (
        lambda symbol: {
            "disclosureIndex": 1643141,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        }
    )

    expected_report = {
        "scale_text": "1.000 TL",
        "period_end": "30.06.2026",
        "previous_period_end": "30.06.2025",
        "rows": {},
    }

    transport._build_report = (
        lambda html: expected_report
    )

    report = transport.fetch_report(
        symbol="ASELS",
    )

    assert report == expected_report

def test_kap_http_financial_transport_extracts_scale_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    scale_text = transport._extract_scale_text(
        html=html,
    )

    assert scale_text == "1.000 TL"

def test_kap_http_financial_transport_scale_requires_scale_text():
    transport = KapHttpFinancialTransport()

    with pytest.raises(
        RuntimeError,
        match="Financial report scale not found",
    ):
        transport._extract_scale_text(
            html="<html>no scale here</html>",
        )

def test_kap_http_financial_transport_extracts_periods_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    period_end, previous_period_end = (
        transport._extract_period_ends(
            html=html,
        )
    )

    assert period_end == "30.06.2026"
    assert previous_period_end == "30.06.2025"

def test_kap_http_financial_transport_periods_require_period_data():
    transport = KapHttpFinancialTransport()

    with pytest.raises(
        RuntimeError,
        match="Financial report periods not found",
    ):
        transport._extract_period_ends(
            html="<html>no period data here</html>",
        )

def test_kap_http_financial_transport_extracts_revenue_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="ifrs-full_Revenue",
    )

    assert row == {
        "current": 88494252.0,
        "previous": 70956004.0,
    }

def test_kap_http_financial_transport_financial_row_requires_xbrl_code():
    transport = KapHttpFinancialTransport()

    with pytest.raises(
        RuntimeError,
        match="Financial row not found: ifrs-full_MissingField",
    ):
        transport._extract_financial_row(
            html="<html>no financial rows here</html>",
            xbrl_code="ifrs-full_MissingField",
        )
def test_kap_http_financial_transport_extracts_profit_loss_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="ifrs-full_ProfitLoss",
    )

    assert row == {
        "current": 14449834.0,
        "previous": 8468992.0,
    }

def test_kap_http_financial_transport_extracts_assets_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="ifrs-full_Assets",
    )

    assert row == {
        "current": 549748035.0,
        "previous": 508228606.0,
    }

def test_kap_http_financial_transport_extracts_equity_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="ifrs-full_Equity",
    )

    assert row == {
        "current": 308524609.0,
        "previous": 296498504.0,
    }

def test_kap_http_financial_transport_extracts_current_borrowings_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="kap-fr_CurrentBorowings",
    )

    assert row == {
        "current": 25398173.0,
        "previous": 15456810.0,
    }

def test_kap_http_financial_transport_extracts_current_portion_of_noncurrent_borrowings_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="kap-fr_CurrentPortionOfNoncurrentBorrowings",
    )

    assert row == {
        "current": 39308899.0,
        "previous": 29324421.0,
    }

def test_kap_http_financial_transport_extracts_financial_rows_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    rows = transport._extract_financial_rows(
        html=html,
    )

    assert rows["ifrs-full_Revenue"] == {
        "current": 88494252.0,
        "previous": 70956004.0,
    }

    assert rows["ifrs-full_ProfitLoss"] == {
        "current": 14449834.0,
        "previous": 8468992.0,
    }

    assert rows["ifrs-full_Assets"] == {
        "current": 549748035.0,
        "previous": 508228606.0,
    }

    assert rows["ifrs-full_Equity"] == {
        "current": 308524609.0,
        "previous": 296498504.0,
    }

    assert rows["kap-fr_CurrentBorowings"] == {
        "current": 25398173.0,
        "previous": 15456810.0,
    }

    assert rows[
        "kap-fr_CurrentPortionOfNoncurrentBorrowings"
    ] == {
        "current": 39308899.0,
        "previous": 29324421.0,
    }

    assert rows["ifrs-full_LongtermBorrowings"] == {
        "current": 8586218.0,
        "previous": 5921301.0,
    }

    assert rows["ifrs-full_CashAndCashEquivalents"] == {
        "current": 39468926.0,
        "previous": 34251653.0,
    }

def test_kap_http_financial_transport_extracts_cash_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    row = transport._extract_financial_row(
        html=html,
        xbrl_code="ifrs-full_CashAndCashEquivalents",
    )

    assert row == {
        "current": 39468926.0,
        "previous": 34251653.0,
    }

def test_kap_http_financial_transport_builds_structured_report_from_real_fixture():
    fixture_path = (
        "tests/fixtures/"
        "kap_asels_financial_detail.html"
    )

    with open(
        fixture_path,
        encoding="utf-8",
    ) as fixture:
        html = fixture.read()

    transport = KapHttpFinancialTransport()

    report = transport._build_report(
        html=html,
    )

    assert report["scale_text"] == "1.000 TL"
    assert report["period_end"] == "30.06.2026"
    assert report["previous_period_end"] == "30.06.2025"

    assert report["rows"]["ifrs-full_Revenue"] == {
        "current": 88494252.0,
        "previous": 70956004.0,
    }

    assert report["rows"]["ifrs-full_ProfitLoss"] == {
        "current": 14449834.0,
        "previous": 8468992.0,
    }

    assert report["rows"]["ifrs-full_CashAndCashEquivalents"] == {
        "current": 39468926.0,
        "previous": 34251653.0,
    }

def test_kap_fundamental_provider_maps_real_kap_debt_xbrl_codes():
    provider = KapFundamentalProvider()

    rows = {
            "ifrs-full_Revenue": {
            "current": 88494252.0,
            "previous": 70956004.0,
        },
            "ifrs-full_ProfitLoss": {
            "current": 14449834.0,
            "previous": 8468992.0,
        },
            "ifrs-full_Assets": {
            "current": 549748035.0,
            "previous": 508228606.0,
        },
            "ifrs-full_Equity": {
            "current": 308524609.0,
            "previous": 296498504.0,
        },
            "kap-fr_CurrentBorowings": {
            "current": 25398173.0,
            "previous": 15456810.0,
        },
            "kap-fr_CurrentPortionOfNoncurrentBorrowings": {
            "current": 39308899.0,
            "previous": 29324421.0,
        },
            "ifrs-full_LongtermBorrowings": {
            "current": 8586218.0,
            "previous": 5921301.0,
        },
            "ifrs-full_CashAndCashEquivalents": {
            "current": 39468926.0,
            "previous": 34251653.0,
        },
    }

    mapped = provider._map_financial_rows(
        raw_rows=rows,
    )

    assert mapped["total_debt"] == 73293290.0
    assert mapped["cash"] == 39468926.0

class FakeMemberResolver:
    def __init__(
        self,
        member_id: str,
    ) -> None:
        self.member_id = member_id
        self.requested_symbol = None

    def resolve(
        self,
        symbol: str,
    ) -> str:
        self.requested_symbol = symbol

        return self.member_id


def test_resolve_member_id_uses_member_resolver() -> None:
    resolver = FakeMemberResolver(
        member_id="4028e4a1413b7ef401413bc2251e0047",
    )

    transport = KapHttpFinancialTransport(
        member_resolver=resolver,
    )

    member_id = transport._resolve_member_id(
        symbol="ASELS",
    )

    assert member_id == (
        "4028e4a1413b7ef401413bc2251e0047"
    )
    assert resolver.requested_symbol == "ASELS"

def test_extract_scale_text_accepts_plain_try() -> None:
    transport = KapHttpFinancialTransport()

    html = (
        r"Sunum Para Birimi\u003c/td\u003e"
        r"\u003ctd\u003eTL\u003c/td\u003e"
    )

    scale_text = transport._extract_scale_text(
        html=html,
    )

    assert scale_text == "TL"

def test_extract_financial_rows_skips_missing_rows() -> None:
    transport = KapHttpFinancialTransport()

    def fake_extract_financial_row(
        html: str,
        xbrl_code: str,
    ) -> dict[str, float]:
        if xbrl_code == "ifrs-full_Revenue":
            raise RuntimeError(
                "Financial row not found: ifrs-full_Revenue"
            )

        return {
            "current": 100.0,
            "previous": 90.0,
        }

    transport._extract_financial_row = (
        fake_extract_financial_row
    )

    rows = transport._extract_financial_rows(
        html="fake-html",
    )

    assert "ifrs-full_Revenue" not in rows
    assert "ifrs-full_ProfitLoss" in rows
    assert "ifrs-full_Assets" in rows
    assert "ifrs-full_Equity" in rows

def test_extract_financial_rows_includes_bank_interest_income() -> None:
    transport = KapHttpFinancialTransport()

    requested_codes = []

    def fake_extract_financial_row(
        html: str,
        xbrl_code: str,
    ) -> dict[str, float]:
        requested_codes.append(xbrl_code)

        if xbrl_code == "kap-fr_InterestIncome":
            return {
                "current": 250.0,
                "previous": 200.0,
            }

        raise RuntimeError(
            f"Financial row not found: {xbrl_code}"
        )

    transport._extract_financial_row = (
        fake_extract_financial_row
    )

    rows = transport._extract_financial_rows(
        html="fake-html",
    )

    assert "kap-fr_InterestIncome" in requested_codes
    assert rows["kap-fr_InterestIncome"] == {
        "current": 250.0,
        "previous": 200.0,
    }

def test_latest_financial_disclosure_prefers_latest_period() -> None:
    transport = KapHttpFinancialTransport()

    disclosures = [
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "disclosureClass": "FR",
            "year": 2026,
            "period": 2,
            "donem": "6 Aylık",
        },
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "disclosureClass": "FR",
            "year": 2026,
            "period": 3,
            "donem": "9 Aylık",
        },
    ]

    disclosure_id = (
        transport._select_latest_financial_disclosure(
            disclosures
        )
    )

    assert disclosure_id == 1900

def test_latest_financial_disclosure_prefers_latest_id_within_same_period() -> None:
    transport = KapHttpFinancialTransport()

    disclosures = [
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
    ]

    disclosure_id = (
        transport._select_latest_financial_disclosure(
            disclosures
        )
    )

    assert disclosure_id == 2000

def test_financial_period_end_maps_kap_period_to_date() -> None:
    transport = KapHttpFinancialTransport()

    assert transport._financial_period_end(
        year=2026,
        period=1,
    ) == "31.03.2026"

    assert transport._financial_period_end(
        year=2026,
        period=2,
    ) == "30.06.2026"

    assert transport._financial_period_end(
        year=2026,
        period=3,
    ) == "30.09.2026"

    assert transport._financial_period_end(
        year=2026,
        period=4,
    ) == "31.12.2026"

def test_select_latest_financial_disclosure_metadata() -> None:
    transport = KapHttpFinancialTransport()

    disclosures = [
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 3,
        },
    ]

    selected = (
        transport._select_latest_financial_disclosure_metadata(
            disclosures
        )
    )

    assert selected == {
        "disclosureIndex": 1900,
        "title": "Finansal Rapor",
        "year": 2026,
        "period": 3,
    }
def test_extract_financial_disclosures_from_next_payload() -> None:
    transport = KapHttpFinancialTransport()

    html = (
        r'\"disclosureIndex\":2000,'
        r'\"title\":\"Finansal Rapor\",'
        r'\"year\":2026,'
        r'\"period\":2,'
        r'\"disclosureIndex\":1900,'
        r'\"title\":\"Finansal Rapor\",'
        r'\"year\":2026,'
        r'\"period\":3'
    )

    disclosures = (
        transport._extract_financial_disclosures(
            html=html,
        )
    )

    assert disclosures == [
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 3,
        },
    ]

def test_find_latest_financial_disclosure_metadata() -> None:
    class FakeResponse:
        text = (
            r'\"disclosureIndex\":2000,'
            r'\"title\":\"Finansal Rapor\",'
            r'\"year\":2026,'
            r'\"period\":2,'
            r'\"disclosureIndex\":1900,'
            r'\"title\":\"Finansal Rapor\",'
            r'\"year\":2026,'
            r'\"period\":3'
        )

        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url):
            return FakeResponse()

    transport = KapHttpFinancialTransport(
        session=FakeSession(),
    )

    transport._resolve_member_id = (
        lambda symbol: "1234"
    )

    selected = (
        transport._find_latest_financial_disclosure_metadata(
            symbol="ASELS",
        )
    )

    assert selected == {
        "disclosureIndex": 1900,
        "title": "Finansal Rapor",
        "year": 2026,
        "period": 3,
    }

def test_validate_financial_period_accepts_matching_period() -> None:
    transport = KapHttpFinancialTransport()

    transport._validate_financial_period(
        year=2026,
        period=2,
        actual_period_end="30.06.2026",
    )

def test_validate_financial_period_rejects_mismatch() -> None:
    transport = KapHttpFinancialTransport()

    with pytest.raises(
        RuntimeError,
        match=(
            "Financial report period mismatch: "
            "expected 30.06.2026, got 31.03.2026"
        ),
    ):
        transport._validate_financial_period(
            year=2026,
            period=2,
            actual_period_end="31.03.2026",
        )

def test_fetch_report_validates_selected_financial_period() -> None:
    transport = KapHttpFinancialTransport()

    transport._find_latest_financial_disclosure_metadata = (
        lambda symbol: {
            "disclosureIndex": 1645596,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        }
    )

    transport._fetch_disclosure_page = (
        lambda disclosure_id: "<html>detail</html>"
    )

    transport._build_report = (
        lambda html: {
            "scale_text": "1.000 TL",
            "period_end": "31.03.2026",
            "previous_period_end": "31.03.2025",
            "rows": {},
        }
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Financial report period mismatch: "
            "expected 30.06.2026, got 31.03.2026"
        ),
    ):
        transport.fetch_report(
            symbol="HALKB",
        )
def test_select_financial_disclosure_metadata_for_period() -> None:
    transport = KapHttpFinancialTransport()

    disclosures = [
        {
            "disclosureIndex": 1800,
            "title": "Finansal Rapor",
            "year": 2025,
            "period": 2,
        },
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": 2025,
            "period": 4,
        },
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
    ]

    metadata = (
        transport._select_financial_disclosure_metadata_for_period(
            disclosures=disclosures,
            year=2025,
            period=4,
        )
    )

    assert metadata == {
        "disclosureIndex": 1900,
        "title": "Finansal Rapor",
        "year": 2025,
        "period": 4,
    }

def test_select_financial_disclosure_for_period_prefers_latest_id() -> None:
    transport = KapHttpFinancialTransport()

    disclosures = [
        {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": 2025,
            "period": 4,
        },
        {
            "disclosureIndex": 1950,
            "title": "Finansal Rapor",
            "year": 2025,
            "period": 4,
        },
        {
            "disclosureIndex": 2000,
            "title": "Finansal Rapor",
            "year": 2026,
            "period": 2,
        },
    ]

    metadata = (
        transport._select_financial_disclosure_metadata_for_period(
            disclosures=disclosures,
            year=2025,
            period=4,
        )
    )

    assert metadata["disclosureIndex"] == 1950

def test_fetch_report_for_period_fetches_selected_financial_report() -> None:
    transport = KapHttpFinancialTransport()

    transport._find_financial_disclosure_metadata_for_period = (
        lambda symbol, year, period: {
            "disclosureIndex": 1900,
            "title": "Finansal Rapor",
            "year": year,
            "period": period,
        }
    )

    transport._fetch_disclosure_page = (
        lambda disclosure_id: "<html>financial report</html>"
    )

    transport._build_report = (
        lambda html: {
            "scale_text": "1.000 TL",
            "period_end": "31.12.2025",
            "previous_period_end": "31.12.2024",
            "rows": {},
        }
    )

    report = transport.fetch_report_for_period(
        symbol="ASELS",
        year=2025,
        period=4,
    )

    assert report["period_end"] == "31.12.2025"