"""Industrial-style workflow: query ontology and classify measurements."""

from pathlib import Path

from root_cause_analysis.classification import (
    classify_transformers,
    default_transformer_measurements,
)
from root_cause_analysis.querying import query_transformers_by_water_level


def main() -> None:
    ontology_path = Path("data/ontology/onto_pw.owl")
    high_water_transformers = query_transformers_by_water_level(
        ontology_path,
        minimum_water_level=100,
    )
    print("Transformers with high water content:")
    for transformer in high_water_transformers:
        print("-", transformer)

    result = classify_transformers(default_transformer_measurements())
    print("\nRule-based classifications")
    print("Failures:", result.failures)
    print("NonFailures:", result.non_failures)


if __name__ == "__main__":
    main()
