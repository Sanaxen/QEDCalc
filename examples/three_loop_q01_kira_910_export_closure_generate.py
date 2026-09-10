"""Grow the Q01 kira2form target list until all non-master RHS dependencies are exported.

This script never reruns reduction.  It reads the original 944-demand list and
whichever closure FORM export already exists, finds RHS integrals that are
neither masters nor exported LHS rules, and adds them to the next kira2form
target list.  Exit code 10 means another kira2form export pass is required;
exit code 0 means the exported rule set is dependency-closed.
"""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
DEMAND_PLAN = ROOT / "output" / "kira_q01_910_demand_plan.json"
TARGET_FILE = PROJECT / "q01_closure_targets"
EXPORT_JOB = PROJECT / "jobs_export_closure.yaml"
INITIAL_FORM = PROJECT / "results" / "Q01_full" / "kira_q01_944_targets.inc"
CLOSURE_FORM = PROJECT / "results" / "Q01_full" / "kira_q01_closure_targets.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_full" / "masters.final"
STATE_FILE = PROJECT / "q01_export_closure_state.json"
FAMILY = "Q01_full"
EXPECTED_DEMAND = 944


def _integral_text(indices: tuple[int, ...]) -> str:
    return f"{FAMILY}[" + ",".join(str(v) for v in indices) + "]"


def _load_original_targets() -> list[tuple[int, ...]]:
    data = json.loads(DEMAND_PLAN.read_text(encoding="utf-8"))
    raw = data.get("all_demanded_kira_integrals")
    if not isinstance(raw, list):
        raise SystemExit("ERROR: demand plan has no all_demanded_kira_integrals list")
    values = [tuple(int(v) for v in item) for item in raw]
    unique = list(dict.fromkeys(values))
    if len(values) != EXPECTED_DEMAND or len(unique) != EXPECTED_DEMAND:
        raise SystemExit(
            f"ERROR: expected {EXPECTED_DEMAND} unique demand integrals; "
            f"got total={len(values)} unique={len(unique)}"
        )
    return unique


def _read_existing_target_file() -> list[tuple[int, ...]]:
    if not TARGET_FILE.exists():
        return []
    values: list[tuple[int, ...]] = []
    prefix = FAMILY + "["
    for raw in TARGET_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or not line.startswith(prefix) or not line.endswith("]"):
            continue
        payload = line[len(prefix):-1]
        values.append(tuple(int(part.strip()) for part in payload.split(",")))
    return list(dict.fromkeys(values))


def _scan_form(path: Path, masters: set[tuple[int, ...]]) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]]]:
    lhs: set[tuple[int, ...]] = set()
    rhs_nonmasters: set[tuple[int, ...]] = set()
    for rule in iter_kira_form_rules(path, family=FAMILY):
        lhs.add(tuple(rule.lhs.indices))
        for term in rule.terms:
            rhs = tuple(term.integral.indices)
            if rhs not in masters:
                rhs_nonmasters.add(rhs)
    return lhs, rhs_nonmasters


def _render_export_job() -> str:
    return f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},q01_closure_targets]\n      reconstruct_mass: false\n'''


def main() -> None:
    print("QEDCalc Q01 Kira FORM dependency-closure target generator")
    print("mode: export planning only; reduction is NOT rerun")

    if not DEMAND_PLAN.exists() or not MASTERS_FILE.exists() or not INITIAL_FORM.exists():
        raise SystemExit("ERROR: required completed Q01 demand/export artifacts are missing")

    original = _load_original_targets()
    current = _read_existing_target_file()
    targets = list(dict.fromkeys(original + current))
    masters = set(load_master_indices(MASTERS_FILE, family=FAMILY))

    form_path = CLOSURE_FORM if CLOSURE_FORM.exists() else INITIAL_FORM
    lhs, rhs_nonmasters = _scan_form(form_path, masters)
    unresolved = sorted(rhs_nonmasters - lhs)

    before = len(targets)
    targets = list(dict.fromkeys(targets + unresolved))
    added = len(targets) - before

    TARGET_FILE.write_text(
        "\n".join(_integral_text(v) for v in targets) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    EXPORT_JOB.write_text(_render_export_job(), encoding="utf-8", newline="\n")

    state = {
        "form_scanned": str(form_path),
        "original_demand": len(original),
        "masters": len(masters),
        "exported_lhs_rules": len(lhs),
        "unique_nonmaster_rhs_dependencies": len(rhs_nonmasters),
        "unresolved_rhs_dependencies": len(unresolved),
        "targets_before": before,
        "targets_after": len(targets),
        "targets_added": added,
    }
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    print("FORM scanned:", form_path)
    print("exported LHS rules:", len(lhs))
    print("non-master RHS dependencies:", len(rhs_nonmasters))
    print("unresolved RHS dependencies:", len(unresolved))
    print("closure targets:", len(targets))
    print("new targets added:", added)

    if unresolved:
        print("Q01 Kira FORM dependency closure NEEDS EXPORT")
        raise SystemExit(10)

    print("Q01 Kira FORM dependency closure COMPLETE")


if __name__ == "__main__":
    main()
