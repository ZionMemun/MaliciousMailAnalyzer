# This file checks whether the email greeting is personalized with the user's name.

import re

from email_parsing.schemas import ParsedEmail
from features.feature_result import FeatureResult, create_not_detected_result


FEATURE_ID = "personalization"

GREETING_WORDS = [
    "hi",
    "hello",
    "dear",
]


def analyze_personalization(
    parsed_email: ParsedEmail,
    user_name: str | None
) -> FeatureResult:
    """
    Checks whether the email uses a greeting and whether it includes the user's name.
    """

    if not user_name:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Personalization not checked",
            description="No user name was provided for personalization analysis."
        )

    email_text = build_email_text(parsed_email)
    normalized_email_text = normalize_text(email_text)
    normalized_user_name = normalize_text(user_name)

    user_name_found = contains_user_name(
        normalized_email_text,
        normalized_user_name
    )

    greeting_found = find_greeting(
        normalized_email_text
    )

    greeting_contains_user_name = (
        greeting_found is not None
        and normalized_user_name in greeting_found
    )

    score = calculate_personalization_score(
        user_name_found=user_name_found,
        greeting_found=greeting_found,
        greeting_contains_user_name=greeting_contains_user_name
    )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Personalization analysis",
        description=(
            "Checks whether the email contains a greeting and whether "
            "the user's name appears in the message."
        ),
        detected=True,
        score=score,
        evidence={
            "user_name": user_name,
            "user_name_found": user_name_found,
            "greeting_found": greeting_found,
            "greeting_contains_user_name": greeting_contains_user_name,
        },
        minimum_verdict=None
    )


def build_email_text(parsed_email: ParsedEmail) -> str:
    """
    Combines the email subject and body into one searchable text.
    """

    subject = parsed_email.subject or ""
    body_text = parsed_email.body_text or ""

    return f"{subject} {body_text}"


def normalize_text(text: str) -> str:
    """
    Normalizes text for case-insensitive matching.
    """

    clean_text = text.lower()

    clean_text = re.sub(
        r"[^a-z\s]",
        " ",
        clean_text
    )

    clean_text = re.sub(
        r"\s+",
        " ",
        clean_text
    )

    return clean_text.strip()


def contains_user_name(
    normalized_email_text: str,
    normalized_user_name: str
) -> bool:
    """
    Checks whether the normalized user name appears as a full word sequence.
    """

    if not normalized_user_name:
        return False

    pattern = rf"\b{re.escape(normalized_user_name)}\b"

    return re.search(
        pattern,
        normalized_email_text
    ) is not None


def find_greeting(
    normalized_email_text: str
) -> str | None:
    """
    Finds the first greeting phrase in the email text.
    """

    greeting_pattern = (
        r"\b(hi|hello|dear)\s+([a-z]+(?:\s+[a-z]+){0,3})"
    )

    match = re.search(
        greeting_pattern,
        normalized_email_text
    )

    if not match:
        return None

    return match.group(0)


def calculate_personalization_score(
    user_name_found: bool,
    greeting_found: str | None,
    greeting_contains_user_name: bool
) -> int:
    """
    Calculates a risk score adjustment based on personalization signals.
    """

    score = 0

    if user_name_found:
        score -= 15

    if greeting_found and not greeting_contains_user_name:
        score += 10

    return score