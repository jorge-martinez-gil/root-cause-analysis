# Root Cause Analysis in the Industrial Domain using Knowledge Graphs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![DOI:10.1016/j.procs.2022.01.304](https://img.shields.io/badge/DOI-10.1016%2Fj.procs.2022.01.304-blue.svg)](https://doi.org/10.1016/j.procs.2022.01.304)

Research software accompanying:
**Martinez-Gil et al. (2022), _Root Cause Analysis in the Industrial Domain using Knowledge Graphs: A Case Study on Power Transformers_.**

## Motivation

Industrial fault diagnosis requires actionable, explainable workflows. This repository demonstrates a knowledge graph-oriented approach that combines ontology querying and rule-based classification for transformer diagnostics.

## Key features

- Reproducible ontology query workflow (`query.py`, `rca-query`)
- Reproducible rule-based classification workflow (`swrl-rules.py`, `rca-classify`)
- Packaged Python module under `src/root_cause_analysis`
- Tests, linting, typing checks, and CI automation
- Citation and community-contribution infrastructure

## Approach overview

1. **Ontology query**: identify transformers with potentially risky measurements (e.g., water level threshold).
2. **Rule-based classification**: apply threshold logic from the publication examples to classify records.

## Installation

```bash
python -m pip install -e .
```

For development checks:

```bash
python -m pip install -e .[dev]
```

## Quickstart

```bash
python examples/minimal_quickstart.py
```

## Reproducible example

```bash
python examples/industrial_workflow.py
```

Expected output includes:
- transformers above the water threshold (e.g., `PW101`)
- lists of failure/non-failure candidates from the sample measurement table

## Project structure

```text
.
├── data/ontology/onto_pw.owl
├── docs/
├── examples/
├── src/root_cause_analysis/
├── tests/
├── query.py
└── swrl-rules.py
```

## Development

Run quality checks locally:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

## Documentation

- [Methodology](docs/methodology.md)
- [Data and model assumptions](docs/assumptions.md)
- [Usage guide](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)

## Citation

Please cite the paper if you find it useful:
```
@article{martinez2022root,
  title={Root cause analysis in the industrial domain using knowledge graphs: a case study on power transformers},
  author={Martinez-Gil, Jorge and Buchgeher, Georg and Gabauer, David and Freudenthaler, Bernhard and Filipiak, Dominik and Fensel, Anna},
  journal={Procedia Computer Science},
  volume={200},
  pages={944--953},
  year={2022},
  publisher={Elsevier}
}
```

## Roadmap

- Expand benchmark datasets and scenario coverage
- Add configurable rule profiles for additional industrial contexts
- Provide richer explainability artifacts for inferred outcomes

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
