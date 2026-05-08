# This file analyzes suspicious recipient patterns in the email.

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "recipient_pattern"

MANY_RECIPIENTS_THRESHOLD = 5


def analyze_recipient_pattern(
    parsed_email: ParsedEmail,
    user_email: str | None
) -> FeatureResult:
    """
    Detects suspicious recipient patterns such as many recipients,
    hidden recipients, or missing direct targeting.
    """

    to_recipients = parsed_email.to or []
    cc_recipients = parsed_email.cc or []

    visible_recipients = (
        to_recipients + cc_recipients
    )

    visible_recipient_count = len(
        visible_recipients
    )

    user_email_found = check_if_user_email_exists(
        user_email=user_email,
        visible_recipients=visible_recipients
    )

    suspicious_patterns = []
    score = 0

    if visible_recipient_count >= MANY_RECIPIENTS_THRESHOLD:
        suspicious_patterns.append(
            "many_visible_recipients"
        )
        score += 10

    if user_email and not user_email_found:
        suspicious_patterns.append(
            "user_not_in_visible_recipients"
        )
        score += 10

    if contains_undisclosed_recipients(
        visible_recipients
    ):
        suspicious_patterns.append(
            "undisclosed_recipients"
        )
        score += 10

    if not suspicious_patterns:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No suspicious recipient patterns detected",
            description="The email recipient structure appears normal."
        )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Suspicious recipient pattern detected",
        description=(
            "The email contains recipient patterns commonly "
            "associated with bulk or suspicious email campaigns."
        ),
        detected=True,
        score=min(score, 25),
        evidence={
            "visible_recipient_count": visible_recipient_count,
            "to_recipients": to_recipients,
            "cc_recipients": cc_recipients,
            "user_email_found": user_email_found,
            "suspicious_patterns": suspicious_patterns,
        },
        minimum_verdict=None
    )


def check_if_user_email_exists(
    user_email: str | None,
    visible_recipients: list[str]
) -> bool:
    """
    Checks whether the user's email appears in visible recipients.
    """

    if not user_email:
        return False

    normalized_user_email = user_email.strip().lower()

    normalized_recipients = [
        recipient.strip().lower()
        for recipient in visible_recipients
    ]

    return normalized_user_email in normalized_recipients


def contains_undisclosed_recipients(
    visible_recipients: list[str]
) -> bool:
    """
    Checks whether visible recipients contain undisclosed recipient wording.
    """

    combined_recipients_text = " ".join(
        visible_recipients
    ).lower()

    return "undisclosed" in combined_recipients_text