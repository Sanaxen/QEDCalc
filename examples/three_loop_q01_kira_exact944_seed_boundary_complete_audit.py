"""Aggregate the completed Q01 exact944 one-axis seed-boundary audits.

This check is intentionally cheap: it does not run Kira.  It only verifies the
saved audit JSON files for the validated r+1, s+1 and d+1 extensions and writes
one summary artifact declaring the seed-boundary validation complete.
"""
from __future__ import annotations

import json
from pathlib import Path

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

AUDITS = {
    "r_plus_1": {
        "path": PROJECT / "q01_exact944_r10s3d0_boundary_audit.json",
        "stability_key": "basis_stable_under_r_plus_1",
        "bounds": {"r": 10, "s": 3, "d": 0},
        "solver": "Kira/Fermat",
    },
    "s_plus_1": {
        "path": PROJECT / "q01_exact944_r9s4d0_firefly_boundary_audit.json",
        "stability_key": "basis_stable_under_s_plus_1",
        "bounds": {"r": 9, "s": 4, "d": 0},
        "solver": "Kira/FireFly",
    },
    "d_plus_1": {
        "path": PROJECT / "q01_exact944_r9s3d1_firefly_boundary_audit.json",
        "stability_key": "basis_stable_under_d_plus_1",
        "bounds": {"r": 9, "s": 3, "d": 1},
        "solver": "Kira/FireFly",
    },
}

OUTPUT_JSON = PROJECT / "q01_exact944_seed_boundary_complete_audit.json"
OUTPUT_TXT = PROJECT / "q01_exact944_seed_boundary_complete_audit.txt"
EXPECTED_FINAL60 = {"master": 60, "reduced": 0, "zero": 0, "unresolved": 0}
EXPECTED_JOINT = {"master": 60, "reduced": 874, "zero": 37, "unresolved": 0}
EXPECTED_TARGETS = 971


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"ERROR: required seed-boundary audit JSON not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: audit JSON is not an object: {path}")
    return data


def main() -> None:
    results: dict[str, dict] = {}
    failures: list[str] = []

    for axis, spec in AUDITS.items():
        data = _load(spec["path"])
        checks = {
            "audit_pass": data.get("pass") is True,
            "execution_pass": data.get("execution_pass") is True,
            "kira_unreduced_integrals_zero": data.get("kira_unreduced_integrals_zero") is True,
            "basis_stable": data.get(spec["stability_key"]) is True,
            "joint_mandatory_targets_971": data.get("joint_mandatory_targets") == EXPECTED_TARGETS,
            "final60_status_exact": data.get("final60_status") == EXPECTED_FINAL60,
            "joint_target_status_exact": data.get("joint_target_status") == EXPECTED_JOINT,
            "seed_bounds_exact": data.get("seed_bounds") == spec["bounds"],
        }
        axis_pass = all(checks.values())
        if not axis_pass:
            for name, ok in checks.items():
                if not ok:
                    failures.append(f"{axis}: {name}")
        results[axis] = {
            "path": str(spec["path"]),
            "solver": spec["solver"],
            "seed_bounds": spec["bounds"],
            "masters_final_forms": data.get("masters_final_forms"),
            "checks": checks,
            "pass": axis_pass,
        }

    complete = not failures and all(row["pass"] for row in results.values())
    summary = {
        "mode": "Q01 exact944 completed one-axis seed-boundary validation",
        "baseline_seed_bounds": {"r": 9, "s": 3, "d": 0},
        "joint_mandatory_targets": EXPECTED_TARGETS,
        "expected_final60_status": EXPECTED_FINAL60,
        "expected_joint_target_status": EXPECTED_JOINT,
        "axes": results,
        "all_three_axes_stable": complete,
        "pass": complete,
        "failures": failures,
        "interpretation": (
            "PASS means the finalized 60-form master basis remains unchanged when the saved "
            "r=9,s=3,d=0 seed boundary is enlarged independently along r, s and d, while all "
            "971 mandatory targets remain fully classified with Kira reporting zero unreduced integrals."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 exact944 seed-boundary complete audit",
        "",
        "baseline seed bounds: r=9 s=3 d=0",
        f"joint mandatory targets: {EXPECTED_TARGETS}",
        "",
    ]
    for axis in ("r_plus_1", "s_plus_1", "d_plus_1"):
        row = results[axis]
        b = row["seed_bounds"]
        lines.append(
            f"{axis}: r={b['r']} s={b['s']} d={b['d']}  solver={row['solver']}  "
            f"masters.final={row['masters_final_forms']}  PASS={row['pass']}"
        )
    lines += [
        "",
        f"all three axes stable: {complete}",
        "",
        summary["interpretation"],
    ]
    if failures:
        lines += ["", "failed checks:"] + [f"  - {item}" for item in failures]
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc Q01 exact944 seed-boundary complete audit")
    for axis in ("r_plus_1", "s_plus_1", "d_plus_1"):
        row = results[axis]
        b = row["seed_bounds"]
        print(
            f"{axis}: r={b['r']} s={b['s']} d={b['d']} "
            f"solver={row['solver']} masters.final={row['masters_final_forms']} PASS={row['pass']}"
        )
    print("all three axes stable:", complete)
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if not complete:
        for item in failures:
            print("  FAIL:", item)
        raise SystemExit(1)
    print("Q01 exact944 seed-boundary complete audit PASS")


if __name__ == "__main__":
    main()
