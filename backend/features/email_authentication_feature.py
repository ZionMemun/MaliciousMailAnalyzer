# This file analyzes SPF, DKIM, and DMARC authentication results from email headers.

import re

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "email_authentication"


AUTHENTICATION_CHECKS = [
    "spf",
    "dkim",
    "dmarc",
]


def analyze_email_authentication(
    parsed_email: ParsedEmail
) -> FeatureResult:
    """
    Analyzes SPF, DKIM, and DMARC authentication results from email headers.
    """

    authentication_text = extract_authentication_text(
        parsed_email.headers
    )

    if not authentication_text:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Email authentication results unavailable",
            description=(
                "The email does not contain authentication results "
                "for SPF, DKIM, or DMARC."
            )
        )

    authentication_results = extract_authentication_results(
        authentication_text
    )

    failed_checks = find_failed_authentication_checks(
        authentication_results
    )

    if not failed_checks:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Email authentication checks passed",
            description="No SPF, DKIM, or DMARC authentication failures were detected."
        )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Email authentication failure detected",
        description=(
            "The email contains failed authentication checks such as "
            "SPF, DKIM, or DMARC."
        ),
        detected=True,
        score=0,
        evidence={
            "authentication_results": authentication_results,
            "failed_checks": failed_checks,
        },
        minimum_verdict="high_risk"
    )


def extract_authentication_text(
    headers: dict
) -> str:
    """
    Extracts authentication-related header values into one searchable text.
    """

    authentication_header_names = {
        "authentication-results",
        "arc-authentication-results",
        "received-spf",
    }

    authentication_values = []

    for header_name, header_value in headers.items():

        normalized_header_name = header_name.lower()

        if normalized_header_name in authentication_header_names:
            authentication_values.append(
                str(header_value)
            )

    return " ".join(authentication_values).lower()


def extract_authentication_results(
    authentication_text: str
) -> dict[str, str]:
    """
    Extracts SPF, DKIM, and DMARC results from authentication header text.
    """

    results = {}

    for check_name in AUTHENTICATION_CHECKS:

        pattern = rf"\b{check_name}\s*=\s*([a-z]+)"

        match = re.search(
            pattern,
            authentication_text
        )

        if match:
            results[check_name] = match.group(1)

    return results


def find_failed_authentication_checks(
    authentication_results: dict[str, str]
) -> list[str]:
    """
    Finds failed SPF, DKIM, or DMARC authentication checks.
    """

    failed_checks = []

    for check_name, result in authentication_results.items():

        if result in {
            "fail",
            "softfail",
            "neutral",
        }:
            failed_checks.append(
                check_name
            )

    return failed_checks