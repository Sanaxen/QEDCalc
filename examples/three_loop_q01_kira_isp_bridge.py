from __future__ import annotations

from pathlib import Path

import sympy as sp

from three_loop.kira_isp_bridge import (
    expand_qedcalc_integral_to_kira,
    reduce_qedcalc_integral_via_kira,
)
from three_loop.kira_reducer import (
    KiraReductionTable,
    map_qedcalc_physical_integral_to_kira,
    reduce_qedcalc_physical_integral,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_4line" / "masters.final"
SOURCE = (1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0)


def _with_isp(slot: int, power: int) -> tuple[int, ...]:
    values = list(SOURCE)
    values[slot] = power
    return tuple(values)


def _term_map(result) -> dict[tuple[int, ...], sp.Expr]:
    return {term.master: sp.factor(term.coefficient) for term in result.terms}


def main() -> None:
    if not FORM_FILE.is_file() or not MASTERS_FILE.is_file():
        raise SystemExit(
            "missing Kira r6s2d2 FORM export; run the full reduction and FORM export first"
        )

    print("QEDCalc Q01 native ISP -> Kira basis bridge validation")
    table = KiraReductionTable.from_form_export(FORM_FILE, MASTERS_FILE)
    print(f"rules loaded: {len(table.rules)}")
    print(f"masters loaded: {len(table.masters)}")

    # Physical-only input must reduce exactly as the already validated direct
    # physical mapper.  This protects the overall P=-D sign convention.
    physical_expansion = expand_qedcalc_integral_to_kira(SOURCE)
    direct_map = map_qedcalc_physical_integral_to_kira(SOURCE)
    if len(physical_expansion.terms) != 1:
        raise SystemExit("physical-only bridge expansion did not produce one Kira integral")
    only = physical_expansion.terms[0]
    if only.kira_indices != direct_map.kira_indices:
        raise SystemExit("physical-only bridge Kira indices disagree with direct mapper")
    if sp.simplify(only.coefficient - direct_map.normalization_sign) != 0:
        raise SystemExit("physical-only bridge normalization sign disagrees with direct mapper")

    old_reduction = reduce_qedcalc_physical_integral(table, SOURCE)
    new_reduction = reduce_qedcalc_integral_via_kira(table, SOURCE)
    if old_reduction.status != new_reduction.status:
        raise SystemExit("physical-only reducer status changed through ISP bridge")
    if _term_map(old_reduction) != _term_map(new_reduction):
        raise SystemExit("physical-only master coefficients changed through ISP bridge")

    print(f"physical-only expansion terms: {len(physical_expansion.terms)}")
    print(f"physical-only status: {new_reduction.status}")

    # Native indices 9,10,11 correspond to D10,D11,D12.
    one_power_results = []
    for slot, name in ((9, "D10"), (10, "D11"), (11, "D12")):
        native = _with_isp(slot, -1)
        expansion = expand_qedcalc_integral_to_kira(native)
        print(f"{name}^-index numerator degree 1 expansion terms: {len(expansion.terms)}")
        for term in expansion.terms:
            print(f"  {sp.sstr(term.coefficient)} * {term.kira_indices}")
        if len(expansion.terms) != 3:
            raise SystemExit(f"{name} first-power numerator should expand to exactly 3 terms")

        reduced = reduce_qedcalc_integral_via_kira(table, native)
        one_power_results.append((name, reduced))
        print(
            f"{name} first-power reduction: status={reduced.status}, "
            f"master_terms={len(reduced.terms)}, missing={len(reduced.missing_kira_integrals)}"
        )
        if reduced.missing_kira_integrals:
            for item in reduced.missing_kira_integrals[:10]:
                print(f"  missing Kira integral: {item}")
            raise SystemExit(
                f"{name} first-power numerator is outside the current Kira table; "
                "increase the Kira seed before continuing"
            )
        if any(term.master not in table.masters for term in reduced.terms):
            raise SystemExit(f"{name} reduction contains a non-master RHS integral")

    # Degree-two single-ISP algebra should contain six multinomial terms.
    for slot, name in ((9, "D10"), (10, "D11"), (11, "D12")):
        expansion = expand_qedcalc_integral_to_kira(_with_isp(slot, -2))
        print(f"{name} degree-2 expansion terms: {len(expansion.terms)}")
        if len(expansion.terms) != 6:
            raise SystemExit(f"{name} squared numerator should expand to exactly 6 terms")

    # Positive native ISP indices mean 1/(linear scalar product)^n and are not
    # representable by this finite polynomial bridge.
    rejected = False
    try:
        expand_qedcalc_integral_to_kira(_with_isp(9, 1))
    except ValueError:
        rejected = True
    print(f"positive native ISP denominator rejected: {rejected}")
    if not rejected:
        raise SystemExit("positive native linear ISP denominator was not rejected")

    print("first-power master term counts:")
    for name, result in one_power_results:
        print(f"  {name}: {len(result.terms)}")

    print("Q01 Kira native ISP bridge PASS")


if __name__ == "__main__":
    main()
