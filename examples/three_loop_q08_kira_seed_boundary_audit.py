"""Run Q08/Q48 one-axis Kira seed-boundary master-basis audits.

The r7s3d0 baseline master list is the reference set. Boundary seeds may
produce additional masters; stability means that every baseline master remains
a master in each one-axis enlarged seed.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.q08_kira_backend import (
    Q08_KIRA_NAME,
    Q08_KIRA_TOP_SECTOR,
    Q08SeedLimits,
    export_q08_kira_project,
    q08_kira_manifest,
    validate_q08_kira_basis,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
BASELINE_MASTER_COPY = AUDIT_DIR / "q08_r7s3d0_masters.txt"
SEEDS = {
    "r8s3d0": Q08SeedLimits(8, 3, 0),
    "r7s4d0": Q08SeedLimits(7, 4, 0),
    "r7s3d1": Q08SeedLimits(7, 3, 1),
}


def _project(seed: str) -> Path:
    return ROOT / "output" / f"kira_q08_full_{seed}"


def _audit_json(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q08_kira_{seed}_boundary_audit.json"


def _audit_txt(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q08_kira_{seed}_boundary_audit.txt"


def _parse_master_text(text: str) -> list[str]:
    pattern = re.compile(rf"{re.escape(Q08_KIRA_NAME)}\s*\[[^\]]+\]")
    masters: list[str] = []
    seen: set[str] = set()
    for item in pattern.findall(text):
        normalized = re.sub(r"\s+", "", item)
        if normalized not in seen:
            seen.add(normalized)
            masters.append(normalized)
    return masters


def _load_baseline() -> list[str]:
    if not BASELINE_MASTER_COPY.is_file():
        raise FileNotFoundError(
            f"baseline master copy not found: {BASELINE_MASTER_COPY}; "
            "run run_three_loop_q08_kira_r7s3d0.bat first"
        )
    masters = _parse_master_text(
        BASELINE_MASTER_COPY.read_text(encoding="utf-8", errors="replace")
    )
    if len(masters) != 12:
        raise ValueError(f"expected 12 Q08 baseline masters, found {len(masters)}")
    return masters


def _clean_runtime_outputs(project: Path) -> list[str]:
    removed: list[str] = []
    for name in (
        "results",
        "sectormappings",
        "tmp",
        "firefly_saves",
        "ff_save",
        "firefly_saves_alt",
        "pyred",
    ):
        path = project / name
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(str(path))
        elif path.exists():
            path.unlink()
            removed.append(str(path))
    for pattern in ("*.log", "*.log.gz"):
        for path in project.glob(pattern):
            path.unlink()
            removed.append(str(path))
    return removed


def prepare(seed: str) -> None:
    limits = SEEDS[seed]
    baseline = _load_baseline()
    basis = validate_q08_kira_basis()
    manifest = q08_kira_manifest(limits)
    errors: list[str] = []

    if basis.get("coefficient_matrix_rank") != 12 or not basis.get("full_rank"):
        errors.append(f"Q08 basis is not full rank: {basis}")
    if manifest.get("top_sector") != Q08_KIRA_TOP_SECTOR:
        errors.append(f"Q08 top sector changed: {manifest.get('top_sector')}")
    expected_limits = {"r": limits.r, "s": limits.s, "d": limits.d}
    if manifest.get("seed_limits") != expected_limits:
        errors.append(
            f"Q08 {seed} seed manifest mismatch: "
            f"{manifest.get('seed_limits')} != {expected_limits}"
        )
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(f"QEDCalc Q08 {seed} boundary prepare FAIL")

    project = _project(seed)
    project.mkdir(parents=True, exist_ok=True)
    removed = _clean_runtime_outputs(project)
    export_q08_kira_project(project, limits=limits, back_substitution=True)

    print(f"QEDCalc Q08 {seed} boundary prepare")
    print(f"canonical family: {Q08_KIRA_NAME}")
    print("covered diagrams: ['Q08', 'Q48']")
    print(f"top sector: {Q08_KIRA_TOP_SECTOR}")
    print(f"seed: {seed}")
    print(f"baseline masters: {len(baseline)}")
    print(f"project: {project}")
    print(f"stale runtime entries removed: {len(removed)}")
    print("back substitution: enabled")
    print(f"QEDCalc Q08 {seed} boundary prepare PASS")


def finalize(seed: str) -> None:
    baseline = _load_baseline()
    project = _project(seed)
    errors: list[str] = []
    candidates = sorted(project.rglob("masters.final"), key=lambda path: str(path))

    if not candidates:
        errors.append(f"no masters.final found under {project}")
        masters_path = None
        masters: list[str] = []
    else:
        if len(candidates) != 1:
            errors.append(
                "multiple masters.final files found: "
                + ", ".join(str(path) for path in candidates)
            )
        masters_path = candidates[0]
        masters = _parse_master_text(
            masters_path.read_text(encoding="utf-8", errors="replace")
        )
        if not masters:
            errors.append(f"no {Q08_KIRA_NAME}[...] masters parsed from {masters_path}")

    boundary_set = set(masters)
    missing = [master for master in baseline if master not in boundary_set]
    retained = len(baseline) - len(missing)
    subset = not missing
    if not subset:
        errors.append(
            f"baseline master set is not contained in {seed}: "
            f"{len(missing)} of {len(baseline)} baseline masters missing"
        )

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit = {
        "canonical_family": Q08_KIRA_NAME,
        "covered_diagrams": ["Q08", "Q48"],
        "baseline_seed": {"r": 7, "s": 3, "d": 0},
        "boundary_seed_name": seed,
        "boundary_seed": {
            "r": SEEDS[seed].r,
            "s": SEEDS[seed].s,
            "d": SEEDS[seed].d,
        },
        "top_sector": Q08_KIRA_TOP_SECTOR,
        "project_dir": str(project),
        "masters_final": str(masters_path) if masters_path else None,
        "masters_final_candidate_count": len(candidates),
        "baseline_master_copy": str(BASELINE_MASTER_COPY),
        "baseline_master_count": len(baseline),
        "boundary_master_count": len(masters),
        "retained_baseline_master_count": retained,
        "missing_baseline_masters": missing,
        "baseline_subset_of_boundary": subset,
        "stability_interpretation": (
            "A boundary seed may introduce extra masters. Stability requires every "
            "r7s3d0 baseline master to remain present under the tested one-axis extension."
        ),
        "errors": errors,
        "audit_pass": not errors,
    }
    _audit_json(seed).write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        f"QEDCalc Q08 {seed} seed-boundary audit",
        f"canonical family: {Q08_KIRA_NAME}",
        "baseline seed: r7s3d0",
        f"boundary seed: {seed}",
        f"baseline masters: {len(baseline)}",
        f"boundary masters: {len(masters)}",
        f"retained baseline masters: {retained}/{len(baseline)}",
        f"missing baseline masters: {len(missing)}",
        f"baseline subset of boundary: {subset}",
        f"masters.final: {audit['masters_final']}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {_audit_json(seed)}",
        f"audit TXT: {_audit_txt(seed)}",
        f"QEDCalc Q08 {seed} seed-boundary audit "
        + ("PASS" if not errors else "FAIL"),
    ]
    _audit_txt(seed).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if missing:
        print("Missing baseline masters:")
        for master in missing:
            print("  ", master)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(f"QEDCalc Q08 {seed} seed-boundary audit FAIL")


def aggregate() -> None:
    baseline = _load_baseline()
    errors: list[str] = []
    summaries: dict[str, dict[str, object]] = {}

    for seed in SEEDS:
        path = _audit_json(seed)
        if not path.is_file():
            errors.append(f"missing boundary audit JSON for {seed}: {path}")
            continue
        try:
            audit = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot read boundary audit JSON for {seed}: {exc}")
            continue
        if audit.get("boundary_seed_name") != seed:
            errors.append(
                f"boundary audit seed mismatch for {seed}: "
                f"{audit.get('boundary_seed_name')}"
            )
        if audit.get("baseline_master_count") != len(baseline):
            errors.append(f"baseline count mismatch for {seed}")
        if not audit.get("audit_pass"):
            errors.append(f"boundary audit did not pass for {seed}")
        if not audit.get("baseline_subset_of_boundary"):
            errors.append(f"baseline master subset test failed for {seed}")
        summaries[seed] = {
            "master_count": audit.get("boundary_master_count"),
            "retained_baseline_master_count": audit.get(
                "retained_baseline_master_count"
            ),
            "missing_baseline_master_count": len(
                audit.get("missing_baseline_masters") or []
            ),
            "baseline_subset_of_boundary": bool(
                audit.get("baseline_subset_of_boundary")
            ),
            "audit_pass": bool(audit.get("audit_pass")),
        }

    stable = not errors and len(summaries) == len(SEEDS)
    aggregate_json = AUDIT_DIR / "three_loop_q08_kira_seed_boundary_audit.json"
    aggregate_txt = AUDIT_DIR / "three_loop_q08_kira_seed_boundary_audit.txt"
    result = {
        "canonical_family": Q08_KIRA_NAME,
        "covered_diagrams": ["Q08", "Q48"],
        "baseline_seed": {"r": 7, "s": 3, "d": 0},
        "baseline_master_count": len(baseline),
        "boundary_seeds": summaries,
        "stable_under_tested_one_axis_seed_extensions": stable,
        "master_basis_status": (
            "stable_under_tested_one_axis_seed_extensions"
            if stable
            else "boundary_review_required"
        ),
        "promotion_note": (
            "This audit does not itself assign a final master_basis_id; "
            "promote only after local PASS review."
        ),
        "errors": errors,
        "audit_pass": stable,
    }
    aggregate_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "QEDCalc Q08 seed-boundary aggregate audit",
        f"canonical family: {Q08_KIRA_NAME}",
        "baseline seed: r7s3d0",
        f"baseline masters: {len(baseline)}",
    ]
    for seed in SEEDS:
        summary = summaries.get(seed)
        if summary is None:
            lines.append(f"{seed}: MISSING AUDIT")
        else:
            lines.append(
                f"{seed}: masters={summary['master_count']} "
                f"retained={summary['retained_baseline_master_count']}/{len(baseline)} "
                f"missing={summary['missing_baseline_master_count']} "
                f"subset={summary['baseline_subset_of_boundary']}"
            )
    lines.extend(
        [
            f"stable under tested one-axis seed extensions: {stable}",
            f"internal audit errors: {len(errors)}",
            f"audit JSON: {aggregate_json}",
            f"audit TXT: {aggregate_txt}",
            "QEDCalc Q08 seed-boundary aggregate audit "
            + ("PASS" if stable else "FAIL"),
        ]
    )
    aggregate_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q08 seed-boundary aggregate audit FAIL")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", choices=tuple(SEEDS))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--finalize", action="store_true")
    action.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()

    if args.aggregate:
        if args.seed is not None:
            parser.error("--aggregate must not be combined with --seed")
        aggregate()
        return

    if args.seed is None:
        parser.error("--seed is required with --prepare/--finalize")
    if args.prepare:
        prepare(args.seed)
    else:
        finalize(args.seed)


if __name__ == "__main__":
    main()
