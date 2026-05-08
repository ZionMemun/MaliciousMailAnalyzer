# This file checks whether the Reply-To domain is different from the sender domain.

from email_parsing.schemas import ParsedEmail
from features.feature_result import FeatureResult, create_not_detected_result


FEATURE_ID = "reply_to_domain_mismatch"


def analyze_reply_to_mismatch(
    parsed_email: ParsedEmail
) -> FeatureResult:
    """
    Checks whether the Reply-To domain is different from the sender domain.
    """

    sender_domain = parsed_email.from_domain
    reply_to_domain = parsed_email.reply_to_domain

    if not reply_to_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No Reply-To domain mismatch detected",
            description="The email does not contain a separate Reply-To address."
        )

    if not sender_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Sender domain unavailable",
            description="The sender domain could not be extracted."
        )

    if sender_domain == reply_to_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Reply-To domain matches sender domain",
            description="The Reply-To domain matches the sender domain."
        )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Reply-To domain mismatch detected",
        description=(
            "The email uses a Reply-To domain that is different from "
            "the sender domain."
        ),
        detected=True,
        score=0,
        evidence={
            "sender_email": parsed_email.from_email,
            "sender_domain": sender_domain,
            "reply_to": parsed_email.reply_to,
            "reply_to_domain": reply_to_domain,
        },
        minimum_verdict="high_risk"
    )