# This file manually checks the email analysis API using a sample .eml file.

from pathlib import Path

import requests


API_URL = "http://127.0.0.1:8000/analyze-email"


def check_api() -> None:
    """
    Sends a sample raw MIME email to the backend API and prints the response.
    """

    project_root = Path(__file__).resolve().parents[2]
    email_file_path = project_root / "samples" / "sample_email.eml"

    raw_email = email_file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    response = requests.post(
        API_URL,
        json={
            "raw_email": raw_email,
            "user_name": "Zion",
            "user_email": "zion.maimon@gmail.com",
        },
        timeout=30
    )

    response.raise_for_status()

    print(response.json())


if __name__ == "__main__":
    check_api()