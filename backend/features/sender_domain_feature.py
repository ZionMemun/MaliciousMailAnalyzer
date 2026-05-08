# This file analyzes the sender domain for suspicious phishing-like patterns.

import re

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "sender_domain"


SUSPICIOUS_TLDS = {
    "ru",
    "xyz",
    "top",
    "click",
    "work",
    "fit",
    "rest",
    "country",
    "stream",
}


def analyze_sender_domain(
    parsed_email: ParsedEmail
) -> FeatureResult:
    """
    Analyzes the sender domain for suspicious phishing-like patterns.
    """

    sender_domain = parsed_email.from_domain

    if not sender_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Sender domain unavailable",
            description="The sender domain could not be extracted."
        )

    suspicious_patterns = []

    score = 0
    minimum_verdict = None

    if has_suspicious_tld(sender_domain):

        suspicious_patterns.append(
            "suspicious_tld"
        )

        minimum_verdict = "high_risk"

    if has_digit_letter_substitution(
        sender_domain
    ):

        suspicious_patterns.append(
            "digit_letter_substitution"
        )

        score += 25

    if not suspicious_patterns:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No suspicious sender domain patterns detected",
            description=(
                "The sender domain does not contain suspicious "
                "phishing-like patterns."
            )
        )

    return FeatureResult(
        feature_id=FEATURE_ID,

        title="Suspicious sender domain detected",

        description=(
            "The sender domain contains phishing-like patterns "
            "commonly associated with malicious emails."
        ),

        detected=True,

        score=score,

        evidence={
            "sender_domain": sender_domain,
            "suspicious_patterns": suspicious_patterns,
        },

        minimum_verdict=minimum_verdict
    )


def has_suspicious_tld(
    domain: str
) -> bool:
    """
    Checks whether the domain ends with a suspicious top-level domain.
    """

    clean_domain = domain.lower().split(":")[0]

    if "." not in clean_domain:
        return False

    tld = clean_domain.split(".")[-1]

    return tld in SUSPICIOUS_TLDS


def has_digit_letter_substitution(
    domain: str
) -> bool:
    """
    Detects phishing-like digit substitutions inside domain words.

    Examples:
    amaz0n
    micr0soft
    paypa1
    g00gle
    """

    clean_domain = domain.lower()

    suspicious_pattern = (
        r"[a-z]+[01357][a-z]+"
    )

    return re.search(
        suspicious_pattern,
        clean_domain
    ) is not None