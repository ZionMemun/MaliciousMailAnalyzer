# This file extracts plain text and HTML content from an email body.

from email.message import EmailMessage

from bs4 import BeautifulSoup


def extract_email_body(message: EmailMessage) -> tuple[str, str]:
    """
    Extracts plain text and HTML body content from an email message.
    """

    text_parts: list[str] = []
    html_parts: list[str] = []

    if message.is_multipart():
        _extract_body_from_multipart_message(message, text_parts, html_parts)
    else:
        _extract_body_from_single_part_message(message, text_parts, html_parts)

    body_text = "\n".join(part.strip() for part in text_parts if part.strip())
    body_html = "\n".join(part.strip() for part in html_parts if part.strip())

    return body_text, body_html


def convert_html_to_text(html_content: str) -> str:
    """
    Converts HTML content into readable plain text.
    """

    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _extract_body_from_multipart_message(
    message: EmailMessage,
    text_parts: list[str],
    html_parts: list[str]
) -> None:
    """
    Extracts body parts from a multipart email message.
    """

    for part in message.walk():
        content_type = part.get_content_type()
        content_disposition = part.get_content_disposition()

        if content_disposition == "attachment":
            continue

        if content_type == "text/plain":
            text_parts.append(_safe_get_content(part))

        elif content_type == "text/html":
            html_content = _safe_get_content(part)
            html_parts.append(html_content)

            if not text_parts:
                text_parts.append(convert_html_to_text(html_content))


def _extract_body_from_single_part_message(
    message: EmailMessage,
    text_parts: list[str],
    html_parts: list[str]
) -> None:
    """
    Extracts body content from a non-multipart email message.
    """

    content_type = message.get_content_type()
    content = _safe_get_content(message)

    if content_type == "text/plain":
        text_parts.append(content)

    elif content_type == "text/html":
        html_parts.append(content)
        text_parts.append(convert_html_to_text(content))


def _safe_get_content(part: EmailMessage) -> str:
    """
    Safely extracts text content from an email part.
    """

    try:
        content = part.get_content()
        return content if isinstance(content, str) else ""

    except Exception:
        return ""