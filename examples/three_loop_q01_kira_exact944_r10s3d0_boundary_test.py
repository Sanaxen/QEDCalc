"""Run/audit the first Q01 exact944 seed-boundary extension: r=10,s=3,d=0.

This is the first one-axis stability test beyond the saved r=9,s=3,d=0 scope.
It uses ordinary Kira triangular reduction + back substitution with Fermat;
FireFly is deliberately disabled.  The mandatory target list is the union of
all original exact944 demands and the finalized 60 master forms, so every final
form is explicitly classified in the enlarged reduction context.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_reducer import load_master_indices

IndexTuple = tuple[int, ...]
ORIGINAL_TARGETS = PROJECT / "q01_944_targets"
FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
TARGET_FILE = PROJECT / "q01_exact944_r10s3d0_boundary_targets"
JOB_FILE = PROJECT / "jobs_q01_exact944_r10s3d0_boundary.yaml"
LOG_FILE = PROJECT / "q01_exact944_r10s3d0_boundary.log"
ALT_DIR_NAME = "exact944_r10s3d0_fermat"
ALT_ROOT = PROJECT / ALT_DIR_NAME
OUTPUT_JSON = PROJECT / "q01_exact944_r10s3d0_boundary_audit.json"
OUTPUT_TXT = PROJECT / "q01_exact944_r10s3d0_boundary_audit.txt"
TOP_SECTOR = 511
R_BOUND, S_BOUND, D_BOUND = 10, 3, 0

_TARGET_RE = re.compile(rf"^{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$")
_MASTER_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
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
    return f"{FAMILY}[{','.join(str(x) for x in v)}]"


def _read_target_file(path: Path) -> set[IndexTuple]:
    if not path.exists():
        raise SystemExit(f"ERROR: target file not found: {path}")
    result: set[IndexTuple] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            result.add(_parse(raw.strip()))
    return result


def _load_final60() -> set[IndexTuple]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: final basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    if not data.get("pass"):
        raise SystemExit("ERROR: final basis JSON is not marked PASS")
    result: set[IndexTuple] = set()
    for row in data.get("basis_terms", []):
        raw = row.get("indices") if isinstance(row, dict) else None
        if isinstance(raw, list) and len(raw) == 12:
            result.add(tuple(int(v) for v in raw))
    if len(result) != 60:
        raise SystemExit(f"ERROR: expected final 60 forms, got {len(result)}")
    return result


def _bounds(v: IndexTuple) -> tuple[int, int, int]:
    r = sum(x for x in v if x > 0)
    s = sum(-x for x in v if x < 0)
    d = sum(max(x - 1, 0) for x in v if x > 0)
    return r, s, d


def generate() -> None:
    original = _read_target_file(ORIGINAL_TARGETS)
    if len(original) != 944:
        raise SystemExit(f"ERROR: expected 944 original targets, got {len(original)}")
    final60 = _load_final60()
    targets = original | final60

    violating = []
    for v in sorted(targets):
        r, s, d = _bounds(v)
        if r > R_BOUND or s > S_BOUND or d > D_BOUND:
            violating.append((v, r, s, d))
    if violating:
        v, r, s, d = violating[0]
        raise SystemExit(
            "ERROR: mandatory target lies outside planned r10s3d0 seed bounds: "
            f"{_fmt(v)} has r={r} s={s} d={d}"
        )

    TARGET_FILE.write_text(
        "\n".join(_fmt(v) for v in sorted(targets)) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    JOB_FILE.write_text(
        "jobs:\n"
        "  - reduce_sectors:\n"
        "      reduce:\n"
        f"        - {{topologies: [{FAMILY}], sectors: [{TOP_SECTOR}], r: {R_BOUND}, s: {S_BOUND}, d: {D_BOUND}}}\n"
        "      select_integrals:\n"
        "        select_mandatory_list:\n"
        f"          - [{FAMILY},{TARGET_FILE.name}]\n"
        "      run_symmetries: true\n"
        "      run_initiate: true\n"
        "      run_triangular: true\n"
        "      run_back_substitution: true\n"
        "      run_firefly: false\n"
        f"      alt_dir: {ALT_DIR_NAME}\n"
        "  - kira2form:\n"
        "      target:\n"
        f"        - [{FAMILY},{TARGET_FILE.name}]\n"
        f"      alt_dir: {ALT_DIR_NAME}\n",
        encoding="utf-8",
        newline="\n",
    )

    print("QEDCalc Q01 exact944 r10s3d0 seed-boundary generator")
    print("mode: ordinary triangular + back substitution; FireFly disabled")
    print("original exact944 demands:", len(original))
    print("final 60 forms:", len(final60))
    print("joint mandatory targets:", len(targets))
    print(f"seed bounds: r={R_BOUND} s={S_BOUND} d={D_BOUND}")
    print("top sector:", TOP_SECTOR)
    print("alt_dir:", ALT_DIR_NAME)
    print("generated target list:", TARGET_FILE)
    print("generated job:", JOB_FILE)
    print("Q01 exact944 r10s3d0 seed-boundary generation PASS")


def _find_export() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / f"kira_{TARGET_FILE.name}.inc"
    if preferred.exists():
        return preferred
    candidates = sorted(result_dir.glob("*.inc"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    raise SystemExit(f"ERROR: FORM export not found under {result_dir}")


def audit() -> None:
    original = _read_target_file(ORIGINAL_TARGETS)
    final60 = _load_final60()
    targets = _read_target_file(TARGET_FILE)
    expected_targets = original | final60
    if targets != expected_targets:
        raise SystemExit(
            "ERROR: saved boundary target list differs from original944 U final60: "
            f"saved={len(targets)} expected={len(expected_targets)}"
        )

    result_dir = ALT_ROOT / "results" / FAMILY
    masters_file = result_dir / "masters.final"
    if not masters_file.exists():
        raise SystemExit(f"ERROR: masters.final not found: {masters_file}")
    masters = set(load_master_indices(masters_file, family=FAMILY))

    form = _find_export()
    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form, family=FAMILY):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
        elif rule.is_zero:
            zeros.add(lhs)

    log_text = LOG_FILE.read_text(encoding="utf-8", errors="strict") if LOG_FILE.exists() else ""
    reported_masters = {
        tuple(int(x.strip()) for x in m.group("args").split(","))
        for m in _MASTER_RE.finditer(log_text)
    }
    master_evidence = masters | reported_masters
    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))

    def classify(v: IndexTuple) -> str:
        if v in master_evidence:
            return "master"
        if v in rules:
            return "reduced"
        if v in zeros:
            return "zero"
        return "unresolved"

    final_status = {v: classify(v) for v in final60}
    target_status = {v: classify(v) for v in targets}
    final_counts = {
        name: sum(status == name for status in final_status.values())
        for name in ("master", "reduced", "zero", "unresolved")
    }
    target_counts = {
        name: sum(status == name for status in target_status.values())
        for name in ("master", "reduced", "zero", "unresolved")
    }
    final_unresolved = sorted(v for v, status in final_status.items() if status == "unresolved")
    target_unresolved = sorted(v for v, status in target_status.items() if status == "unresolved")
    reduced_final = sorted(v for v, status in final_status.items() if status == "reduced")
    zero_final = sorted(v for v, status in final_status.items() if status == "zero")

    stable = final_counts["master"] == 60 and not reduced_final and not zero_final and not final_unresolved
    execution_pass = not target_unresolved and unreduced_zero

    summary = {
        "mode": "fresh Q01 exact944 r10s3d0 Kira/Fermat seed-boundary test",
        "seed_bounds": {"r": R_BOUND, "s": S_BOUND, "d": D_BOUND},
        "top_sector": TOP_SECTOR,
        "original_exact944_demands": len(original),
        "final_basis_forms": len(final60),
        "joint_mandatory_targets": len(targets),
        "masters_final_forms": len(masters),
        "kira_reported_master_forms": len(reported_masters),
        "form_export": str(form),
        "final60_status": final_counts,
        "joint_target_status": target_counts,
        "final60_reduced_forms": [_fmt(v) for v in reduced_final],
        "final60_zero_forms": [_fmt(v) for v in zero_final],
        "final60_unresolved_forms": [_fmt(v) for v in final_unresolved],
        "joint_unresolved_forms": [_fmt(v) for v in target_unresolved[:50]],
        "kira_unreduced_integrals_zero": unreduced_zero,
        "basis_stable_under_r_plus_1": stable,
        "execution_pass": execution_pass,
        "pass": execution_pass,
        "interpretation": (
            "execution_pass means every joint mandatory target was classified and Kira reported "
            "unreduced integrals: 0. basis_stable_under_r_plus_1 is the scientific result: true "
            "means all previous final 60 forms remain masters after enlarging r from 9 to 10; "
            "false means at least one previous form is reduced or zero in the enlarged scope."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 exact944 r10s3d0 seed-boundary audit",
        "",
        f"seed bounds: r={R_BOUND} s={S_BOUND} d={D_BOUND}",
        f"original exact944 demands: {len(original)}",
        f"final basis forms tested: {len(final60)}",
        f"joint mandatory targets: {len(targets)}",
        f"masters.final forms: {len(masters)}",
        f"final60 status: {final_counts}",
        f"joint target status: {target_counts}",
        f"Kira unreduced integrals = 0: {unreduced_zero}",
        f"basis stable under r+1: {stable}",
        "",
        summary["interpretation"],
    ]
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("QEDCalc Q01 exact944 r10s3d0 seed-boundary audit")
    print("joint mandatory targets:", len(targets))
    print("masters.final forms:", len(masters))
    print("final60 status:", final_counts)
    print("joint target status:", target_counts)
    print("Kira unreduced integrals = 0:", unreduced_zero)
    print("basis stable under r+1:", stable)
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if reduced_final:
        print("previous final forms now reduced:", len(reduced_final))
        for v in reduced_final[:12]:
            print("  reduced:", _fmt(v))
    if zero_final:
        print("previous final forms now zero:", len(zero_final))
        for v in zero_final[:12]:
            print("  zero:", _fmt(v))
    if target_unresolved:
        for v in target_unresolved[:12]:
            print("  unresolved:", _fmt(v))
        raise SystemExit(3)
    if not unreduced_zero:
        raise SystemExit(1)
    print("Q01 exact944 r10s3d0 seed-boundary audit PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "audit"))
    args = parser.parse_args()
    generate() if args.mode == "generate" else audit()


if __name__ == "__main__":
    main()
