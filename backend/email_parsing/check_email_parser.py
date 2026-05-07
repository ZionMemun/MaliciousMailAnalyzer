# This file manually checks the email parser using a sample .eml file.

from pathlib import Path

from email_parsing.email_parser import parse_email_file


def check_email_parser() -> None:
    """
    Parses a sample email and prints the extracted fields.
    """

    project_root = Path(__file__).resolve().parents[2]

    email_file_path = project_root / "samples" / "sample_email.eml"

    parsed_email = parse_email_file(str(email_file_path))

    print("\n========== PARSED EMAIL ==========\n")

    print("From name:", parsed_email.from_name)
    print("From email:", parsed_email.from_email)
    print("From domain:", parsed_email.from_domain)

    print("\nReply-To:", parsed_email.reply_to)

    print("\nTo:", parsed_email.to)
    print("Cc:", parsed_email.cc)

    print("\nSubject:", parsed_email.subject)

    print("\nURLs:")
    for url in parsed_email.urls:
        print("-", url)

    print("\nAttachments:")
    for attachment in parsed_email.attachments:
        print("-", attachment)

    print("\nBody text:")
    print(parsed_email.body_text)

    print("\nBody HTML preview:")
    print(parsed_email.body_html[:3000])


if __name__ == "__main__":
    check_email_parser()