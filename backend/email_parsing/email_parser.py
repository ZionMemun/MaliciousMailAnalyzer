# This file coordinates the full email parsing process.

from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

from email_parsing.attachment_extractor import extract_attachments
from email_parsing.body_extractor import extract_email_body
from email_parsing.header_extractor import (
    extract_headers,
    extract_recipients,
    extract_reply_to,
    extract_sender,
    extract_subject,
)
from email_parsing.schemas import ParsedEmail
from email_parsing.url_extractor import extract_urls


def parse_email_file(file_path: str) -> ParsedEmail:
    """
    Parses a .eml file into a normalized ParsedEmail object.
    """

    message = load_email_message(file_path)

    return parse_email_message(message)


def parse_email_message(message: EmailMessage) -> ParsedEmail:
    """
    Parses an EmailMessage object into a normalized ParsedEmail object.
    """

    from_name, from_email, from_domain = extract_sender(message)
    reply_to, reply_to_domain = extract_reply_to(message)
    to_addresses, cc_addresses, bcc_addresses = extract_recipients(message)
    body_text, body_html = extract_email_body(message)

    return ParsedEmail(
        from_name=from_name,
        from_email=from_email,
        from_domain=from_domain,

        reply_to=reply_to,
        reply_to_domain=reply_to_domain,

        to=to_addresses,
        cc=cc_addresses,
        bcc=bcc_addresses,

        subject=extract_subject(message),

        body_text=body_text,
        body_html=body_html,

        urls=extract_urls(body_text, body_html),
        attachments=extract_attachments(message),

        headers=extract_headers(message)
    )


def load_email_message(file_path: str) -> EmailMessage:
    """
    Loads a raw .eml file into an EmailMessage object.
    """

    with open(file_path, "rb") as email_file:
        return BytesParser(policy=policy.default).parse(email_file)