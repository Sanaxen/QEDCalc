from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_reduction import build_direct_symbolic_rules
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT = ROOT / "output" / "3loop_q01_direct_symbolic_reduction.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def main() -> None:
    print("QEDCalc Q01 exact direct symbolic reduction")
    family = q01_integral_family()
    targets = load_targets(SOURCE)
    templates = build_ibp_derivative_templates(family)
    rules = build_direct_symbolic_rules(family, targets, templates=templates)

    rhs_hist = Counter(rule.rhs_term_count for rule in rules)
    out = {
        "target_count": len(targets),
        "direct_symbolic_rule_count": len(rules),
        "non_direct_target_count": len(targets) - len(rules),
        "rhs_term_count_histogram": dict(sorted(rhs_hist.items())),
        "rules": [
            {
                "target": rule.target,
                "source_label": rule.source_label,
                "target_coefficient": str(rule.target_coefficient),
                "rhs": [
                    {"index": powers, "coefficient": str(coeff)}
                    for powers, coeff in rule.rhs
                ],
            }
            for rule in rules
        ],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"targets: {len(targets)}")
    print(f"exact direct symbolic rules: {len(rules)}")
    print(f"non-direct targets: {len(targets) - len(rules)}")
    print(f"rhs term-count histogram: {dict(sorted(rhs_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 exact direct symbolic reduction PASS")


if __name__ == "__main__":
    main()
