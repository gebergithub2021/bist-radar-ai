from bist_radar.fundamentals.kap_http_financial_transport import (
    KapHttpFinancialTransport,
)
import pytest


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