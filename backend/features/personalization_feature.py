# This file checks whether the email greeting is personalized with one of the user's names.

import re

from email_parsing.schemas import ParsedEmail
from features.feature_result import FeatureResult, create_not_detected_result


FEATURE_ID = "personalization"

GREETING_WORDS = [
    "hi",
    "hello",
    "hey",
    "dear",
]


def analyze_personalization(
    parsed_email: ParsedEmail,
    user_name: str | None
) -> FeatureResult:
    """
    Checks whether the email uses a greeting and whether it includes one of the user's names.
    """

    if not user_name:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="Personalization not checked",
            description="No user name was provided for personalization analysis."
        )

    user_names = parse_user_names(user_name)

    email_text = build_email_text(parsed_email)
    normalized_email_text = normalize_text(email_text)
    normalized_user_names = [
        normalize_text(name)
        for name in user_names
        if normalize_text(name)
    ]

    matched_user_name = find_matching_user_name(
        normalized_email_text=normalized_email_text,
        normalized_user_names=normalized_user_names
    )

    greeting_found = find_greeting(
        normalized_email_text
    )

    greeting_contains_user_name = (
        greeting_found is not None
        and matched_user_name is not None
        and matched_user_name in greeting_found
    )

    score = calculate_personalization_score(
        matched_user_name=matched_user_name,
        greeting_found=greeting_found,
        greeting_contains_user_name=greeting_contains_user_name
    )

    title, description = build_personalization_message(
        matched_user_name=matched_user_name,
        greeting_found=greeting_found
    )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title=title,
        description=description,
        detected=True,
        score=score,
        evidence={
            "provided_user_names": user_names,
            "matched_user_name": matched_user_name,
            "user_name_found": matched_user_name is not None,
            "greeting_found": greeting_found,
            "greeting_contains_user_name": greeting_contains_user_name,
        },
        minimum_verdict=None
    )


def parse_user_names(user_name: str) -> list[str]:
    """
    Parses one or more user names separated by commas.
    """

    return [
        name.strip()
        for name in user_name.split(",")
        if name.strip()
    ]


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
        r"[^a-zא-ת\s]",
        " ",
        clean_text
    )

    clean_text = re.sub(
        r"\s+",
        " ",
        clean_text
    )

    return clean_text.strip()


def find_matching_user_name(
    normalized_email_text: str,
    normalized_user_names: list[str]
) -> str | None:
    """
    Finds the first provided user name that appears in the email text.
    """

    for normalized_user_name in normalized_user_names:
        if contains_user_name(
            normalized_email_text=normalized_email_text,
            normalized_user_name=normalized_user_name
        ):
            return normalized_user_name

    return None


def contains_user_name(
    normalized_email_text: str,
    normalized_user_name: str
) -> bool:
    """
    Checks whether a user name appears directly or inside a greeting target word.
    """

    if not normalized_user_name:
        return False

    direct_pattern = rf"\b{re.escape(normalized_user_name)}\b"

    if re.search(direct_pattern, normalized_email_text):
        return True

    greeting_target_pattern = r"\b(hi|hello|hey|dear)\s+([a-zא-ת]+)"

    greeting_matches = re.findall(
        greeting_target_pattern,
        normalized_email_text
    )

    for _, greeting_target in greeting_matches:
        if normalized_user_name in greeting_target:
            return True

    return False


def find_greeting(
    normalized_email_text: str
) -> str | None:
    """
    Finds the first greeting phrase in the email text.
    """

    greeting_pattern = (
        r"\b(hi|hello|hey|dear)\s+([a-zא-ת]+(?:\s+[a-zא-ת]+){0,3})"
    )

    match = re.search(
        greeting_pattern,
        normalized_email_text
    )

    if not match:
        return None

    return match.group(0)


def calculate_personalization_score(
    matched_user_name: str | None,
    greeting_found: str | None,
    greeting_contains_user_name: bool
) -> int:
    """
    Calculates a risk score adjustment based on personalization signals.
    """

    score = 0

    if matched_user_name:
        score -= 15

    if greeting_found and not greeting_contains_user_name:
        score += 10

    return score


def build_personalization_message(
    matched_user_name: str | None,
    greeting_found: str | None
) -> tuple[str, str]:
    """
    Builds a contextual title and description for the personalization result.
    """

    if matched_user_name:
        return (
            "Personalized greeting detected",
            (
                "The email contains one of the provided user names, "
                "which lowers the risk because the message appears more personally addressed."
            )
        )

    if greeting_found:
        return (
            "Generic greeting detected",
            (
                "The email contains a greeting, but none of the provided user names "
                "appears after it. This may indicate a less personalized or bulk message."
            )
        )

    return (
        "No personalization signal detected",
        (
            "The email does not contain a clear greeting or any of the provided user names."
        )
    )
