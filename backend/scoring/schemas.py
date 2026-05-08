# This file defines the final scoring structures used by the email risk scorer.

from dataclasses import dataclass

from features.feature_result import FeatureResult


@dataclass
class FinalEmailVerdict:
    """
    Stores the final risk analysis result for an email.
    """

    verdict: str

    regular_score: int

    hard_signals: list[FeatureResult]

    detected_features: list[FeatureResult]