"""Classify unresolved exact944 FORM dependency leaves by Kira sector.

This diagnostic never runs Kira.  It reconstructs the dependency graph from the
completed exact944 kira2form export, finds leaves that are neither exported
rules nor masters/explicit-zero rules, computes their Kira sector numbers, and
checks those sectors against sectormappings/Q01_full/trivialsector.

The purpose is deliberately narrow: establish how much of the apparent FORM
closure gap is explained exactly by Kira's saved trivial-sector information
before attempting to interpret symmetry/relation mapping files.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
EXACT = PROJECT / "exact944"
RESULTS = EXACT / "results" / "Q01_full"
FORM_FILE = RESULTS / "kira_q01_944_targets.inc"
MASTERS_FILE = RESULTS / "masters.final"
MAPPINGS = EXACT / "sectormappings" / "Q01_full"
TRIVIAL_FILE = MAPPINGS / "trivialsector"
NONTRIVIAL_FILE = MAPPINGS / "nonTrivialSector"
REPORT = PROJECT / "qedcalc_kira_q01_exact944_leaf_sector_diagnostic.json"
FAMILY = "Q01_full"
IndexTuple = tuple[int, ...]


def _load_sector_csv(path: Path) -> set[int]:
    text = path.read_text(encoding="utf-8").strip()
    values: set[int] = set()
    for raw in text.replace("\n", ",").split(","):
        token = raw.strip()
        if token:
            values.add(int(token))
    return values


def _sector(indices: IndexTuple) -> int:
    """Kira sector id: bit i is set iff propagator power a_i is positive."""
    return sum((1 << i) for i, power in enumerate(indices) if power > 0)


def main() -> None:
    print("QEDCalc Q01 exact944 unresolved-leaf sector diagnostic")
    print("mode: saved artifacts only; no Kira rerun")

    required = [FORM_FILE, MASTERS_FILE, TRIVIAL_FILE]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("ERROR: required artifact(s) missing:\n  " + "\n  ".join(missing))

    masters = set(load_master_indices(MASTERS_FILE, family=FAMILY))
    rules: dict[IndexTuple, tuple[IndexTuple, ...]] = {}
    zero_rules: set[IndexTuple] = set()

    for rule in iter_kira_form_rules(FORM_FILE, family=FAMILY):
        lhs = tuple(rule.lhs.indices)
        if lhs in rules or lhs in zero_rules:
            raise SystemExit(f"ERROR: duplicate FORM rule for {lhs}")
        rhs = tuple(tuple(term.integral.indices) for term in rule.terms)
        if rhs:
            rules[lhs] = rhs
        else:
            compact = "".join(rule.rhs_form.split())
            if compact in {"0", "+0", "-0"}:
                zero_rules.add(lhs)
            else:
                raise SystemExit(
                    "ERROR: non-integral nonzero FORM RHS encountered: "
                    f"{lhs} -> {rule.rhs_form[:160]}"
                )

    all_rhs = {child for rhs in rules.values() for child in rhs}
    leaves = {
        child for child in all_rhs
        if child not in masters and child not in zero_rules and child not in rules
    }

    trivial_sectors = _load_sector_csv(TRIVIAL_FILE)
    nontrivial_sectors = _load_sector_csv(NONTRIVIAL_FILE) if NONTRIVIAL_FILE.exists() else set()

    trivial_leaves = {leaf for leaf in leaves if _sector(leaf) in trivial_sectors}
    remaining = leaves - trivial_leaves

    leaf_sector_counts = Counter(_sector(leaf) for leaf in leaves)
    remaining_sector_counts = Counter(_sector(leaf) for leaf in remaining)
    remaining_marked_nontrivial = {
        leaf for leaf in remaining if _sector(leaf) in nontrivial_sectors
    }

    print("FORM rules loaded:", len(rules) + len(zero_rules))
    print("FORM explicit-zero rules:", len(zero_rules))
    print("masters loaded:", len(masters))
    print("unresolved leaves:", len(leaves))
    print("distinct unresolved sectors:", len(leaf_sector_counts))
    print("saved trivial sectors:", len(trivial_sectors))
    print("leaves in trivial sectors:", len(trivial_leaves))
    print("remaining leaves after trivial-sector classification:", len(remaining))
    print("remaining distinct sectors:", len(remaining_sector_counts))
    print("remaining leaves in saved nonTrivialSector:", len(remaining_marked_nontrivial))

    print("remaining sector counts (top 30):")
    for sector, count in remaining_sector_counts.most_common(30):
        print(f"  sector {sector}: {count}")

    report = {
        "form_rules_loaded": len(rules) + len(zero_rules),
        "form_zero_rules": len(zero_rules),
        "masters_loaded": len(masters),
        "unresolved_leaves": len(leaves),
        "distinct_unresolved_sectors": len(leaf_sector_counts),
        "saved_trivial_sectors": len(trivial_sectors),
        "leaves_in_trivial_sectors": len(trivial_leaves),
        "remaining_leaves": len(remaining),
        "remaining_distinct_sectors": len(remaining_sector_counts),
        "remaining_leaves_in_nontrivial_sector_file": len(remaining_marked_nontrivial),
        "remaining_sector_counts": [
            {"sector": sector, "count": count}
            for sector, count in sorted(remaining_sector_counts.items())
        ],
        "remaining_examples": [
            {"indices": list(leaf), "sector": _sector(leaf)}
            for leaf in sorted(remaining)[:50]
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("report:", REPORT)
    print("Q01 exact944 unresolved-leaf sector diagnostic PASS")


if __name__ == "__main__":
    main()
