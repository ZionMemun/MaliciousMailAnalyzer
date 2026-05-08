# This file analyzes URLs found in the email for suspicious web-related patterns.

import ipaddress

from urllib.parse import urlparse

from email_parsing.schemas import ParsedEmail
from features.feature_result import (
    FeatureResult,
    create_not_detected_result
)


FEATURE_ID = "url_risk"


SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "shorturl.at",
}


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


def analyze_url_risk(
    parsed_email: ParsedEmail
) -> FeatureResult:
    """
    Analyzes URLs in the email and detects suspicious web URL patterns.
    """

    urls = parsed_email.urls or []

    if not urls:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No URLs detected",
            description="The email does not contain any URLs."
        )

    suspicious_urls = []

    for url in urls:

        if not is_web_url(url):
            continue

        url_analysis = analyze_single_url(
            url
        )

        if url_analysis["patterns"]:
            suspicious_urls.append(
                url_analysis
            )

    if not suspicious_urls:
        return create_not_detected_result(
            feature_id=FEATURE_ID,
            title="No suspicious URL patterns detected",
            description=(
                "The email contains URLs, but no suspicious URL "
                "patterns were detected."
            )
        )

    suspicious_patterns = extract_unique_patterns(
        suspicious_urls
    )

    minimum_verdict = determine_minimum_verdict(
        suspicious_patterns
    )

    return FeatureResult(
        feature_id=FEATURE_ID,

        title="Suspicious URL pattern detected",

        description=(
            "The email contains URLs with patterns commonly associated "
            "with suspicious or malicious messages."
        ),

        detected=True,

        score=0,

        evidence={
            "suspicious_patterns": suspicious_patterns,
            "suspicious_urls": suspicious_urls,
        },

        minimum_verdict=minimum_verdict
    )


def analyze_single_url(
    url: str
) -> dict:
    """
    Analyzes a single web URL and returns suspicious patterns found in it.
    """

    normalized_url = normalize_url(
        url
    )

    parsed_url = urlparse(
        normalized_url
    )

    domain = parsed_url.netloc.lower()

    patterns = []

    if is_ip_address(domain):
        patterns.append(
            "uses_ip_address"
        )

    if is_shortened_url(domain):
        patterns.append(
            "uses_url_shortener"
        )

    if has_suspicious_tld(domain):
        patterns.append(
            "suspicious_tld"
        )

    return {
        "url": url,
        "domain": domain,
        "patterns": patterns,
    }


def is_web_url(
    url: str
) -> bool:
    """
    Checks whether a URL points to a real web resource.
    """

    normalized_url = normalize_url(
        url
    )

    parsed_url = urlparse(
        normalized_url
    )

    scheme = parsed_url.scheme.lower()

    domain = parsed_url.netloc.lower()

    if scheme not in {
        "http",
        "https",
    }:
        return False

    if not domain:
        return False

    if "mailto:" in domain:
        return False

    if "@" in domain:
        return False

    return (
        is_valid_domain(domain)
        or is_ip_address(domain)
    )


def normalize_url(
    url: str
) -> str:
    """
    Normalizes URLs before parsing.
    """

    clean_url = url.strip()

    if clean_url.startswith("www."):
        return f"https://{clean_url}"

    return clean_url


def is_valid_domain(
    domain: str
) -> bool:
    """
    Checks whether a domain has a basic valid structure.
    """

    domain_without_port = domain.split(":")[0]

    if "." not in domain_without_port:
        return False

    domain_parts = domain_without_port.split(".")

    return all(
        part
        for part in domain_parts
    )


def extract_unique_patterns(
    suspicious_urls: list[dict]
) -> list[str]:
    """
    Extracts all unique suspicious patterns from analyzed URLs.
    """

    suspicious_patterns = set()

    for url_analysis in suspicious_urls:

        suspicious_patterns.update(
            url_analysis["patterns"]
        )

    return sorted(
        suspicious_patterns
    )


def is_ip_address(
    domain: str
) -> bool:
    """
    Checks whether the URL domain is an IP address.
    """

    if not domain:
        return False

    domain_without_port = domain.split(":")[0]

    try:
        ipaddress.ip_address(
            domain_without_port
        )

        return True

    except ValueError:
        return False


def is_shortened_url(
    domain: str
) -> bool:
    """
    Checks whether the URL domain belongs to a known URL shortener.
    """

    clean_domain = domain.replace(
        "www.",
        ""
    )

    return clean_domain in SHORTENER_DOMAINS


def has_suspicious_tld(
    domain: str
) -> bool:
    """
    Checks whether the URL domain ends with a suspicious top-level domain.
    """

    clean_domain = domain.split(":")[0]

    if "." not in clean_domain:
        return False

    tld = clean_domain.split(".")[-1]

    return tld in SUSPICIOUS_TLDS


def determine_minimum_verdict(
    suspicious_patterns: list[str]
) -> str | None:
    """
    Determines whether suspicious URL patterns should force
    a high-risk verdict.
    """

    if suspicious_patterns:
        return "high_risk"

    return None