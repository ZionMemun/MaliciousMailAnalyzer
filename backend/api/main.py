# This file exposes the FastAPI backend used by the Gmail Add-on.

from fastapi import FastAPI

from api.schemas import AnalyzeEmailRequest
from email_parsing.email_parser import parse_email_string
from features.feature_runner import run_all_features
from scoring.email_scorer import calculate_email_verdict

app = FastAPI(
    title="Malicious Mail Analyzer API"
)

@app.get("/")
def health_check() -> dict:
    """
    Checks whether the backend service is running.
    """

    return {
        "status": "running"
    }


@app.post("/analyze-email")
def analyze_email(
    request: AnalyzeEmailRequest
) -> dict:
    """
    Analyzes a raw MIME email and returns a maliciousness verdict.
    """

    parsed_email = parse_email_string(
        request.raw_email
    )

    feature_results = run_all_features(
        parsed_email=parsed_email,
        user_name=request.user_name,
        user_email=request.user_email
    )

    final_verdict = calculate_email_verdict(
        feature_results
    )

    return {
        "verdict": final_verdict.verdict,
        "regular_score": final_verdict.regular_score,

        "hard_signals": [
            {
                "feature_id": feature.feature_id,
                "title": feature.title,
                "description": feature.description,
                "evidence": feature.evidence,
                "minimum_verdict": feature.minimum_verdict,
            }
            for feature in final_verdict.hard_signals
        ],

        "detected_features": [
            {
                "feature_id": feature.feature_id,
                "title": feature.title,
                "score": feature.score,
                "description": feature.description,
                "evidence": feature.evidence,
                "minimum_verdict": feature.minimum_verdict,
            }
            for feature in final_verdict.detected_features
        ],
    }