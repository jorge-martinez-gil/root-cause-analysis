"""Legacy script: query transformers with high water content."""

from pathlib import Path

from root_cause_analysis.querying import query_transformers_by_water_level


def main() -> None:
    candidates = [
        Path("data/ontology/onto_pw.owl"),
        Path("onto_pw"),
    ]
    ontology_path = next((path for path in candidates if path.exists()), candidates[0])
    for transformer_iri in query_transformers_by_water_level(ontology_path):
        print(transformer_iri)


if __name__ == "__main__":
    main()
