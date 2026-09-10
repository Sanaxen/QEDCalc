"""Audit the saved Q01 910-integral set against the completed full-demand Kira export.

This script does not regenerate the expensive projected trace or rerun Kira.
It loads the canonical 910 native QEDCalc integrals, expands native D10-D12
linear ISP powers into the Q01_full Kira quadratic basis, and verifies that
every resulting Kira integral is reducible through the exact-demand FORM
export to masters (possibly through intermediate exported rules).
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
FORM_FILE = PROJECT / "results" / "Q01_full" / "kira_q01_944_targets.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_full" / "masters.final"
NATIVE_TXT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT_JSON = PROJECT / "qedcalc_kira_q01_910_full_coverage.json"
FAMILY = "Q01_full"
EXPECTED_NATIVE = 910
EXPECTED_UNIQUE_KIRA = 944

_INTEGRAL_RE = re.compile(r"\bI\(\s*([-+]?\d+(?:\s*,\s*[-+]?\d+){11})\s*\)")
IndexTuple = tuple[int, ...]


def _load_native_txt(path: Path) -> tuple[IndexTuple, ...]:
    if not path.exists():
        raise SystemExit(f"ERROR: native Q01 integral artifact not found: {path}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SystemExit(f"ERROR: cannot read native Q01 integral artifact: {exc}") from exc

    parsed: list[IndexTuple] = []
    for line in lines:
        match = _INTEGRAL_RE.search(line)
        if match is None:
            continue
        parsed.append(tuple(int(v.strip()) for v in match.group(1).split(",")))

    unique = tuple(dict.fromkeys(parsed))
    if len(parsed) != EXPECTED_NATIVE or len(unique) != EXPECTED_NATIVE:
        raise SystemExit(
            "ERROR: native TXT does not contain exactly "
            f"{EXPECTED_NATIVE} unique integrals (parsed={len(parsed)}, unique={len(unique)})"
        )
    return unique


def _load_rule_dependencies() -> tuple[dict[IndexTuple, tuple[IndexTuple, ...]], set[IndexTuple]]:
    """Load the FORM export structurally without requiring master-only RHS rules.

    kira2form may emit a target rule whose RHS still references another exported
    reduction rule.  That is valid as long as the dependency chain terminates in
    masters (or zero).  Coefficients are irrelevant for this coverage audit.
    """
    masters = set(load_master_indices(MASTERS_FILE, family=FAMILY))
    dependencies: dict[IndexTuple, tuple[IndexTuple, ...]] = {}

    for rule in iter_kira_form_rules(FORM_FILE, family=FAMILY):
        lhs = tuple(rule.lhs.indices)
        if lhs in dependencies:
            raise ValueError(f"duplicate Kira reduction rule for {lhs}")
        dependencies[lhs] = tuple(tuple(term.integral.indices) for term in rule.terms)

    return dependencies, masters


def _resolve_to_masters(
    key: IndexTuple,
    dependencies: dict[IndexTuple, tuple[IndexTuple, ...]],
    masters: set[IndexTuple],
    memo: dict[IndexTuple, bool],
    active: set[IndexTuple],
) -> bool:
    """Return True iff one integral's exported dependency chain closes on masters/zero."""
    if key in masters:
        return True
    cached = memo.get(key)
    if cached is not None:
        return cached
    if key in active:
        memo[key] = False
        return False
    if key not in dependencies:
        memo[key] = False
        return False

    active.add(key)
    rhs = dependencies[key]
    # Empty RHS is a zero rule and therefore fully resolved.
    ok = all(_resolve_to_masters(dep, dependencies, masters, memo, active) for dep in rhs)
    active.remove(key)
    memo[key] = ok
    return ok


def main() -> None:
    print("QEDCalc Q01 full-demand Kira coverage audit")
    print("mode: saved artifacts only; no projected trace or Kira reduction is rerun")
    print("project:", PROJECT)

    if not FORM_FILE.exists():
        raise SystemExit(f"ERROR: exact-demand FORM export not found: {FORM_FILE}")
    if not MASTERS_FILE.exists():
        raise SystemExit(f"ERROR: masters.final not found: {MASTERS_FILE}")

    native_integrals = _load_native_txt(NATIVE_TXT)
    print("native integrals total:", len(native_integrals))

    dependencies, masters = _load_rule_dependencies()
    memo: dict[IndexTuple, bool] = {}
    print("Kira rules loaded:", len(dependencies))
    print("Kira masters loaded:", len(masters))

    nonmaster_rhs = {
        dep
        for rhs in dependencies.values()
        for dep in rhs
        if dep not in masters
    }
    print("unique non-master RHS dependencies:", len(nonmaster_rhs))

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
            if _resolve_to_masters(kira, dependencies, masters, memo, set()):
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
            missing_examples.append(
                {
                    "native": list(native),
                    "expansion_terms": len(expansion.terms),
                    "missing": [list(v) for v in local_missing[:10]],
                }
            )

    unresolved_dependencies = sorted(
        dep for dep in nonmaster_rhs
        if not _resolve_to_masters(dep, dependencies, masters, memo, set())
    )

    summary = {
        "native_integrals_total": len(native_integrals),
        "status_counts": dict(sorted(status_counts.items())),
        "expanded_kira_terms_total": total_expanded_terms,
        "unique_expanded_kira_integrals": len(unique_expanded),
        "expected_unique_expanded_kira_integrals": EXPECTED_UNIQUE_KIRA,
        "unique_missing_kira_integrals": len(missing_kira),
        "max_isp_expansion_size": max_expansion_size,
        "kira_rules_loaded": len(dependencies),
        "kira_masters_loaded": len(masters),
        "unique_nonmaster_rhs_dependencies": len(nonmaster_rhs),
        "unresolved_nonmaster_rhs_dependencies": len(unresolved_dependencies),
        "unresolved_dependency_examples": [list(v) for v in unresolved_dependencies[:10]],
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
    print("unresolved non-master RHS dependencies:", len(unresolved_dependencies))
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
        and len(unresolved_dependencies) == 0
    )
    if not ok:
        print("Q01 full-demand Kira 910-integral coverage FAIL")
        raise SystemExit(1)

    print("Q01 full-demand Kira 910-integral coverage PASS")


if __name__ == "__main__":
    main()
