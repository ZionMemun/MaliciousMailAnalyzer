# This file extracts URLs from plain text and HTML email content.

import re


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"]+|www\.[^\s<>\"]+",
    re.IGNORECASE
)


def extract_urls(body_text: str, body_html: str) -> list[str]:
    """
    Extracts URLs from both plain text and HTML content.
    """

    text_urls = extract_urls_from_text(body_text)
    html_urls = extract_urls_from_text(body_html)

    return merge_unique_urls(text_urls, html_urls)


def extract_urls_from_text(text: str) -> list[str]:
    """
    Extracts URLs from a text string.
    """

    if not text:
        return []

    urls = URL_PATTERN.findall(text)

    return clean_and_deduplicate_urls(urls)


def clean_and_deduplicate_urls(urls: list[str]) -> list[str]:
    """
    Cleans URLs and removes duplicates while preserving order.
    """

    seen_urls = set()
    unique_urls = []

    for url in urls:
        cleaned_url = clean_url(url)

        if cleaned_url and cleaned_url not in seen_urls:
            seen_urls.add(cleaned_url)
            unique_urls.append(cleaned_url)

    return unique_urls


def clean_url(url: str) -> str:
    """
    Removes common trailing characters from a URL.
    """

    return url.strip().rstrip(".,);]\"'")


def merge_unique_urls(*url_lists: list[str]) -> list[str]:
    """
    Merges multiple URL lists while removing duplicates.
    """

    seen_urls = set()
    merged_urls = []

    for url_list in url_lists:
        for url in url_list:
            if url not in seen_urls:
                seen_urls.add(url)
                merged_urls.append(url)

    return merged_urls