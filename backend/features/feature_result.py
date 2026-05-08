# This file defines the standard result structure returned by every email security feature.

from dataclasses import dataclass, field
from typing import Any, Literal


VerdictLevel = Literal[
    "safe",
    "low_risk",
    "suspicious",
    "high_risk"
]


@dataclass
class FeatureResult:
    """
    Stores the output of a single email security feature.
    """

    feature_id: str
    title: str
    description: str

    detected: bool
    score: int

    evidence: dict[str, Any] = field(default_factory=dict)

    minimum_verdict: VerdictLevel | None = None


def create_not_detected_result(
    feature_id: str,
    title: str,
    description: str
) -> FeatureResult:
    """
    Creates a default result for a feature that was not detected.
    """

    return FeatureResult(
        feature_id=feature_id,
        title=title,
        description=description,
        detected=False,
        score=0,
        evidence={},
        minimum_verdict=None
    )