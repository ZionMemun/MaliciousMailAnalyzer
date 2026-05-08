# This file defines the API request schemas for email analysis.

from pydantic import BaseModel


class AnalyzeEmailRequest(BaseModel):
    """
    Represents the request body sent from the Gmail Add-on.
    """

    raw_email: str

    user_name: str | None = None

    user_email: str | None = None