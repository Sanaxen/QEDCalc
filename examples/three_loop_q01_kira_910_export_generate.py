"""Generate a Kira FORM-export job for the exact Q01 944-integral demand.

This script does not run Kira. It reads the saved Q01 demand plan, writes a
plain Kira integral list containing exactly the 944 unique demanded Kira
integrals, and writes jobs_export.yaml that exports only those integrals from
the already completed Q01_full reduction database.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
DEMAND_PLAN = ROOT / "output" / "kira_q01_910_demand_plan.json"
TARGET_FILE = PROJECT / "q01_944_targets"
EXPORT_JOB = PROJECT / "jobs_export.yaml"
FAMILY = "Q01_full"
EXPECTED_DEMAND = 944


def _load_demand_plan() -> dict[str, object]:
    if not DEMAND_PLAN.exists():
        raise SystemExit(
            "ERROR: Q01 demand plan not found: " + str(DEMAND_PLAN) + "\n"
            "Run run_three_loop_q01_kira_910_demand_plan.bat first."
        )
    try:
        data = json.loads(DEMAND_PLAN.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read Q01 demand plan: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("ERROR: malformed Q01 demand plan")
    return data


def _normalize_integrals(data: dict[str, object]) -> list[tuple[int, ...]]:
    raw = data.get("all_demanded_kira_integrals")
    if not isinstance(raw, list):
        raise SystemExit("ERROR: demand plan has no all_demanded_kira_integrals list")

    values: list[tuple[int, ...]] = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 12:
            raise SystemExit(f"ERROR: malformed Kira integral in demand plan: {item!r}")
        try:
            values.append(tuple(int(v) for v in item))
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"ERROR: malformed Kira integral in demand plan: {item!r}") from exc

    unique = list(dict.fromkeys(values))
    if len(values) != EXPECTED_DEMAND or len(unique) != EXPECTED_DEMAND:
        raise SystemExit(
            f"ERROR: expected exactly {EXPECTED_DEMAND} unique demanded Kira integrals; "
            f"got total={len(values)} unique={len(unique)}"
        )
    return unique


def _integral_text(indices: tuple[int, ...]) -> str:
    return f"{FAMILY}[" + ",".join(str(v) for v in indices) + "]"


def _render_export_job() -> str:
    return f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},q01_944_targets]\n      reconstruct_mass: false\n'''


def main() -> None:
    print("QEDCalc Q01 exact-demand Kira FORM export generator")
    print("mode: CONFIG ONLY; Kira is NOT run by this Python script")
    print("project:", PROJECT)

    if not PROJECT.exists():
        raise SystemExit("ERROR: Q01 full-demand Kira project not found: " + str(PROJECT))
    masters = PROJECT / "results" / FAMILY / "masters.final"
    if not masters.exists():
        raise SystemExit(
            "ERROR: completed Q01_full reduction result was not found: " + str(masters)
        )

    data = _load_demand_plan()
    integrals = _normalize_integrals(data)

    TARGET_FILE.write_text(
        "\n".join(_integral_text(v) for v in integrals) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    EXPORT_JOB.write_text(_render_export_job(), encoding="utf-8", newline="\n")

    target_lines = [line for line in TARGET_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(target_lines) != EXPECTED_DEMAND or len(set(target_lines)) != EXPECTED_DEMAND:
        raise SystemExit("ERROR: generated Q01 Kira target list audit failed")

    job = EXPORT_JOB.read_text(encoding="utf-8")
    required = [
        "kira2form:",
        "[Q01_full,q01_944_targets]",
        "reconstruct_mass: false",
    ]
    missing = [token for token in required if token not in job]
    if missing:
        raise SystemExit(f"ERROR: generated export job audit failed: {missing}")

    print("family:", FAMILY)
    print("exact Kira targets:", len(target_lines))
    print("generated:", TARGET_FILE)
    print("generated:", EXPORT_JOB)
    print("NOTE: no reduction is rerun; kira2form reads the completed database only.")
    print("Q01 exact-demand Kira FORM export generation PASS")


if __name__ == "__main__":
    main()
