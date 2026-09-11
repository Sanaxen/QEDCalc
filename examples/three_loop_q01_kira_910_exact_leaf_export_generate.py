"""Generate a cheap kira2form diagnostic for unresolved exact944 RHS leaves.

This script never reruns triangular reduction or back substitution.  It parses
the completed exact944 FORM export, finds RHS integrals that are neither
exported rules nor masters/explicit-zero rules, writes those unresolved leaves
as a Kira target list, and prepares a kira2form-only job against alt_dir=exact944.

If Kira reports these leaves as unreduced, they were not solved in the existing
exact944 database and must be included in a future mandatory reduction set.
"""
from __future__ import annotations

from pathlib import Path

from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
EXACT_RESULTS = PROJECT / "exact944" / "results" / "Q01_full"
FORM_FILE = EXACT_RESULTS / "kira_q01_944_targets.inc"
MASTERS_FILE = EXACT_RESULTS / "masters.final"
TARGET_FILE = PROJECT / "q01_exact944_unresolved_leaves"
JOB_FILE = PROJECT / "jobs_exact944_leaf_export.yaml"
FAMILY = "Q01_full"
ALT_DIR = "exact944"
EXPECTED_LEAVES = 1305
IndexTuple = tuple[int, ...]


def _collect_leaves() -> tuple[IndexTuple, ...]:
    masters = set(load_master_indices(MASTERS_FILE, family=FAMILY))
    rules: dict[IndexTuple, tuple[IndexTuple, ...]] = {}
    zero_rules: set[IndexTuple] = set()

    for rule in iter_kira_form_rules(FORM_FILE, family=FAMILY):
        lhs = tuple(rule.lhs.indices)
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
    leaves = tuple(sorted(
        child for child in all_rhs
        if child not in masters and child not in zero_rules and child not in rules
    ))
    return leaves


def _format_target(indices: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in indices)}]"


def _render_job() -> str:
    return f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},q01_exact944_unresolved_leaves]\n      reconstruct_mass: false\n      alt_dir: {ALT_DIR}\n'''


def main() -> None:
    print("QEDCalc Q01 exact944 unresolved-leaf export diagnostic generator")
    print("mode: kira2form only; triangular/back substitution are NOT rerun")

    for path in (PROJECT, FORM_FILE, MASTERS_FILE):
        if not path.exists():
            raise SystemExit(f"ERROR: required artifact not found: {path}")

    leaves = _collect_leaves()
    print("unresolved leaves found:", len(leaves))
    if len(leaves) != EXPECTED_LEAVES:
        raise SystemExit(
            f"ERROR: expected {EXPECTED_LEAVES} unresolved leaves from the saved exact944 export; "
            f"got {len(leaves)}"
        )

    TARGET_FILE.write_text(
        "\n".join(_format_target(v) for v in leaves) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    JOB_FILE.write_text(_render_job(), encoding="utf-8", newline="\n")

    print("target file:", TARGET_FILE)
    print("target integrals:", len(leaves))
    print("generated:", JOB_FILE)
    print("alt_dir:", ALT_DIR)
    print("Q01 exact944 unresolved-leaf export diagnostic generation PASS")


if __name__ == "__main__":
    main()
