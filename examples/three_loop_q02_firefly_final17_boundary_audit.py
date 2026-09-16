"""Validate the Q02 17-master union-reduction candidate under seed extensions.

The baseline candidate comes from the successful mandatory-union reduction at
r9s4d2.  Each boundary run reduces the same 110 union targets at one enlarged
seed and exports them to FORM.  The scientific stability test is whether all 17
candidate final forms remain masters in the enlarged reduction context; all
110 targets must also be classified as master/reduced/zero.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from examples.three_loop_q02_firefly_union_reduction import (
    AUDIT_DIR,
    MASTER_COPY as FINAL17_COPY,
    SOURCE_TARGET_FILE,
)
from three_loop.integral_family_classification import ROOT
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices
from three_loop.q02_kira_backend import Q02_KIRA_NAME, Q02_KIRA_TOP_SECTOR, Q02SeedLimits, export_q02_kira_project

IndexTuple = tuple[int, ...]
BASE_SEED = (9, 4, 2)
SEEDS: dict[str, tuple[int, int, int]] = {
    "r10s4d2": (10, 4, 2),
    "r9s5d2": (9, 5, 2),
    "r9s4d3": (9, 4, 3),
}
TARGET_BASENAME = "q02_firefly_final17_boundary_targets"
_TARGET_RE = re.compile(rf"^{re.escape(Q02_KIRA_NAME)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$")
_MASTER_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(Q02_KIRA_NAME)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]"
)


def _parse(text: str) -> IndexTuple:
    m = _TARGET_RE.match(text.strip())
    if not m:
        raise ValueError(f"unexpected integral syntax: {text!r}")
    values = tuple(int(x.strip()) for x in m.group("args").split(","))
    if len(values) != 12:
        raise ValueError("expected 12 indices")
    return values


def _fmt(v: IndexTuple) -> str:
    return f"{Q02_KIRA_NAME}[{','.join(str(x) for x in v)}]"


def _read_integrals(path: Path) -> set[IndexTuple]:
    if not path.is_file():
        raise FileNotFoundError(path)
    out: set[IndexTuple] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if raw:
            out.add(_parse(raw))
    return out


def _bounds(v: IndexTuple) -> tuple[int, int, int]:
    r = sum(x for x in v if x > 0)
    s = sum(-x for x in v if x < 0)
    d = sum(max(x - 1, 0) for x in v if x > 0)
    return r, s, d


def _project(seed: str) -> Path:
    return ROOT / "output" / f"kira_q02_full_firefly_final17_{seed}"


def _target_file(seed: str) -> Path:
    return _project(seed) / TARGET_BASENAME


def _job_file(seed: str) -> Path:
    return _project(seed) / "jobs.yaml"


def _log_file(seed: str) -> Path:
    return _project(seed) / f"q02_firefly_final17_{seed}.log"


def _audit_json(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q02_firefly_final17_{seed}_boundary_audit.json"


def _audit_txt(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q02_firefly_final17_{seed}_boundary_audit.txt"


def _clean(project: Path) -> None:
    for name in ("results", "sectormappings", "tmp", "firefly_saves", "ff_save", "firefly_saves_alt", "pyred"):
        path = project / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for pattern in ("*.log", "*.log.gz"):
        for path in project.glob(pattern):
            path.unlink()


def _render_jobs(seed: str) -> str:
    r, s, d = SEEDS[seed]
    return (
        "jobs:\n"
        "  - reduce_sectors:\n"
        "      reduce:\n"
        f"        - {{topologies: [{Q02_KIRA_NAME}], sectors: [{Q02_KIRA_TOP_SECTOR}], r: {r}, s: {s}, d: {d}}}\n"
        "      select_integrals:\n"
        "        select_mandatory_list:\n"
        f"          - [{Q02_KIRA_NAME},{TARGET_BASENAME}]\n"
        "      run_symmetries: true\n"
        "      run_initiate: true\n"
        "      run_triangular: false\n"
        "      run_back_substitution: false\n"
        "      run_firefly: true\n"
        "  - kira2form:\n"
        "      target:\n"
        f"        - [{Q02_KIRA_NAME},{TARGET_BASENAME}]\n"
    )


def prepare(seed: str) -> None:
    targets = _read_integrals(SOURCE_TARGET_FILE)
    final17 = _read_integrals(FINAL17_COPY)
    if len(targets) != 110:
        raise SystemExit(f"ERROR: expected 110 union targets, got {len(targets)}")
    if len(final17) != 17:
        raise SystemExit(f"ERROR: expected 17 candidate final masters, got {len(final17)}")
    if not final17.issubset(targets):
        raise SystemExit("ERROR: final17 candidate is not a subset of the 110 union targets")

    r_bound, s_bound, d_bound = SEEDS[seed]
    violating = []
    for v in targets:
        r, s, d = _bounds(v)
        if r > r_bound or s > s_bound or d > d_bound:
            violating.append((v, r, s, d))
    if violating:
        v, r, s, d = sorted(violating, key=lambda row: (row[1], row[2], row[3], row[0]))[0]
        raise SystemExit(
            f"ERROR: mandatory target outside {seed} bounds: {_fmt(v)} has r={r} s={s} d={d}"
        )

    project = _project(seed)
    project.mkdir(parents=True, exist_ok=True)
    _clean(project)
    export_q02_kira_project(project, limits=Q02SeedLimits(r_bound, s_bound, d_bound), back_substitution=False)
    _target_file(seed).write_text(
        "\n".join(_fmt(v) for v in sorted(targets)) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _job_file(seed).write_text(_render_jobs(seed), encoding="utf-8", newline="\n")

    print(f"QEDCalc Q02 final17 {seed} FireFly boundary prepare")
    print("baseline union seed: r9s4d2")
    print(f"boundary seed: {seed}")
    print("mandatory union targets: 110")
    print("candidate final masters: 17")
    print(f"project: {project}")
    print(f"QEDCalc Q02 final17 {seed} FireFly boundary prepare PASS")


def _find_form_export(seed: str) -> Path:
    result_dir = _project(seed) / "results" / Q02_KIRA_NAME
    preferred = result_dir / f"kira_{TARGET_BASENAME}.inc"
    if preferred.is_file():
        return preferred
    candidates = sorted(result_dir.glob("*.inc"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"FORM export not found under {result_dir}")


def finalize(seed: str) -> None:
    targets = _read_integrals(SOURCE_TARGET_FILE)
    final17 = _read_integrals(FINAL17_COPY)
    project = _project(seed)
    masters_path = project / "results" / Q02_KIRA_NAME / "masters.final"
    if not masters_path.is_file():
        raise SystemExit(f"ERROR: masters.final not found: {masters_path}")
    masters = set(load_master_indices(masters_path, family=Q02_KIRA_NAME))

    try:
        form = _find_form_export(seed)
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form, family=Q02_KIRA_NAME):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
        elif rule.is_zero:
            zeros.add(lhs)

    log_text = _log_file(seed).read_text(encoding="utf-8", errors="replace") if _log_file(seed).exists() else ""
    reported_masters = {
        tuple(int(x.strip()) for x in m.group("args").split(","))
        for m in _MASTER_RE.finditer(log_text)
    }
    master_evidence = masters | reported_masters

    def classify(v: IndexTuple) -> str:
        if v in master_evidence:
            return "master"
        if v in rules:
            return "reduced"
        if v in zeros:
            return "zero"
        return "unresolved"

    final_status = {v: classify(v) for v in final17}
    target_status = {v: classify(v) for v in targets}
    names = ("master", "reduced", "zero", "unresolved")
    final_counts = {name: sum(x == name for x in final_status.values()) for name in names}
    target_counts = {name: sum(x == name for x in target_status.values()) for name in names}
    reduced_final = sorted(v for v, status in final_status.items() if status == "reduced")
    zero_final = sorted(v for v, status in final_status.items() if status == "zero")
    unresolved_final = sorted(v for v, status in final_status.items() if status == "unresolved")
    unresolved_targets = sorted(v for v, status in target_status.items() if status == "unresolved")
    stable = final_counts["master"] == 17 and not reduced_final and not zero_final and not unresolved_final
    execution_pass = not unresolved_targets

    result = {
        "canonical_family": Q02_KIRA_NAME,
        "solver_backend": "firefly",
        "baseline_union_seed": {"r": 9, "s": 4, "d": 2},
        "boundary_seed_name": seed,
        "boundary_seed": dict(zip(("r", "s", "d"), SEEDS[seed])),
        "mandatory_union_targets": len(targets),
        "candidate_final_masters": len(final17),
        "masters_final_forms": len(masters),
        "form_export": str(form),
        "final17_status": final_counts,
        "union_target_status": target_counts,
        "final17_reduced_forms": [_fmt(v) for v in reduced_final],
        "final17_zero_forms": [_fmt(v) for v in zero_final],
        "final17_unresolved_forms": [_fmt(v) for v in unresolved_final],
        "union_unresolved_forms": [_fmt(v) for v in unresolved_targets],
        "basis_stable": stable,
        "execution_pass": execution_pass,
        "audit_pass": execution_pass,
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    _audit_json(seed).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        f"QEDCalc Q02 final17 {seed} FireFly boundary audit",
        "baseline union seed: r9s4d2",
        f"boundary seed: {seed}",
        "mandatory union targets: 110",
        f"masters.final forms: {len(masters)}",
        f"final17 status: {final_counts}",
        f"union target status: {target_counts}",
        f"basis stable: {stable}",
        f"execution pass: {execution_pass}",
        f"audit JSON: {_audit_json(seed)}",
        f"audit TXT: {_audit_txt(seed)}",
        f"QEDCalc Q02 final17 {seed} FireFly boundary audit " + ("PASS" if execution_pass else "FAIL"),
    ]
    _audit_txt(seed).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if reduced_final:
        for v in reduced_final[:12]:
            print("  previous final17 form now reduced:", _fmt(v))
    if zero_final:
        for v in zero_final[:12]:
            print("  previous final17 form now zero:", _fmt(v))
    if unresolved_targets:
        for v in unresolved_targets[:12]:
            print("  unresolved target:", _fmt(v))
        raise SystemExit(3)


def aggregate() -> None:
    errors: list[str] = []
    summaries: dict[str, object] = {}
    for seed in SEEDS:
        path = _audit_json(seed)
        if not path.is_file():
            errors.append(f"missing audit: {path}")
            continue
        row = json.loads(path.read_text(encoding="utf-8"))
        if not row.get("execution_pass"):
            errors.append(f"execution did not pass for {seed}")
        if not row.get("basis_stable"):
            errors.append(f"final17 basis not stable for {seed}")
        summaries[seed] = {
            "masters_final_forms": row.get("masters_final_forms"),
            "final17_status": row.get("final17_status"),
            "union_target_status": row.get("union_target_status"),
            "basis_stable": bool(row.get("basis_stable")),
        }

    stable = not errors and len(summaries) == len(SEEDS)
    out_json = AUDIT_DIR / "three_loop_q02_firefly_final17_boundary_aggregate_audit.json"
    out_txt = AUDIT_DIR / "three_loop_q02_firefly_final17_boundary_aggregate_audit.txt"
    result = {
        "canonical_family": Q02_KIRA_NAME,
        "candidate_master_basis_id": "Q02_final17",
        "baseline_union_seed": {"r": 9, "s": 4, "d": 2},
        "tested_boundary_seeds": summaries,
        "stable_under_tested_one_axis_extensions": stable,
        "errors": errors,
        "audit_pass": stable,
    }
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q02 final17 FireFly boundary aggregate audit",
        "candidate master basis: Q02_final17",
        "baseline union seed: r9s4d2",
    ]
    for seed in SEEDS:
        row = summaries.get(seed)
        lines.append(f"{seed}: MISSING AUDIT" if row is None else f"{seed}: masters.final={row['masters_final_forms']} final17={row['final17_status']} stable={row['basis_stable']}")
    lines += [
        f"stable under tested one-axis extensions: {stable}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
        "QEDCalc Q02 final17 FireFly boundary aggregate audit " + ("PASS" if stable else "FAIL"),
    ]
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 final17 FireFly boundary aggregate audit FAIL")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", choices=tuple(SEEDS))
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prepare", action="store_true")
    g.add_argument("--finalize", action="store_true")
    g.add_argument("--aggregate", action="store_true")
    args = p.parse_args()
    if args.aggregate:
        if args.seed is not None:
            p.error("--aggregate cannot be combined with --seed")
        aggregate()
    elif args.seed is None:
        p.error("--seed is required with --prepare/--finalize")
    elif args.prepare:
        prepare(args.seed)
    else:
        finalize(args.seed)


if __name__ == "__main__":
    main()
