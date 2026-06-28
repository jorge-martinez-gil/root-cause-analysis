# Usage Guide

## Installation

```bash
python -m pip install -e .
```

## Command line

```bash
# Full explainable diagnosis (sample fleet); writes report + knowledge graph
rca-diagnose --output-dir ./rca_outputs

# Diagnose your own CSV (one row per asset)
rca-diagnose --input my_transformers.csv --output-dir ./out --format markdown

# SPARQL screening by any measured parameter
rca-query --input my_transformers.csv --parameter "Health index" --operator "<" --threshold 80

# Backward-compatible failure / non-failure classification
rca-classify

# Regenerate the ontology TBox
rca-build-ontology --output-dir data/ontology
```

## Python API

```python
from root_cause_analysis import (
    diagnose, build_diagnosed_graph, diagnosis_report,
    sample_transformer_measurements, iec60599_diagnosis,
)

measurements = sample_transformer_measurements()

# Diagnose with explanation traces
for d in diagnose(measurements):
    print(d.explanation())

# Knowledge graph + PROV-O provenance, plus a Markdown report
graph, diagnoses = build_diagnosed_graph(measurements)
print(diagnosis_report(diagnoses))

# Low-level IEC 60599 classifier
result = iec60599_diagnosis({"H2": 200, "CH4": 500, "C2H6": 30, "C2H4": 300, "C2H2": 10})
print(result.code, result.label)   # -> T3 ...
```
