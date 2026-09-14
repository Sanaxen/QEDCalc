"""Export and audit the Q01 terminal leaves against the existing FireFly reduction.

This helper never reruns the expensive FireFly reduction.  It takes the RHS
leaves left by the closure-wave-1 FORM export, writes them as a new Kira target
list, asks ``kira2form`` to export any reductions already present in the saved
FireFly database, then merges wave-1 and wave-2 rules and checks whether the
projected-amplitude dependency graph now closes to ``masters.final`` only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_DIR_NAME,
    ALT_ROOT,
    FAMILY,
    PROJECT,
    _find_export_files,
)
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices

IndexTuple = tuple[int, ...]

TARGET_FILE = PROJECT / "q01_terminal_wave2_targets"
EXPORT_JOB = PROJECT / "jobs_q01_terminal_wave2_firefly_export.yaml"
OUTPUT_JSON = PROJECT / "q01_terminal_wave2_firefly_export_audit.json"


def _indices12(values: Iterable[int]) -> IndexTuple:
    result = tuple(int(v) for v in values)
    if len(result) != 12:
        raise ValueError(f"expected 12 indices, got {len(result)}")
    return result


def _integral_text(indices: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in indices)}]"


def _load_graph(path: Path) -> tuple[dict[IndexTuple, tuple[IndexTuple, ...]], set[IndexTuple]]:
    rules: dict[IndexTuple, tuple[IndexTuple, ...]] = {}
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(path, family=FAMILY):
        lhs = _indices12(rule.lhs.indices)
        rhs = tuple(_indices12(term.integral.indices) for term in rule.terms)
        if lhs in rules or lhs in zeros:
            raise SystemExit(f"ERROR: duplicate FORM rule in {path}: {lhs}")
        if rhs:
            rules[lhs] = rhs
        elif rule.is_zero:
            zeros.add(lhs)
        else:
            raise SystemExit(
                f"ERROR: nonzero scalar-only FORM RHS is unsupported: {lhs} -> {rule.rhs_form!r}"
            )
    return rules, zeros


def _terminal_leaves(
    rules: dict[IndexTuple, tuple[IndexTuple, ...]],
    zeros: set[IndexTuple],
    masters: set[IndexTuple],
) -> set[IndexTuple]:
    rhs = {child for children in rules.values() for child in children}
    return {v for v in rhs if v not in rules and v not in zeros and v not in masters}


def generate() -> None:
    wave1_form, masters_file = _find_export_files()
    rules, zeros = _load_graph(wave1_form)
    masters = set(load_master_indices(masters_file, family=FAMILY))
    leaves = sorted(_terminal_leaves(rules, zeros, masters))
    if not leaves:
        raise SystemExit("ERROR: wave-1 FORM graph already has no non-master terminal leaves")

    TARGET_FILE.write_text(
        "\n".join(_integral_text(v) for v in leaves) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    EXPORT_JOB.write_text(
        "jobs:\n"
        "  - kira2form:\n"
        "      target:\n"
        f"        - [{FAMILY},{TARGET_FILE.name}]\n"
        f"      alt_dir: {ALT_DIR_NAME}\n",
        encoding="utf-8",
        newline="\n",
    )

    print("QEDCalc Q01 terminal wave-2 FireFly export generator")
    print("mode: existing FireFly artifacts only; reduction is NOT recomputed")
    print("wave-1 FORM export:", wave1_form)
    print("explicit masters:", len(masters))
    print("wave-1 non-master terminal leaves:", len(leaves))
    print("generated target list:", TARGET_FILE)
    print("generated export job:", EXPORT_JOB)
    print("Q01 terminal wave-2 FireFly export generation PASS")


def _find_wave2_form() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / "kira_q01_terminal_wave2_targets.inc"
    if preferred.is_file():
        return preferred

    candidates = sorted(
        (p for p in result_dir.glob("*.inc") if "terminal_wave2" in p.name),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    raise SystemExit(
        "ERROR: terminal wave-2 kira2form export was not found under " + str(result_dir)
    )


def audit() -> None:
    wave1_form, masters_file = _find_export_files()
    wave2_form = _find_wave2_form()
    masters = set(load_master_indices(masters_file, family=FAMILY))

    wave1_rules, wave1_zeros = _load_graph(wave1_form)
    wave2_rules, wave2_zeros = _load_graph(wave2_form)
    wave1_terminal = _terminal_leaves(wave1_rules, wave1_zeros, masters)

    overlap = set(wave1_rules) & set(wave2_rules)
    incompatible = [v for v in overlap if wave1_rules[v] != wave2_rules[v]]
    if incompatible:
        raise SystemExit(
            f"ERROR: wave-1/wave-2 exports disagree for {len(incompatible)} integral(s); first={incompatible[0]}"
        )

    merged_rules = dict(wave1_rules)
    merged_rules.update(wave2_rules)
    merged_zeros = set(wave1_zeros) | set(wave2_zeros)
    merged_terminal = _terminal_leaves(merged_rules, merged_zeros, masters)

    wave2_target_status = {
        "rule": sum(v in wave2_rules for v in wave1_terminal),
        "zero": sum(v in wave2_zeros for v in wave1_terminal),
        "explicit_master": sum(v in masters for v in wave1_terminal),
        "still_no_rule": sum(
            v not in wave2_rules and v not in wave2_zeros and v not in masters
            for v in wave1_terminal
        ),
    }

    # Detect cycles in the merged graph.  Terminal nodes are allowed for this
    # diagnostic, but a full 4-master closure PASS requires none to remain.
    state: dict[IndexTuple, int] = {}
    cycle_nodes: set[IndexTuple] = set()

    def visit(node: IndexTuple) -> None:
        flag = state.get(node, 0)
        if flag == 1:
            cycle_nodes.add(node)
            return
        if flag == 2 or node not in merged_rules:
            return
        state[node] = 1
        for child in merged_rules[node]:
            visit(child)
        state[node] = 2

    for node in merged_rules:
        visit(node)

    closed_to_four = len(masters) == 4 and not merged_terminal and not cycle_nodes
    summary = {
        "mode": "saved FireFly database; kira2form export only; no reduction recomputation",
        "wave1_form": str(wave1_form),
        "wave2_form": str(wave2_form),
        "masters_file": str(masters_file),
        "explicit_masters": len(masters),
        "wave1_rules": len(wave1_rules),
        "wave1_zero_rules": len(wave1_zeros),
        "wave1_terminal_leaves": len(wave1_terminal),
        "wave2_rules": len(wave2_rules),
        "wave2_zero_rules": len(wave2_zeros),
        "wave2_target_status": wave2_target_status,
        "merged_rules": len(merged_rules),
        "merged_zero_rules": len(merged_zeros),
        "remaining_nonmaster_terminal_leaves": len(merged_terminal),
        "remaining_terminal_integrals": [_integral_text(v) for v in sorted(merged_terminal)],
        "cycle_nodes": [_integral_text(v) for v in sorted(cycle_nodes)],
        "closed_to_four_explicit_masters": closed_to_four,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("QEDCalc Q01 terminal wave-2 FireFly export audit")
    print("wave-1 terminal leaves:", len(wave1_terminal))
    print("wave-2 reduction rules:", len(wave2_rules))
    print("wave-2 zero rules:", len(wave2_zeros))
    print("wave-2 target status:", wave2_target_status)
    print("merged reduction rules:", len(merged_rules))
    print("merged zero rules:", len(merged_zeros))
    print("explicit Kira masters:", len(masters))
    print("remaining non-master terminal leaves:", len(merged_terminal))
    print("dependency cycles:", len(cycle_nodes))
    print("audit JSON:", OUTPUT_JSON)

    if closed_to_four:
        print("Q01 terminal -> 4-master closure audit PASS")
        return

    if merged_terminal:
        print("Q01 terminal -> 4-master closure audit INCOMPLETE")
        print("additional saved-result export wave is required; FireFly reduction was not rerun")
        for value in sorted(merged_terminal)[:12]:
            print("  remaining:", _integral_text(value))
        raise SystemExit(3)

    print("Q01 terminal -> 4-master closure audit FAIL")
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "audit"))
    args = parser.parse_args()
    if args.mode == "generate":
        generate()
    else:
        audit()


if __name__ == "__main__":
    main()
