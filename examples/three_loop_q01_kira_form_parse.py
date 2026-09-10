from __future__ import annotations

import json
from pathlib import Path

from three_loop.kira_form_parser import iter_kira_form_rules


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_4line" / "masters.final"
OUTPUT = PROJECT / "qedcalc_kira_form_parse_result.json"


def _parse_master_file(path: Path) -> set[tuple[int, ...]]:
    masters: set[tuple[int, ...]] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or "[" not in line or "]" not in line:
            continue
        body = line.split("[", 1)[1].split("]", 1)[0]
        masters.add(tuple(int(part.strip()) for part in body.split(",")))
    return masters


def main() -> None:
    if not FORM_FILE.is_file():
        raise SystemExit(f"missing FORM export: {FORM_FILE}")
    if not MASTERS_FILE.is_file():
        raise SystemExit(f"missing masters file: {MASTERS_FILE}")

    masters = _parse_master_file(MASTERS_FILE)
    rule_count = 0
    zero_rules = 0
    rhs_term_count = 0
    max_rhs_terms = 0
    rhs_integrals: set[tuple[int, ...]] = set()
    non_master_rhs: set[tuple[int, ...]] = set()
    lhs_indices: set[tuple[int, ...]] = set()
    coefficient_samples: list[str] = []
    rule_samples: list[dict[str, object]] = []

    for rule in iter_kira_form_rules(FORM_FILE, family="Q01_4line"):
        rule_count += 1
        lhs_indices.add(rule.lhs.indices)
        if rule.is_zero:
            zero_rules += 1
        rhs_term_count += len(rule.terms)
        max_rhs_terms = max(max_rhs_terms, len(rule.terms))
        for term in rule.terms:
            rhs_integrals.add(term.integral.indices)
            if term.integral.indices not in masters:
                non_master_rhs.add(term.integral.indices)
            if len(coefficient_samples) < 12 and term.coefficient_form not in coefficient_samples:
                coefficient_samples.append(term.coefficient_form)
        if len(rule_samples) < 8:
            rule_samples.append(
                {
                    "lhs": list(rule.lhs.indices),
                    "term_count": len(rule.terms),
                    "terms": [
                        {
                            "coefficient_form": term.coefficient_form,
                            "rhs": list(term.integral.indices),
                        }
                        for term in rule.terms[:8]
                    ],
                    "rhs_form_prefix": rule.rhs_form[:300],
                }
            )

    payload = {
        "form_file": str(FORM_FILE),
        "master_count": len(masters),
        "masters": [list(row) for row in sorted(masters)],
        "rule_count": rule_count,
        "unique_lhs_count": len(lhs_indices),
        "zero_rule_count": zero_rules,
        "rhs_term_count": rhs_term_count,
        "unique_rhs_integral_count": len(rhs_integrals),
        "max_rhs_terms_per_rule": max_rhs_terms,
        "non_master_rhs_count": len(non_master_rhs),
        "non_master_rhs_samples": [list(row) for row in sorted(non_master_rhs)[:20]],
        "coefficient_samples": coefficient_samples,
        "rule_samples": rule_samples,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    print("QEDCalc Q01 Kira FORM reduction parser validation")
    print(f"FORM file: {FORM_FILE}")
    print(f"masters: {len(masters)}")
    print(f"rules: {rule_count}")
    print(f"unique LHS: {len(lhs_indices)}")
    print(f"zero rules: {zero_rules}")
    print(f"RHS terms: {rhs_term_count}")
    print(f"unique RHS integrals: {len(rhs_integrals)}")
    print(f"max RHS terms/rule: {max_rhs_terms}")
    print(f"non-master RHS integrals: {len(non_master_rhs)}")
    print("coefficient samples:")
    for coeff in coefficient_samples:
        print(f"  {coeff}")
    print(f"generated: {OUTPUT}")

    if rule_count != 6183:
        raise SystemExit(f"expected 6183 FORM rules, got {rule_count}")
    if len(lhs_indices) != rule_count:
        raise SystemExit("duplicate FORM reduction LHS detected")
    if non_master_rhs:
        raise SystemExit(
            "back-substituted FORM table still contains non-master RHS integrals; "
            "send qedcalc_kira_form_parse_result.json"
        )
    print("Q01 Kira FORM reduction parser PASS")


if __name__ == "__main__":
    main()
