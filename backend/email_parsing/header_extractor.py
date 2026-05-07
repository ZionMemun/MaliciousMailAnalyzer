# This file extracts sender, recipient, subject, and header information from an email.

from email.message import EmailMessage
from email.utils import getaddresses, parseaddr


def extract_sender(message: EmailMessage) -> tuple[str | None, str | None, str | None]:
    """
    Extracts the sender display name, email address, and domain.
    """

    sender_name, sender_email = parse_single_email_address(message.get("From", ""))
    sender_domain = extract_domain(sender_email)

    return sender_name, sender_email, sender_domain


def extract_reply_to(message: EmailMessage) -> tuple[str | None, str | None]:
    """
    Extracts the Reply-To email address and domain.
    """

    _, reply_to_email = parse_single_email_address(message.get("Reply-To", ""))
    reply_to_domain = extract_domain(reply_to_email)

    return reply_to_email, reply_to_domain


def extract_recipients(message: EmailMessage) -> tuple[list[str], list[str], list[str]]:
    """
    Extracts To, Cc, and Bcc recipient email addresses.
    """

    to_addresses = parse_multiple_email_addresses(message.get("To", ""))
    cc_addresses = parse_multiple_email_addresses(message.get("Cc", ""))
    bcc_addresses = parse_multiple_email_addresses(message.get("Bcc", ""))

    return to_addresses, cc_addresses, bcc_addresses


def extract_subject(message: EmailMessage) -> str:
    """
    Extracts the email subject.
    """

    return message.get("Subject", "") or ""


def extract_headers(message: EmailMessage) -> dict[str, str]:
    """
    Extracts all email headers into a dictionary.
    """

    return dict(message.items())


def parse_single_email_address(raw_address: str) -> tuple[str | None, str | None]:
    """
    Parses a single email address into display name and email address.
    """

    display_name, email_address = parseaddr(raw_address)

    clean_display_name = display_name.strip() if display_name else None
    clean_email_address = email_address.lower().strip() if email_address else None

    return clean_display_name, clean_email_address


def parse_multiple_email_addresses(raw_addresses: str) -> list[str]:
    """
    Parses a recipient header into a list of email addresses.
    """

    parsed_addresses = getaddresses([raw_addresses])

    return [
        email_address.lower().strip()
        for _, email_address in parsed_addresses
        if email_address
    ]


def extract_domain(email_address: str | None) -> str | None:
    """
    Extracts the domain part from an email address.
    """

    if not email_address or "@" not in email_address:
        return None

    return email_address.split("@")[-1].lower().strip()