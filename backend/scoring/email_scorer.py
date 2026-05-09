# This file calculates the final email verdict from all extracted feature results.

from features.feature_result import FeatureResult
from scoring.schemas import FinalEmailVerdict


HIGH_RISK_THRESHOLD = 70
SUSPICIOUS_THRESHOLD = 40
LOW_RISK_THRESHOLD = 15


def calculate_email_verdict(
    feature_results: list[FeatureResult]
) -> FinalEmailVerdict:
    """
    Calculates the final email verdict from extracted feature results.
    """

    hard_signals = extract_hard_signals(
        feature_results
    )

    regular_score = calculate_regular_score(
        feature_results
    )

    detected_features = [
        feature
        for feature in feature_results
        if feature.detected
    ]

    if hard_signals:

        return FinalEmailVerdict(
            verdict="high_risk",

            regular_score=regular_score,

            hard_signals=hard_signals,

            detected_features=detected_features,
        )

    verdict = determine_score_based_verdict(
        regular_score
    )

    return FinalEmailVerdict(
        verdict=verdict,

        regular_score=regular_score,

        hard_signals=[],

        detected_features=detected_features,
    )


def extract_hard_signals(
    feature_results: list[FeatureResult]
) -> list[FeatureResult]:
    """
    Extracts features that force a minimum verdict.
    """

    return [
        feature
        for feature in feature_results
        if feature.minimum_verdict is not None
    ]


def calculate_regular_score(
    feature_results: list[FeatureResult]
) -> int:
    """
    Calculates the combined weighted score of all regular features
    and normalizes it to the range 0-100.
    """

    raw_score = sum(
        feature.score
        for feature in feature_results
    )

    normalized_score = max(
        0,
        min(raw_score, 100)
    )

    return normalized_score


def determine_score_based_verdict(
    regular_score: int
) -> str:
    """
    Determines the final verdict from the weighted regular score.
    """

    if regular_score >= HIGH_RISK_THRESHOLD:
        return "high_risk"

    if regular_score >= SUSPICIOUS_THRESHOLD:
        return "suspicious"

    if regular_score >= LOW_RISK_THRESHOLD:
        return "low_risk"

    return "safe"