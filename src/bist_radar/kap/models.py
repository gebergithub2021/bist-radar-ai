"""KAP disclosure models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class KapDisclosure:
    """A disclosure published on KAP."""

    disclosure_id: str
    symbol: str
    published_at: datetime
    title: str
    summary: str = ""
    url: str = ""