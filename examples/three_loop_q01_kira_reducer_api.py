from __future__ import annotations

from pathlib import Path

import sympy as sp

from three_loop.kira_reducer import (
    KiraReductionTable,
    map_qedcalc_physical_integral_to_kira,
    reduce_qedcalc_physical_integral,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_4line" / "masters.final"


def main() -> None:
    if not FORM_FILE.is_file():
        raise SystemExit(f"missing FORM reduction file: {FORM_FILE}")
    if not MASTERS_FILE.is_file():
        raise SystemExit(f"missing Kira master list: {MASTERS_FILE}")

    print("QEDCalc Q01 Kira reducer API validation")
    table = KiraReductionTable.from_form_export(FORM_FILE, MASTERS_FILE)
    print(f"rules loaded: {len(table.rules)}")
    print(f"masters loaded: {len(table.masters)}")

    if len(table.rules) != 6183:
        raise SystemExit(f"unexpected rule count: {len(table.rules)}")
    if len(table.masters) != 4:
        raise SystemExit(f"unexpected master count: {len(table.masters)}")

    # Native QEDCalc source sector: D1,D3,D5,D6 active.
    qed_source = (1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0)
    mapped = map_qedcalc_physical_integral_to_kira(qed_source)
    expected_kira = (1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)
    print(f"QEDCalc source: {qed_source}")
    print(f"Kira mapped  : {mapped.kira_indices}")
    print(f"physical sign: {mapped.normalization_sign}")
    if mapped.kira_indices != expected_kira:
        raise SystemExit(f"source-sector permutation mismatch: {mapped.kira_indices}")
    if mapped.normalization_sign != 1:
        raise SystemExit(f"unexpected source-sector normalization sign: {mapped.normalization_sign}")

    source_result = reduce_qedcalc_physical_integral(table, qed_source)
    print(f"source status: {source_result.status}")
    print(f"source RHS terms: {len(source_result.terms)}")
    if source_result.status != "master":
        raise SystemExit(f"QEDCalc source sector did not map to Kira master: {source_result.status}")
    if len(source_result.terms) != 1:
        raise SystemExit("source master identity did not contain exactly one term")
    if source_result.terms[0].master != expected_kira:
        raise SystemExit("source master identity returned the wrong master")
    if sp.simplify(source_result.terms[0].coefficient - 1) != 0:
        raise SystemExit("source master identity coefficient is not one")

    # Every imported Kira rule must be queryable and already terminate on the
    # declared four masters.  The constructor enforces the RHS-master property;
    # here we exercise every lookup path once.
    status_counts = {"reduced": 0, "master": 0, "not_in_table": 0}
    max_terms = 0
    for lhs in table.rules:
        result = table.reduce_kira(lhs)
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
        max_terms = max(max_terms, len(result.terms))
        if result.status != "reduced":
            raise SystemExit(f"table LHS was not returned as reduced: {lhs}: {result.status}")
        for term in result.terms:
            if term.master not in table.masters:
                raise SystemExit(f"non-master RHS escaped table validation: {term.master}")

    for master in table.masters:
        result = table.reduce_kira(master)
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
        if result.status != "master" or len(result.terms) != 1:
            raise SystemExit(f"master identity lookup failed: {master}")
        if result.terms[0].master != master or sp.simplify(result.terms[0].coefficient - 1) != 0:
            raise SystemExit(f"invalid master identity: {master}")

    missing = (9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9)
    missing_result = table.reduce_kira(missing)
    status_counts[missing_result.status] = status_counts.get(missing_result.status, 0) + 1
    if missing_result.status != "not_in_table":
        raise SystemExit("out-of-table lookup did not return not_in_table")

    # Native linear ISP powers must never be silently reinterpreted as Kira's
    # quadratic auxiliary propagator powers.
    isp_rejected = False
    try:
        map_qedcalc_physical_integral_to_kira(
            (1, 0, 1, 0, 1, 1, 0, 0, 0, -1, 0, 0)
        )
    except ValueError:
        isp_rejected = True
    print(f"native ISP direct-map rejected: {isp_rejected}")
    if not isp_rejected:
        raise SystemExit("unsafe native ISP index mapping was not rejected")

    print(f"lookup status counts: {status_counts}")
    print(f"max master terms/rule: {max_terms}")
    print("Q01 Kira reducer API PASS")


if __name__ == "__main__":
    main()
