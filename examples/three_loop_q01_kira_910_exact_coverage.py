"""Final structural coverage audit for the completed exact-944 Q01 Kira reduction.

This script never reruns Kira.  It loads the 910 canonical native QEDCalc
integrals, expands native D10-D12 ISP powers into the Kira basis, and checks
that every demanded Kira integral reaches either a zero rule or one of the
masters in exact944/masters.final by recursively following the exported FORM
reduction graph.

Kira's kira2form output is not assumed to be fully flattened: a back-substituted
export may still reference another exported non-master rule on the RHS.  That
is valid as long as the complete dependency chain terminates at masters/zero.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_reducer import load_master_indices

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
EXACT_RESULTS = PROJECT / "exact944" / "results" / "Q01_full"
FORM_FILE = EXACT_RESULTS / "kira_q01_944_targets.inc"
MASTERS_FILE = EXACT_RESULTS / "masters.final"
NATIVE_TXT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT_JSON = PROJECT / "qedcalc_kira_q01_910_exact_coverage.json"
FAMILY = "Q01_full"
EXPECTED_NATIVE = 910
EXPECTED_UNIQUE_KIRA = 944

_INTEGRAL_RE = re.compile(r"\bI\(\s*([-+]?\d+(?:\s*,\s*[-+]?\d+){11})\s*\)")
IndexTuple = tuple[int, ...]


def _load_native_txt(path: Path) -> tuple[IndexTuple, ...]:
    if not path.exists():
        raise SystemExit(f"ERROR: native Q01 integral artifact not found: {path}")
    parsed: list[IndexTuple] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _INTEGRAL_RE.search(line)
        if match is not None:
            parsed.append(tuple(int(v.strip()) for v in match.group(1).split(",")))
    unique = tuple(dict.fromkeys(parsed))
    if len(parsed) != EXPECTED_NATIVE or len(unique) != EXPECTED_NATIVE:
        raise SystemExit(
            f"ERROR: expected {EXPECTED_NATIVE} unique native integrals; "
            f"got parsed={len(parsed)} unique={len(unique)}"
        )
    return unique


def _load_dependency_graph() -> tuple[set[IndexTuple], dict[IndexTuple, tuple[IndexTuple, ...]], set[IndexTuple]]:
    masters = set(load_master_indices(MASTERS_FILE, family=FAMILY))
    rules: dict[IndexTuple, tuple[IndexTuple, ...]] = {}
    zero_rules: set[IndexTuple] = set()

    for rule in iter_kira_form_rules(FORM_FILE, family=FAMILY):
        lhs = tuple(rule.lhs.indices)
        if lhs in rules or lhs in zero_rules:
            raise SystemExit(f"ERROR: duplicate FORM rule for {lhs}")
        rhs = tuple(tuple(term.integral.indices) for term in rule.terms)
        if not rhs:
            if not rule.is_zero:
                raise SystemExit(
                    "ERROR: FORM rule without integral RHS is not an explicit zero rule: "
                    f"{lhs} -> {rule.rhs_form[:160]}"
                )
            zero_rules.add(lhs)
        else:
            rules[lhs] = rhs

    return masters, rules, zero_rules


def _resolve_graph(
    key: IndexTuple,
    *,
    masters: set[IndexTuple],
    rules: dict[IndexTuple, tuple[IndexTuple, ...]],
    zero_rules: set[IndexTuple],
    memo: dict[IndexTuple, bool],
    unresolved_leaves: set[IndexTuple],
    cycles: set[IndexTuple],
    visiting: set[IndexTuple],
) -> bool:
    if key in masters or key in zero_rules:
        memo[key] = True
        return True
    if key in memo:
        return memo[key]
    if key in visiting:
        cycles.add(key)
        memo[key] = False
        return False
    rhs = rules.get(key)
    if rhs is None:
        unresolved_leaves.add(key)
        memo[key] = False
        return False

    visiting.add(key)
    ok = True
    for child in rhs:
        if not _resolve_graph(
            child,
            masters=masters,
            rules=rules,
            zero_rules=zero_rules,
            memo=memo,
            unresolved_leaves=unresolved_leaves,
            cycles=cycles,
            visiting=visiting,
        ):
            ok = False
    visiting.remove(key)
    memo[key] = ok
    return ok


def main() -> None:
    print("QEDCalc Q01 exact-944 final coverage audit")
    print("mode: saved exact944 artifacts only; no Kira rerun")
    print("FORM:", FORM_FILE)
    print("masters:", MASTERS_FILE)

    if not FORM_FILE.exists():
        raise SystemExit(f"ERROR: exact944 FORM export not found: {FORM_FILE}")
    if not MASTERS_FILE.exists():
        raise SystemExit(f"ERROR: exact944 masters.final not found: {MASTERS_FILE}")

    native_integrals = _load_native_txt(NATIVE_TXT)
    print("native integrals total:", len(native_integrals))

    masters, rules, zero_rules = _load_dependency_graph()
    nonmaster_rhs = {child for rhs in rules.values() for child in rhs if child not in masters}
    print("Kira rules loaded:", len(rules) + len(zero_rules))
    print("Kira zero rules:", len(zero_rules))
    print("Kira masters loaded:", len(masters))
    print("unique non-master RHS dependencies:", len(nonmaster_rhs))

    memo: dict[IndexTuple, bool] = {}
    unresolved_leaves: set[IndexTuple] = set()
    cycles: set[IndexTuple] = set()
    status_counts: Counter[str] = Counter()
    unique_expanded: set[IndexTuple] = set()
    missing_kira: set[IndexTuple] = set()
    total_expanded_terms = 0
    max_expansion_size = 0
    missing_examples: list[dict[str, Any]] = []
    rejected_examples: list[dict[str, Any]] = []

    for native in native_integrals:
        try:
            expansion = expand_qedcalc_integral_to_kira(native)
        except Exception as exc:
            status_counts["rejected"] += 1
            if len(rejected_examples) < 10:
                rejected_examples.append({"native": list(native), "error": str(exc)})
            continue

        total_expanded_terms += len(expansion.terms)
        max_expansion_size = max(max_expansion_size, len(expansion.terms))
        resolved = 0
        unresolved = 0
        local_missing: list[IndexTuple] = []

        for term in expansion.terms:
            kira = tuple(term.kira_indices)
            unique_expanded.add(kira)
            ok = _resolve_graph(
                kira,
                masters=masters,
                rules=rules,
                zero_rules=zero_rules,
                memo=memo,
                unresolved_leaves=unresolved_leaves,
                cycles=cycles,
                visiting=set(),
            )
            if ok:
                resolved += 1
            else:
                unresolved += 1
                missing_kira.add(kira)
                local_missing.append(kira)

        if unresolved == 0:
            status_counts["fully_reduced"] += 1
        elif resolved:
            status_counts["partially_reduced"] += 1
        else:
            status_counts["missing"] += 1

        if local_missing and len(missing_examples) < 10:
            missing_examples.append({
                "native": list(native),
                "expansion_terms": len(expansion.terms),
                "missing": [list(v) for v in local_missing[:10]],
            })

    demanded_roots_missing_from_export = {
        key for key in unique_expanded
        if key not in masters and key not in zero_rules and key not in rules
    }

    summary = {
        "native_integrals_total": len(native_integrals),
        "status_counts": dict(sorted(status_counts.items())),
        "expanded_kira_terms_total": total_expanded_terms,
        "unique_expanded_kira_integrals": len(unique_expanded),
        "expected_unique_expanded_kira_integrals": EXPECTED_UNIQUE_KIRA,
        "unique_missing_kira_integrals": len(missing_kira),
        "max_isp_expansion_size": max_expansion_size,
        "kira_rules_loaded": len(rules) + len(zero_rules),
        "kira_zero_rules": len(zero_rules),
        "kira_masters_loaded": len(masters),
        "unique_nonmaster_rhs_dependencies": len(nonmaster_rhs),
        "unresolved_dependency_leaves": len(unresolved_leaves),
        "dependency_cycles": len(cycles),
        "demanded_roots_missing_from_export": len(demanded_roots_missing_from_export),
        "unresolved_dependency_examples": [list(v) for v in sorted(unresolved_leaves)[:20]],
        "cycle_examples": [list(v) for v in sorted(cycles)[:20]],
        "missing_examples": missing_examples,
        "rejected_examples": rejected_examples,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("fully reduced:", status_counts["fully_reduced"])
    print("partially reduced:", status_counts["partially_reduced"])
    print("missing:", status_counts["missing"])
    print("rejected:", status_counts["rejected"])
    print("expanded Kira terms:", total_expanded_terms)
    print("unique expanded Kira integrals:", len(unique_expanded))
    print("unique missing Kira integrals:", len(missing_kira))
    print("unresolved dependency leaves:", len(unresolved_leaves))
    print("dependency cycles:", len(cycles))
    print("demanded roots missing from export:", len(demanded_roots_missing_from_export))
    print("max ISP expansion size:", max_expansion_size)
    print("report:", OUTPUT_JSON)

    ok = (
        len(native_integrals) == EXPECTED_NATIVE
        and len(unique_expanded) == EXPECTED_UNIQUE_KIRA
        and status_counts["fully_reduced"] == EXPECTED_NATIVE
        and status_counts["partially_reduced"] == 0
        and status_counts["missing"] == 0
        and status_counts["rejected"] == 0
        and len(missing_kira) == 0
        and len(unresolved_leaves) == 0
        and len(cycles) == 0
        and len(demanded_roots_missing_from_export) == 0
    )
    if not ok:
        print("Q01 exact-944 final coverage FAIL")
        raise SystemExit(1)

    print("Q01 exact-944 final coverage PASS")


if __name__ == "__main__":
    main()
