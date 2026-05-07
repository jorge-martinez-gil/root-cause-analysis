"""Minimal quickstart example for repository users."""

from root_cause_analysis.classification import (
    classify_transformers,
    default_transformer_measurements,
)


def main() -> None:
    result = classify_transformers(default_transformer_measurements())
    print("Failures:", result.failures)
    print("NonFailures:", result.non_failures)


if __name__ == "__main__":
    main()
