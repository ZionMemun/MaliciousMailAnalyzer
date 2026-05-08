# This file analyzes email attachments and assigns risk based on file extensions.

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "attachment_risk"


HIGH_RISK_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".vbs",
    ".ps1",
    ".scr",
}

SCRIPT_EXTENSIONS = {
    ".js",
    ".jse",
    ".wsf",
}

MACRO_EXTENSIONS = {
    ".docm",
    ".xlsm",
    ".pptm",
}

ARCHIVE_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
}


def analyze_attachment_risk(
    parsed_email: ParsedEmail
) -> FeatureResult:
    """
    Analyzes email attachments and assigns risk based on file extensions.
    """

    attachments = parsed_email.attachments or []

    if not attachments:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No attachments detected",
            description="The email does not contain any attachments."
        )

    risky_attachments = []

    for attachment in attachments:
        attachment_risk = analyze_single_attachment(
            filename=attachment.filename,
            extension=attachment.extension
        )

        if attachment_risk["risk_category"] is not None:
            risky_attachments.append(attachment_risk)

    if not risky_attachments:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No risky attachments detected",
            description="The email contains attachments, but none have risky file extensions."
        )

    score = calculate_attachment_score(
        risky_attachments
    )

    return FeatureResult(
        feature_id=FEATURE_ID,
        title="Risky attachment detected",
        description=(
            "The email contains one or more attachments with file extensions "
            "commonly used in malicious email campaigns."
        ),
        detected=True,
        score=score,
        evidence={
            "attachment_count": len(attachments),
            "risky_attachments": risky_attachments,
        },
        minimum_verdict=None
    )


def analyze_single_attachment(
    filename: str,
    extension: str | None
) -> dict:
    """
    Analyzes a single attachment and classifies its extension risk.
    """

    normalized_extension = normalize_extension(
        extension
    )

    risk_category = get_risk_category(
        normalized_extension
    )

    return {
        "filename": filename,
        "extension": normalized_extension,
        "risk_category": risk_category,
    }


def normalize_extension(
    extension: str | None
) -> str | None:
    """
    Normalizes attachment extension to lowercase format.
    """

    if not extension:
        return None

    return extension.lower().strip()


def get_risk_category(
    extension: str | None
) -> str | None:
    """
    Maps a file extension to a risk category.
    """

    if extension in HIGH_RISK_EXTENSIONS:
        return "executable_or_system_script"

    if extension in SCRIPT_EXTENSIONS:
        return "script_file"

    if extension in MACRO_EXTENSIONS:
        return "macro_enabled_document"

    if extension in ARCHIVE_EXTENSIONS:
        return "archive_file"

    return None


def calculate_attachment_score(
    risky_attachments: list[dict]
) -> int:
    """
    Calculates attachment risk score based on the riskiest attachment category.
    """

    risk_scores = [
        get_category_score(
            attachment["risk_category"]
        )
        for attachment in risky_attachments
    ]

    return max(risk_scores)


def get_category_score(
    risk_category: str | None
) -> int:
    """
    Returns the score associated with an attachment risk category.
    """

    category_scores = {
        "executable_or_system_script": 60,
        "script_file": 45,
        "macro_enabled_document": 35,
        "archive_file": 20,
    }

    return category_scores.get(
        risk_category,
        0
    )