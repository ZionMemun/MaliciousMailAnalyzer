# This file checks whether the Reply-To address appears unrelated to the sender address.

from email_parsing.schemas import ParsedEmail
from features.feature_result import FeatureResult, create_not_detected_result


FEATURE_ID = "reply_to_domain_mismatch"


def analyze_reply_to_mismatch(parsed_email: ParsedEmail) -> FeatureResult:
    """
    Checks whether the Reply-To address appears unrelated to the sender address.
    """

    sender_email = parsed_email.from_email
    sender_domain = parsed_email.from_domain

    reply_to_email = parsed_email.reply_to
    reply_to_domain = parsed_email.reply_to_domain

    if not reply_to_email or not reply_to_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No Reply-To mismatch detected",
            description="The email does not contain a separate Reply-To address."
        )

    if not sender_email or not sender_domain:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Sender information unavailable",
            description="The sender email or sender domain could not be extracted."
        )

    if addresses_appear_related(
        sender_email=sender_email,
        sender_domain=sender_domain,
        reply_to_email=reply_to_email,
        reply_to_domain=reply_to_domain
    ):
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Reply-To address appears related to sender",
            description="The Reply-To address appears related to the sender address."
        )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Reply-To mismatch detected",
        description=(
            "The email uses a Reply-To address that appears unrelated "
            "to the sender address."
        ),
        detected=True,
        score=0,
        evidence={
            "sender_email": sender_email,
            "sender_domain": sender_domain,
            "reply_to": reply_to_email,
            "reply_to_domain": reply_to_domain,
        },
        minimum_verdict="suspicious"
    )


def addresses_appear_related(
    sender_email: str,
    sender_domain: str,
    reply_to_email: str,
    reply_to_domain: str
) -> bool:
    """
    Checks whether sender and Reply-To appear related using full emails and domains.
    """

    sender_email = sender_email.lower().strip()
    sender_domain = sender_domain.lower().strip()

    reply_to_email = reply_to_email.lower().strip()
    reply_to_domain = reply_to_domain.lower().strip()

    if sender_domain == reply_to_domain:
        return True

    sender_core_token = extract_core_domain_token(sender_domain)
    reply_to_core_token = extract_core_domain_token(reply_to_domain)

    if not sender_core_token or not reply_to_core_token:
        return False

    return (
        sender_core_token in reply_to_email
        or reply_to_core_token in sender_email
        or sender_core_token in reply_to_domain
        or reply_to_core_token in sender_domain
    )


def extract_core_domain_token(domain: str) -> str | None:
    """
    Extracts the main domain token before the suffix.
    """

    domain_parts = domain.split(".")

    if len(domain_parts) < 2:
        return None

    return domain_parts[-2]