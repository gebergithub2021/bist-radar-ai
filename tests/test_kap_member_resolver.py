from bist_radar.fundamentals.kap_member_resolver import (
    KapMemberResolver,
)
import pytest


def test_kap_member_resolver_resolves_known_symbol() -> None:
    resolver = KapMemberResolver(
        members={
            "ASELS": "4028",
            "THYAO": "1106",
        }
    )

    member_id = resolver.resolve(
        symbol="asels",
    )

    assert member_id == "4028"

def test_kap_member_resolver_raises_for_unknown_symbol() -> None:
    resolver = KapMemberResolver(
        members={
            "ASELS": "4028",
        }
    )

    with pytest.raises(
        RuntimeError,
        match="KAP member ID not found for symbol: UNKNOWN",
    ):
        resolver.resolve(
            symbol="UNKNOWN",
        )

def test_kap_member_resolver_builds_members_from_kap_html() -> None:
    html = r'''
    {
        \"mkkMemberOid\":\"4028e4a1413b7ef401413bc2251e0047\",
        \"kapMemberTitle\":\"ASELSAN ELEKTRONİK SANAYİ VE TİCARET A.Ş.\",
        \"stockCode\":\"ASELS\"
    },
    {
        \"mkkMemberOid\":\"8acae2c562329bd10164405fe6c17996\",
        \"kapMemberTitle\":\"ASTOR ENERJİ A.Ş.\",
        \"stockCode\":\"ASTOR\"
    }
    '''

    resolver = KapMemberResolver.from_html(
        html=html,
    )

    assert resolver.resolve(
        symbol="ASELS",
    ) == "4028e4a1413b7ef401413bc2251e0047"

    assert resolver.resolve(
        symbol="ASTOR",
    ) == "8acae2c562329bd10164405fe6c17996"

class FakeResponse:
    def __init__(
        self,
        text: str,
    ) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        pass


class FakeSession:
    def __init__(
        self,
        html: str,
    ) -> None:
        self.html = html
        self.requested_url = None

    def get(
        self,
        url: str,
        timeout: int,
    ) -> FakeResponse:
        self.requested_url = url

        return FakeResponse(
            text=self.html,
        )


def test_kap_member_resolver_loads_members_from_kap() -> None:
    html = r'''
    {
        \"mkkMemberOid\":\"4028e4a1413b7ef401413bc2251e0047\",
        \"stockCode\":\"ASELS\"
    }
    '''

    session = FakeSession(
        html=html,
    )

    resolver = KapMemberResolver.from_kap(
        session=session,
    )

    assert resolver.resolve(
        symbol="ASELS",
    ) == "4028e4a1413b7ef401413bc2251e0047"

    assert session.requested_url == (
        "https://www.kap.org.tr/tr/bist-sirketler"
    )

def test_resolver_splits_multiple_stock_codes() -> None:
    html = (
        r'{\"mkkMemberOid\":\"member-halkb\",'
        r'\"kapMemberTitle\":\"TÜRKİYE HALK BANKASI A.Ş.\",'
        r'\"stockCode\":\"HALKB, THL\",'
        r'\"kapMemberType\":\"IGS\"}'
    )

    resolver = KapMemberResolver.from_html(html)

    assert resolver.resolve("HALKB") == "member-halkb"
    assert resolver.resolve("THL") == "member-halkb"