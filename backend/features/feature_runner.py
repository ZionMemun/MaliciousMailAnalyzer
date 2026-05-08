# This file runs all email security features on a parsed email.

from email_parsing.schemas import ParsedEmail
from features.feature_result import FeatureResult
from features.personalization_feature import analyze_personalization
from features.recipient_pattern_feature import analyze_recipient_pattern
from features.reply_to_mismatch_feature import analyze_reply_to_mismatch
from features.suspicious_words_feature import analyze_suspicious_words
from features.url_risk_feature import analyze_url_risk
from features.attachment_risk_feature import analyze_attachment_risk
from features.email_authentication_feature import analyze_email_authentication
from features.sender_domain_feature import analyze_sender_domain


def run_all_features(
    parsed_email: ParsedEmail,
    user_name: str | None = None,
    user_email: str | None = None
) -> list[FeatureResult]:
    """
    Runs all available email security features and returns their results.
    """

    feature_results = [
        analyze_suspicious_words(parsed_email),

        analyze_personalization(
            parsed_email=parsed_email,
            user_name=user_name
        ),

        analyze_reply_to_mismatch(parsed_email),

        analyze_recipient_pattern(
            parsed_email=parsed_email,
            user_email=user_email
        ),

        analyze_url_risk(parsed_email),

        analyze_attachment_risk(parsed_email),

        analyze_email_authentication(parsed_email),

        analyze_sender_domain(parsed_email),

    ]

    return feature_results