# This file detects suspicious words in the email subject and body.

import re
from collections import defaultdict

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "suspicious_words"

SUSPICIOUS_WORD_GROUPS = {

    "credential_or_account": [
        "account",
        "security",
        "customer",
        "bank",
        "transaction",
        "private",
        "password",
        "credentials",
    ],

    "money_or_scam": [
        "money",
        "investment",
        "investing",
        "stocks",
        "securities",
        "funds",
        "fund",
        "mortgage",
        "loan",
        "cash",
        "deposit",
        "income",
        "million",
        "thousand",
        "dollars",
        "lottery",
        "winning",
        "guaranteed",
        "guarantee",
    ],

    "marketing_or_spam": [
        "free",
        "offer",
        "offers",
        "marketing",
        "advertisement",
        "advertising",
        "promotional",
        "sales",
        "shipping",
        "unsubscribe",
        "buy",
        "cheap",
        "lowest",
        "instant",
        "approved",
    ],

    "medical_spam": [
        "pills",
        "viagra",
        "prescription",
        "meds",
        "drugs",
        "tablets",
        "medications",
        "medical",
        "health",
        "weight",
    ],

    "call_to_action": [
        "click",
        "link",
        "act",
        "visit",
        "receive",
        "remove",
        "reply",
        "login",
        "verify",
        "confirm",
        "update",
        "open",
        "download",
        "submit",
    ],
}


GROUP_COUNT_TO_SCORE = {
    1: 10,
    2: 20,
    3: 30,
    4: 40,
    5: 40,
}


def analyze_suspicious_words(parsed_email: ParsedEmail) -> FeatureResult:
    """
    Detects suspicious words in the email subject and body.
    """

    email_text = build_email_text(parsed_email)

    normalized_words = tokenize_text(email_text)

    matched_words_by_group = find_suspicious_words(
        normalized_words
    )

    if not matched_words_by_group:

        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No suspicious words detected",
            description=(
                "The email does not contain known suspicious word indicators."
            )
        )

    matched_group_count = len(
        matched_words_by_group
    )

    score = calculate_suspicious_words_score(
        matched_group_count
    )

    return FeatureResult(
        feature_id=FEATURE_ID,

        title="Suspicious words detected",

        description=(
            "The email contains words commonly associated "
            "with suspicious or malicious emails."
        ),

        detected=True,

        score=score,

        evidence={
            "matched_words_by_group": dict(
                matched_words_by_group
            ),

            "matched_group_count": matched_group_count,
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


def tokenize_text(text: str) -> set[str]:
    """
    Converts text into a set of normalized lowercase words.
    """

    clean_text = text.lower()

    clean_text = re.sub(
        r"[^a-z\s]",
        " ",
        clean_text
    )

    words = clean_text.split()

    return set(words)


def find_suspicious_words(words: set[str]) -> dict[str, list[str]]:
    """
    Finds suspicious words grouped by threat category.
    """

    matched_words_by_group = defaultdict(list)

    for (
        group_name,
        suspicious_words
    ) in SUSPICIOUS_WORD_GROUPS.items():

        for suspicious_word in suspicious_words:

            if suspicious_word in words:

                matched_words_by_group[
                    group_name
                ].append(suspicious_word)

    return matched_words_by_group


def calculate_suspicious_words_score(matched_group_count: int) -> int:
    """
    Calculates the suspicious words score based only
    on the number of matched suspicious word groups.
    """

    return GROUP_COUNT_TO_SCORE.get(
        matched_group_count,
        15
    )