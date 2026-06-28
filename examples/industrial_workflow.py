"""Industrial workflow: build a knowledge graph, diagnose, explain and query.

Reproduces the case-study pipeline end to end:

1. Build an RDF knowledge graph from measurements and materialise inferred
   diagnoses with PROV-O provenance.
2. Print explanation traces for each asset.
3. Query the knowledge graph with SPARQL for inferred faults and their evidence.
4. Screen assets by a measured parameter with SPARQL.

To also write ``diagnosis_report.md`` and ``knowledge_graph.ttl`` to disk, run::

    rca-diagnose --output-dir ./rca_outputs
"""

from root_cause_analysis import (
    build_diagnosed_graph,
    sample_transformer_measurements,
    screen_assets,
)

PROV_QUERY = """
PREFIX : <http://test.org/onto-pw#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT ?asset ?status ?fault ?rule
WHERE {
  ?d a :Diagnosis ; :ofAsset ?asset ; :hasStatus ?status ; :derivedFromRule ?r .
  ?r rdfs:label ?rule .
  OPTIONAL { ?d :indicatesFault ?f . ?f :faultCode ?fault . }
}
ORDER BY ?asset
"""


def _local(uri: object) -> str:
    return str(uri).split("#")[-1]


def main() -> None:
    measurements = sample_transformer_measurements()
    graph, diagnoses = build_diagnosed_graph(measurements)
    print(f"Knowledge graph: {len(graph)} triples\n")

    print("=== Explanation traces ===")
    for d in diagnoses:
        print(d.explanation())
        print()

    print("=== Inferred faults (SPARQL over the knowledge graph) ===")
    seen = set()
    for row in graph.query(PROV_QUERY):
        asset, status, fault = _local(row[0]), str(row[1]), row[2]
        key = (asset, str(fault))
        if key in seen:
            continue
        seen.add(key)
        fault_str = str(fault) if fault is not None else "-"
        print(f"{asset}: status={status}, IEC fault={fault_str}")

    print("\n=== SPARQL screening: assets with Health index < 80 ===")
    for label, value in screen_assets(
        measurements, parameter="Health index", operator="<", threshold=80.0
    ):
        print(f"{label}: Health index = {value:g}")


if __name__ == "__main__":
    main()
