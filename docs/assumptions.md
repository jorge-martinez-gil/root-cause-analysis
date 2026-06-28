# Data and Model Assumptions

## Inputs

- Measurements are provided as a table with one row per asset. An optional `Asset` column sets identifiers
  (otherwise `PW101`, `PW102`, … are assigned).
- Dissolved-gas columns (`Hydrogen`, `Methane`, `Ethane`, `Ethylene`, `Acetylene`, and optionally `CO`, `CO2`,
  `Oxygen`, `Nitrogen`) are interpreted in **μL/L (ppm)**.
- Oil-quality columns are interpreted as: `Water content` in mg/kg, `Dielectric rigidity` in kV,
  `Interfacial V` (interfacial tension) in mN/m, `Health index` in %.

## Root-cause classification (standards-grounded)

- Faults are classified with the **IEC 60599** basic gas-ratio method; codes are `PD, D1, D2, T1, T2, T3`.
- The method runs only when gassing is **significant** (a key gas exceeds its IEC 60599 90 %-typical value).
- If the ratios match **no** IEC case, the result is reported as **ND (indeterminate)** — never forced into a class.
- If no gas is significant, the result is **NORMAL**.

## Screening rules (advisory, configurable)

These thresholds are advisory defaults and are **not** formal standard limits:

- Water content > 30 mg/kg → moisture symptom
- Dielectric rigidity < 40 kV → dielectric-strength symptom
- Interfacial tension < 25 mN/m → oil-ageing symptom
- Health index < 80 % → degraded-condition symptom (illustrative heuristic)

## Status derivation

Overall asset status is the worst severity among fired rules:
`critical → Failure`, `major → Action required`, `minor/advisory → Investigate`, otherwise `Healthy`.
