# This file runs a simple parser demo on a sample .eml file.

from email_parsing.email_parser import parse_email_file


def main() -> None:
    """
    Parses a sample email file and prints the extracted information.
    """

    email_file_path = "../data/samples/sample_email.eml"
    parsed_email = parse_email_file(email_file_path)

    print("From name:", parsed_email.from_name)
    print("From email:", parsed_email.from_email)
    print("From domain:", parsed_email.from_domain)
    print("Reply-To:", parsed_email.reply_to)
    print("To:", parsed_email.to)
    print("Cc:", parsed_email.cc)
    print("Subject:", parsed_email.subject)
    print("URLs:", parsed_email.urls)
    print("Attachments:", parsed_email.attachments)
    print("Body preview:", parsed_email.body_text[:500])


if __name__ == "__main__":
    main()