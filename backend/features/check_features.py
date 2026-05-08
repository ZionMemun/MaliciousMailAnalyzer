# This file manually checks the feature extraction pipeline on a sample parsed email.

from pathlib import Path

from email_parsing.email_parser import parse_email_file
from features.feature_runner import run_all_features
from scoring.email_scorer import calculate_email_verdict


def check_features() -> None:
    """
    Parses a sample email and prints all extracted feature results.
    """

    project_root = Path(__file__).resolve().parents[2]

    email_file_path = (
        project_root
        / "samples"
        / "sample_email.eml"
    )

    parsed_email = parse_email_file(
        str(email_file_path)
    )

    feature_results = run_all_features(
        parsed_email=parsed_email,

        user_name="Zion",

        user_email="zion.maimon@gmail.com"
    )

    final_verdict = calculate_email_verdict(
        feature_results
    )

    print("\n========== FEATURE RESULTS ==========\n")

    for result in feature_results:

        print("Feature ID:", result.feature_id)

        print("Title:", result.title)

        print("Detected:", result.detected)

        print("Score:", result.score)

        print("Minimum verdict:", result.minimum_verdict)

        print("Description:", result.description)

        print("Evidence:", result.evidence)

        print("-" * 50)

    print("\n========== FINAL ANALYSIS ==========\n")

    print("Final verdict:", final_verdict.verdict)

    print("Regular score:", final_verdict.regular_score)

    print("\nDetected features:")

    for feature in final_verdict.detected_features:
        print("-", feature.feature_id)

    print("\nHard signals:")

    if final_verdict.hard_signals:

        for signal in final_verdict.hard_signals:
            print(
                "-",
                signal.feature_id,
                "=>",
                signal.minimum_verdict
            )

    else:
        print("None")

    print("\n====================================\n")


if __name__ == "__main__":
    check_features()