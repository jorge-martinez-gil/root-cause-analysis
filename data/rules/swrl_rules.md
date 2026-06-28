# Diagnostic Rule Set

This document is the canonical, human-readable description of the rules executed
by `src/root_cause_analysis/rules.py`. It supersedes the legacy `SWRL rules.txt`.

## 1. Root-cause classification — IEC 60599 basic gas-ratio method

Dissolved-gas analysis (DGA) is interpreted with the **IEC 60599:2015** basic
gas-ratio method (also reproduced in **IEEE Std C57.104-2019**). Three ratios are
computed from gas concentrations (μL/L):

- `R1 = C2H2 / C2H4`  (acetylene / ethylene)
- `R2 = CH4 / H2`     (methane / hydrogen)
- `R5 = C2H4 / C2H6`  (ethylene / ethane)

A fault code is assigned per the IEC 60599 case table:

| Code | Fault | R1 = C2H2/C2H4 | R2 = CH4/H2 | R5 = C2H4/C2H6 |
|------|-------|----------------|-------------|----------------|
| PD | Partial discharges | not significant | < 0.1 | < 0.2 |
| D1 | Low-energy discharge | > 1 | 0.1 – 0.5 | > 1 |
| D2 | High-energy discharge (arcing) | 0.6 – 2.5 | 0.1 – 1 | > 2 |
| T1 | Thermal fault, t < 300 °C | not significant | > 1 | < 1 |
| T2 | Thermal fault, 300–700 °C | < 0.1 | > 1 | 1 – 4 |
| T3 | Thermal fault, t > 700 °C | < 0.2 | > 1 | > 4 |

The ratio method is only applied when gassing is *significant*: at least one of
H2, CH4, C2H6, C2H4, C2H2 must exceed its IEC 60599 90 %-typical concentration.
When no case matches, the result is reported as `ND` (indeterminate — possible
mixed faults), and when no gas is significant the result is `NORMAL`.

Because the method depends on ratios and conditional ranges, it is implemented
procedurally rather than as flat SWRL atoms; the table above is its specification.

## 2. Advisory oil-quality / health screening rules

These rules are **advisory** and their thresholds are configurable. They produce
*symptoms* that contribute to the overall asset status; they are not formal
standard limits. Expressed in SWRL-style notation:

```
# High moisture in oil (IEC 60422 concept; advisory threshold)
Transformer(?t) ^ Water_content(?w) ^ relatesToWaterContent(?t,?w)
    ^ hasWaterLevel(?w,?v) ^ swrlb:greaterThan(?v,30) -> hasSymptom(?t, MoistureSymptom)

# Low dielectric breakdown voltage (advisory threshold, kV)
Transformer(?t) ^ hasDielectricRigidity(?t,?v)
    ^ swrlb:lessThan(?v,40) -> hasSymptom(?t, DielectricStrengthSymptom)

# Low interfacial tension (advisory threshold, mN/m)
Transformer(?t) ^ hasInterfacialTension(?t,?v)
    ^ swrlb:lessThan(?v,25) -> hasSymptom(?t, OilAgeingSymptom)

# Low composite health index (illustrative heuristic)
Transformer(?t) ^ hasHealthIndex(?t,?v)
    ^ swrlb:lessThan(?v,80) -> hasSymptom(?t, DegradedConditionSymptom)
```

## 3. Status derivation

The overall asset status is the worst severity among all fired rules:
`critical -> Failure`, `major -> Action required`, `minor/advisory -> Investigate`,
otherwise `Healthy`. Every diagnosis carries a full explanation trace listing the
rules that fired and the evidence (parameter, value, operator, threshold).

## References

- IEC 60599:2015 — Interpretation of dissolved and free gases analysis.
- IEEE Std C57.104-2019 — Interpretation of gases in oil-immersed transformers.
- M. Duval (2002), IEEE Electrical Insulation Magazine 18(3), 8–17.
- IEC 60422:2013 — Mineral insulating oils: supervision and maintenance.
