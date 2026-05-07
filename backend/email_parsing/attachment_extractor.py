# This file extracts metadata about attachments from an email.

from pathlib import Path
from email.message import EmailMessage

from email_parsing.schemas import AttachmentInfo


def extract_attachments(message: EmailMessage) -> list[AttachmentInfo]:
    """
    Extracts metadata for all attachments in an email message.
    """

    attachments: list[AttachmentInfo] = []

    for part in message.walk():
        filename = part.get_filename()

        if not filename:
            continue

        attachment = AttachmentInfo(
            filename=filename,
            content_type=part.get_content_type(),
            size_bytes=get_attachment_size(part),
            extension=get_file_extension(filename)
        )

        attachments.append(attachment)

    return attachments


def get_attachment_size(part: EmailMessage) -> int:
    """
    Calculates the size of an attachment payload in bytes.
    """

    payload = part.get_payload(decode=True)

    if not payload:
        return 0

    return len(payload)


def get_file_extension(filename: str) -> str | None:
    """
    Extracts the lowercase file extension from a filename.
    """

    extension = Path(filename).suffix.lower()

    return extension if extension else None