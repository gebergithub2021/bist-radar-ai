"""Combined candidate analysis model."""

from dataclasses import dataclass

from bist_radar.fundamentals.models import (
    FundamentalAnalysisResult,
)
from bist_radar.models.scan_result import ScanResult


@dataclass(slots=True)
class CandidateAnalysis:
    """Technical and fundamental analysis for a candidate."""

    technical: ScanResult
    fundamental: FundamentalAnalysisResult