from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_reduction import DirectSymbolicRule
from three_loop.merged_symbolic_closure import audit_merged_symbolic_closure

ROOT = Path(__file__).resolve().parents[1]
TARGET_SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
DIRECT_SOURCE = ROOT / "output" / "3loop_q01_direct_symbolic_reduction.json"
REVERSE_SOURCE = ROOT / "output" / "3loop_q01_reverse_symbolic_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_merged_symbolic_closure.json"
INDEX_RE = re.compile(r"I\(([-0-9, ]+)\)")


def load_targets(path: Path) -> tuple[IntegralIndex, ...]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.search(line)
        if match:
            out.append(IntegralIndex(tuple(int(part.strip()) for part in match.group(1).split(","))))
    return tuple(dict.fromkeys(out))


def load_rules(path: Path) -> tuple[DirectSymbolicRule, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for row in data["rules"]:
        out.append(DirectSymbolicRule(
            target=tuple(row["target"]),
            source_label=row["source_label"],
            target_coefficient=sp.sympify(row["target_coefficient"]),
            rhs=tuple(
                (tuple(item["index"]), sp.sympify(item["coefficient"]))
                for item in row["rhs"]
            ),
        ))
    return tuple(out)


def main() -> None:
    print("QEDCalc Q01 merged exact symbolic dependency closure")
    targets = load_targets(TARGET_SOURCE)
    direct_rules = load_rules(DIRECT_SOURCE)
    reverse_rules = load_rules(REVERSE_SOURCE)
    profile = audit_merged_symbolic_closure(targets, direct_rules, reverse_rules)
    closure = profile.closure

    pivot_hist = Counter(record.pivot_node_count for record in closure.records)
    terminal_hist = Counter(record.terminal_count for record in closure.records)
    distinct_terminals = sorted({
        terminal
        for record in closure.records
        for terminal in record.terminal_integrals
    })

    out = {
        "target_count": closure.target_count,
        "direct_rule_count": profile.direct_rule_count,
        "reverse_rule_count": profile.reverse_rule_count,
        "merged_rule_count": profile.merged_rule_count,
        "fully_closed_target_count": closure.fully_closed_target_count,
        "target_with_unresolved_terminals_count": closure.target_with_unresolved_terminals_count,
        "max_pivot_node_count": closure.max_pivot_node_count,
        "max_terminal_count": closure.max_terminal_count,
        "distinct_unresolved_terminal_count": len(distinct_terminals),
        "distinct_unresolved_terminals": distinct_terminals,
        "pivot_node_count_histogram": dict(sorted(pivot_hist.items())),
        "terminal_count_histogram": dict(sorted(terminal_hist.items())),
        "records": [record.__dict__ for record in closure.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"targets: {closure.target_count}")
    print(f"direct symbolic rules: {profile.direct_rule_count}")
    print(f"reverse symbolic rules: {profile.reverse_rule_count}")
    print(f"merged exact symbolic rules: {profile.merged_rule_count}")
    print(f"fully closed through merged rules: {closure.fully_closed_target_count}")
    print(f"targets ending at unresolved terminals: {closure.target_with_unresolved_terminals_count}")
    print(f"distinct unresolved terminals: {len(distinct_terminals)}")
    print(f"max pivot nodes in one closure: {closure.max_pivot_node_count}")
    print(f"max unresolved terminals in one closure: {closure.max_terminal_count}")
    print(f"pivot-node histogram: {dict(sorted(pivot_hist.items()))}")
    print(f"terminal histogram: {dict(sorted(terminal_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 merged exact symbolic dependency closure PASS")


if __name__ == "__main__":
    main()
