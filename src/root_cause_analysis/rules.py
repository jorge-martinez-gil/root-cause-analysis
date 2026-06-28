"""Standards-grounded diagnostic rules for power-transformer root cause analysis.

This module implements the *evidence layer* of the reasoning pipeline. Every rule
is explicit and documented, and every rule that fires returns a structured list of
:class:`Evidence` objects so that downstream components can build a complete,
human-readable explanation trace.

The dissolved-gas-analysis (DGA) root-cause classifier follows the **IEC 60599**
basic gas-ratio method (also reproduced in **IEEE C57.104-2019**). The oil-quality
and health screening rules are advisory and clearly labelled as such; their
thresholds are configurable and are *not* presented as formal standard limits.

References
----------
* IEC 60599:2015 — *Mineral oil-filled electrical equipment in service — Guidance
  on the interpretation of dissolved and free gases analysis.*
* IEEE Std C57.104-2019 — *IEEE Guide for the Interpretation of Gases Generated in
  Mineral Oil-Immersed Transformers.*
* M. Duval (2002), "A review of faults detectable by gas-in-oil analysis in
  transformers," *IEEE Electrical Insulation Magazine* 18(3), 8-17.
* IEC 60422:2013 — *Mineral insulating oils in electrical equipment — Supervision
  and maintenance guidance* (oil-quality screening concepts).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Fault taxonomy (IEC 60599 / IEEE C57.104)
# ---------------------------------------------------------------------------

#: Canonical fault codes and their human-readable descriptions.
FAULT_LABELS: dict[str, str] = {
    "PD": "Partial discharges",
    "D1": "Discharges of low energy (sparking / partial arcing)",
    "D2": "Discharges of high energy (arcing)",
    "T1": "Thermal fault, t < 300 °C",
    "T2": "Thermal fault, 300 °C ≤ t ≤ 700 °C",
    "T3": "Thermal fault, t > 700 °C",
    "ND": "Indeterminate (gas ratios match no IEC 60599 case)",
    "NORMAL": "No significant gassing detected",
}

#: Typical recommended actions per fault code (engineering guidance, advisory).
FAULT_ACTIONS: dict[str, str] = {
    "PD": "Inspect for moisture/contamination and partial-discharge sources; "
    "schedule PD measurement and increase DGA sampling frequency.",
    "D1": "Investigate loose connections / poor contacts; inspect for low-energy "
    "sparking; increase DGA sampling frequency.",
    "D2": "Treat as urgent: high-energy arcing risk. Plan inspection/outage; "
    "check tap changer, leads and winding connections.",
    "T1": "Monitor for low-temperature overheating; review loading and cooling.",
    "T2": "Investigate moderate overheating; inspect cooling system, joints and "
    "circulating currents.",
    "T3": "Treat as urgent: severe overheating. Inspect for hot spots, bad "
    "contacts and core/winding faults; plan outage.",
    "ND": "Resample and re-evaluate; the gas pattern does not match a single "
    "IEC 60599 case (possible mixed faults).",
    "NORMAL": "No action required from DGA; continue routine monitoring.",
}

#: Coarse severity ranking used to derive an overall asset status.
FAULT_SEVERITY: dict[str, str] = {
    "D2": "critical",
    "T3": "critical",
    "D1": "major",
    "T2": "major",
    "PD": "minor",
    "T1": "minor",
    "ND": "advisory",
    "NORMAL": "none",
}

# IEC 60599:2015 90 %-typical gas concentrations (μL/L), transformers without a
# communicating on-load tap changer. Used only to gate the ratio method so that
# faults are not "diagnosed" from background/noise levels.
IEC60599_TYPICAL_VALUES: dict[str, float] = {
    "H2": 100.0,
    "CH4": 75.0,
    "C2H6": 65.0,
    "C2H4": 60.0,
    "C2H2": 3.0,
    "CO": 540.0,
    "CO2": 5300.0,
}

IEC60599_CITATION = "IEC 60599:2015, basic gas-ratio method (Table 1)"

# Map of friendly DataFrame column names to gas symbols used internally.
GAS_COLUMN_ALIASES: dict[str, str] = {
    "Hydrogen": "H2",
    "Methane": "CH4",
    "Ethane": "C2H6",
    "Ethylene": "C2H4",
    "Acetylene": "C2H2",
    "Oxygen": "O2",
    "Nitrogen": "N2",
    "CO": "CO",
    "CO2": "CO2",
}


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Evidence:
    """A single, auditable piece of evidence supporting a rule activation."""

    parameter: str
    value: float
    operator: str
    threshold: float | str
    unit: str = ""
    note: str = ""

    def __str__(self) -> str:
        unit = f" {self.unit}" if self.unit else ""
        val = f"{self.value:.4g}{unit}"
        if self.operator and self.threshold != "":
            thr = self.threshold
            thr_str = f"{thr:g}" if isinstance(thr, (int, float)) else str(thr)
            base = f"{self.parameter} = {val} {self.operator} {thr_str}"
        else:
            base = f"{self.parameter} = {val}"
        return f"{base}  ({self.note})" if self.note else base


# ---------------------------------------------------------------------------
# Screening rule abstraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiagnosticRule:
    """A declarative diagnostic/screening rule.

    ``evaluate`` receives a mapping of parameter -> value and returns a list of
    :class:`Evidence` when the rule fires, or ``None`` when it does not.
    """

    id: str
    name: str
    description: str
    source: str
    severity: str
    conclusion: str
    recommended_action: str
    evaluate: Callable[[Mapping[str, float]], list[Evidence] | None] = field(repr=False)


# ---------------------------------------------------------------------------
# IEC 60599 basic gas-ratio method
# ---------------------------------------------------------------------------


def _ratio(numerator: float, denominator: float) -> float | None:
    """Safe ratio: ``None`` when the denominator is (near) zero."""
    if denominator is None or abs(denominator) < 1e-12:
        return None
    return numerator / denominator


def _between(value: float | None, low: float, high: float) -> bool:
    return value is not None and low <= value <= high


def _lt(value: float | None, bound: float) -> bool:
    return value is not None and value < bound


def _gt(value: float | None, bound: float) -> bool:
    return value is not None and value > bound


@dataclass(frozen=True)
class DGAResult:
    """Outcome of the IEC 60599 ratio method for one asset."""

    code: str
    label: str
    significant: bool
    ratios: dict[str, float | None]
    matched_cases: list[str]
    evidence: list[Evidence]


def dga_significant(gases: Mapping[str, float]) -> tuple[bool, list[str]]:
    """Return whether gassing is significant per IEC 60599 typical values."""
    exceeded = [
        gas
        for gas, typical in IEC60599_TYPICAL_VALUES.items()
        if gas in {"H2", "CH4", "C2H6", "C2H4", "C2H2"} and float(gases.get(gas, 0.0)) > typical
    ]
    return (len(exceeded) > 0, exceeded)


def iec60599_diagnosis(gases: Mapping[str, float]) -> DGAResult:
    """Classify the dominant fault using the IEC 60599 basic gas-ratio method.

    Ratios used:

    * ``R1 = C2H2 / C2H4``
    * ``R2 = CH4 / H2``
    * ``R5 = C2H4 / C2H6``

    Cases are evaluated in IEC table order; when more than one case matches, the
    first is reported as the primary code and all matches are listed for
    transparency.
    """
    h2 = float(gases.get("H2", 0.0))
    ch4 = float(gases.get("CH4", 0.0))
    c2h6 = float(gases.get("C2H6", 0.0))
    c2h4 = float(gases.get("C2H4", 0.0))
    c2h2 = float(gases.get("C2H2", 0.0))

    r1 = _ratio(c2h2, c2h4)  # C2H2 / C2H4
    r2 = _ratio(ch4, h2)  # CH4  / H2
    r5 = _ratio(c2h4, c2h6)  # C2H4 / C2H6
    ratios = {"R1=C2H2/C2H4": r1, "R2=CH4/H2": r2, "R5=C2H4/C2H6": r5}

    significant, exceeded = dga_significant(gases)
    if not significant:
        ev = [
            Evidence(
                parameter="DGA gassing",
                value=0.0,
                operator="below",
                threshold="IEC 60599 typical values",
                note="no key gas exceeds its 90 %-typical concentration",
            )
        ]
        return DGAResult("NORMAL", FAULT_LABELS["NORMAL"], False, ratios, [], ev)

    # IEC 60599 case table.  NS (non-significant) ratios are simply not tested.
    matches: list[str] = []
    if _lt(r2, 0.1) and _lt(r5, 0.2):
        matches.append("PD")
    if _gt(r1, 1.0) and _between(r2, 0.1, 0.5) and _gt(r5, 1.0):
        matches.append("D1")
    if _between(r1, 0.6, 2.5) and _between(r2, 0.1, 1.0) and _gt(r5, 2.0):
        matches.append("D2")
    if _gt(r2, 1.0) and _lt(r5, 1.0):
        matches.append("T1")
    if _lt(r1, 0.1) and _gt(r2, 1.0) and _between(r5, 1.0, 4.0):
        matches.append("T2")
    if _lt(r1, 0.2) and _gt(r2, 1.0) and _gt(r5, 4.0):
        matches.append("T3")

    code = matches[0] if matches else "ND"

    def fmt(x: float | None) -> str:
        return "n/a" if x is None else f"{x:.3g}"

    evidence = [
        Evidence(
            parameter="significant gases",
            value=float(len(exceeded)),
            operator="exceed",
            threshold="IEC 60599 typical",
            note="gases above typical: " + ", ".join(exceeded),
        ),
        Evidence(
            "R1 = C2H2/C2H4",
            r1 if r1 is not None else math.nan,
            "",
            "",
            note=fmt(r1) if r1 is None else "",
        ),
        Evidence("R2 = CH4/H2", r2 if r2 is not None else math.nan, "", ""),
        Evidence("R5 = C2H4/C2H6", r5 if r5 is not None else math.nan, "", ""),
    ]
    if len(matches) > 1:
        evidence.append(
            Evidence(
                parameter="matched IEC cases",
                value=float(len(matches)),
                operator="=",
                threshold=", ".join(matches),
                note="primary code is the first IEC-table match",
            )
        )
    return DGAResult(code, FAULT_LABELS[code], True, ratios, matches, evidence)


def duval_triangle_coordinates(
    gases: Mapping[str, float],
) -> tuple[float, float, float] | None:
    """Return Duval Triangle 1 coordinates (%CH4, %C2H4, %C2H2).

    These coordinates are reported as supporting evidence. Full polygon zone
    classification is intentionally *not* claimed here to avoid mis-stating
    boundary geometry; the IEC 60599 ratio method is the authoritative classifier.
    """
    ch4 = float(gases.get("CH4", 0.0))
    c2h4 = float(gases.get("C2H4", 0.0))
    c2h2 = float(gases.get("C2H2", 0.0))
    total = ch4 + c2h4 + c2h2
    if total <= 0:
        return None
    return (100.0 * ch4 / total, 100.0 * c2h4 / total, 100.0 * c2h2 / total)


# ---------------------------------------------------------------------------
# Advisory oil-quality / health screening rules
# ---------------------------------------------------------------------------


def _screen_water_content(p: Mapping[str, float]) -> list[Evidence] | None:
    value = p.get("Water content")
    if value is None:
        return None
    limit = 30.0  # advisory action level (mg/kg), configurable
    if float(value) > limit:
        return [Evidence("Water content", float(value), ">", limit, "mg/kg")]
    return None


def _screen_dielectric_rigidity(p: Mapping[str, float]) -> list[Evidence] | None:
    value = p.get("Dielectric rigidity")
    if value is None:
        return None
    limit = 40.0  # advisory minimum breakdown voltage (kV), configurable
    if float(value) < limit:
        return [Evidence("Dielectric rigidity", float(value), "<", limit, "kV")]
    return None


def _screen_interfacial_tension(p: Mapping[str, float]) -> list[Evidence] | None:
    value = p.get("Interfacial V")
    if value is None:
        return None
    limit = 25.0  # advisory minimum interfacial tension (mN/m), configurable
    if float(value) < limit:
        return [Evidence("Interfacial tension", float(value), "<", limit, "mN/m")]
    return None


def _screen_health_index(p: Mapping[str, float]) -> list[Evidence] | None:
    value = p.get("Health index")
    if value is None:
        return None
    limit = 80.0  # illustrative health-index heuristic, configurable
    if float(value) < limit:
        return [Evidence("Health index", float(value), "<", limit, "%")]
    return None


SCREENING_RULES: tuple[DiagnosticRule, ...] = (
    DiagnosticRule(
        id="OIL-WATER",
        name="High moisture in oil",
        description="Water content above the advisory action level accelerates "
        "insulation ageing and lowers dielectric strength.",
        source="IEC 60422:2013 (advisory, configurable threshold)",
        severity="major",
        conclusion="Moisture symptom",
        recommended_action="Schedule oil drying/reclamation; check for ingress and "
        "breather/conservator integrity.",
        evaluate=_screen_water_content,
    ),
    DiagnosticRule(
        id="OIL-BDV",
        name="Low dielectric breakdown voltage",
        description="Breakdown voltage below the advisory minimum indicates "
        "degraded dielectric strength (moisture/particles).",
        source="IEC 60422:2013 (advisory, configurable threshold)",
        severity="major",
        conclusion="Dielectric-strength symptom",
        recommended_action="Filter/recondition oil; investigate moisture and "
        "particulate contamination.",
        evaluate=_screen_dielectric_rigidity,
    ),
    DiagnosticRule(
        id="OIL-IFT",
        name="Low interfacial tension",
        description="Low interfacial tension indicates oxidation by-products and oil ageing.",
        source="IEC 60422:2013 (advisory, configurable threshold)",
        severity="minor",
        conclusion="Oil-ageing symptom",
        recommended_action="Plan oil reclamation; review oxidation inhibitor level.",
        evaluate=_screen_interfacial_tension,
    ),
    DiagnosticRule(
        id="HEALTH-IDX",
        name="Low health index",
        description="Composite health index below the advisory threshold flags an "
        "asset for prioritised inspection.",
        source="Health-index heuristic (illustrative, configurable)",
        severity="minor",
        conclusion="Degraded-condition symptom",
        recommended_action="Prioritise for detailed condition assessment.",
        evaluate=_screen_health_index,
    ),
)
