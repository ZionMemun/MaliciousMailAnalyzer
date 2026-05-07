# This file defines the data structures used to store parsed email information.

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttachmentInfo:
    """
    Stores basic metadata about an email attachment.
    """

    filename: str
    content_type: str | None = None
    size_bytes: int | None = None
    extension: str | None = None


@dataclass
class ParsedEmail:
    """
    Stores the normalized structure of a parsed email.
    """

    from_name: str | None = None
    from_email: str | None = None
    from_domain: str | None = None

    reply_to: str | None = None
    reply_to_domain: str | None = None

    to: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)

    subject: str | None = None

    body_text: str = ""
    body_html: str = ""

    urls: list[str] = field(default_factory=list)
    attachments: list[AttachmentInfo] = field(default_factory=list)

    headers: dict[str, Any] = field(default_factory=dict)