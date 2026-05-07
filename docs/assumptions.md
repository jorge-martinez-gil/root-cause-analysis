# Data and Model Assumptions

- The ontology file `data/ontology/onto_pw.owl` is a research sample with transformer and water-content entities.
- Classification uses threshold logic consistent with the original scripts:
  - `Life expectation < 22` → failure candidate
  - `Health index < 85` or `Power factor < 1` → non-failure candidate
- Input tabular data must include the columns:
  - `Life expectation`
  - `Health index`
  - `Power factor`
