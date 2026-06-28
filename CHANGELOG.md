# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-28
### Added
- Explainable reasoning engine (`reasoning.py`) producing per-asset diagnoses with full explanation traces.
- Standards-grounded **IEC 60599 / IEEE C57.104** dissolved-gas root-cause classifier (`rules.py`), verified
  against labelled reference signatures.
- Programmatic, fully documented OWL **TBox** (`ontology.py`) and generated `data/ontology/onto_pw.ttl` / `.owl`.
- **PROV-O provenance**: inferred diagnoses are materialised back into the knowledge graph and are SPARQL-queryable.
- New CLIs: `rca-diagnose` (one-command pipeline with Markdown report + knowledge graph) and `rca-build-ontology`.
- SPARQL screening helper `screen_assets`; labelled reference dataset for tests and tutorials.
- Canonical rule specification `data/rules/swrl_rules.md`.

### Changed
- `classify_transformers` now delegates to the IEC 60599 engine instead of ad-hoc thresholds (API preserved).
- README reworked to describe the real pipeline; the previous "open benchmark" claim is reframed as roadmap.
- `rca-query` now screens a knowledge graph built from measurements by any parameter.

### Fixed
- Ontology inconsistency: `relatesToWaterContent` is now declared; measured properties are no longer modelled
  as subclasses of `Transformer`.
- Removed the divergent, inconsistent rule reimplementations; the rule set is now single-sourced.

## [0.1.0] - 2026-05-07
### Added
- Python package structure under `src/root_cause_analysis`.
- Reproducible examples and test suite.
- CI quality gates for linting, typing, and tests.
- Citation, contribution, and community health files.
