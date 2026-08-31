from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_closure import audit_direct_symbolic_closure
from three_loop.direct_symbolic_reduction import DirectSymbolicRule

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_direct_symbolic_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_direct_symbolic_closure.json"


def _load_rules(data) -> tuple[DirectSymbolicRule, ...]:
    out = []
    for row in data["rules"]:
        out.append(DirectSymbolicRule(
            target=tuple(row["target"]),
            source_label=row["source_label"],
            target_coefficient=sp.sympify(row["target_coefficient"]),
            rhs=tuple((tuple(item[0]), sp.sympify(item[1])) for item in row["rhs"]),
        ))
    return tuple(out)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = tuple(IntegralIndex(tuple(item)) for item in data["targets"])
    rules = _load_rules(data)
    profile = audit_direct_symbolic_closure(targets, rules)

    pivot_hist = Counter(record.pivot_node_count for record in profile.records)
    terminal_hist = Counter(record.terminal_count for record in profile.records)
    out = {
        "target_count": profile.target_count,
        "rule_count": profile.rule_count,
        "fully_closed_target_count": profile.fully_closed_target_count,
        "target_with_unresolved_terminals_count": profile.target_with_unresolved_terminals_count,
        "max_pivot_node_count": profile.max_pivot_node_count,
        "max_terminal_count": profile.max_terminal_count,
        "pivot_node_count_histogram": dict(sorted(pivot_hist.items())),
        "terminal_count_histogram": dict(sorted(terminal_hist.items())),
        "records": [record.__dict__ for record in profile.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 exact direct-rule dependency closure")
    print(f"targets: {profile.target_count}")
    print(f"direct symbolic rules: {profile.rule_count}")
    print(f"fully closed through direct rules: {profile.fully_closed_target_count}")
    print(f"targets ending at unresolved terminals: {profile.target_with_unresolved_terminals_count}")
    print(f"max pivot nodes in one closure: {profile.max_pivot_node_count}")
    print(f"max unresolved terminals in one closure: {profile.max_terminal_count}")
    print(f"pivot-node histogram: {dict(sorted(pivot_hist.items()))}")
    print(f"terminal histogram: {dict(sorted(terminal_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 exact direct-rule dependency closure PASS")


if __name__ == "__main__":
    main()
