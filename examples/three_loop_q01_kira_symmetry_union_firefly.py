"""Run Q01 FireFly on the validated closure-wave-1 targets plus symmetry gaps.

This avoids the supplemental-only black-box validation failure by preserving the
previously successful closure-wave-1 mandatory target set and adding only the
symmetry-derived unresolved targets.  Everything is written to a fresh alt_dir;
existing successful FireFly results are never modified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT
from three_loop.kira_form_parser import iter_kira_form_rules

IndexTuple = tuple[int, ...]
BASE_TARGET_FILE = PROJECT / "q01_exact944_closure1_targets"
SOURCE_AUDIT = PROJECT / "q01_symmetry_closure_firefly_export_audit.json"
UNION_TARGET_FILE = PROJECT / "q01_exact944_closure1_plus_symmetry_targets"
SUPPLEMENT_TARGET_FILE = PROJECT / "q01_symmetry_union_export_targets"
REDUCE_JOB = PROJECT / "jobs_q01_exact944_closure1_plus_symmetry_firefly.yaml"
EXPORT_JOB = PROJECT / "jobs_q01_symmetry_union_firefly_export.yaml"
LOG_FILE = PROJECT / "q01_exact944_closure1_plus_symmetry_firefly.log"
EXPORT_LOG = PROJECT / "q01_symmetry_union_firefly_export.log"
ALT_DIR_NAME = "exact944closure1_plus_symmetry_firefly"
ALT_ROOT = PROJECT / ALT_DIR_NAME
OUTPUT_JSON = PROJECT / "q01_symmetry_union_firefly_audit.json"
TOP_SECTOR = 511

_TARGET_RE = re.compile(rf"^{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$")
_MASTER_RE = re.compile(rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]")


def _parse(text: str) -> IndexTuple:
    m = _TARGET_RE.match(text.strip())
    if not m:
        raise ValueError(f"unexpected integral syntax: {text!r}")
    vals = tuple(int(x.strip()) for x in m.group("args").split(","))
    if len(vals) != 12:
        raise ValueError("expected 12 indices")
    return vals


def _fmt(v: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(x) for x in v)}]"


def _bounds(v: IndexTuple) -> tuple[int, int, int]:
    r = sum(x for x in v if x > 0)
    s = sum(-x for x in v if x < 0)
    d = sum(max(x - 1, 0) for x in v if x > 0)
    return r, s, d


def _read_target_file(path: Path) -> set[IndexTuple]:
    if not path.exists():
        raise SystemExit(f"ERROR: target file not found: {path}")
    return {_parse(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def _load_symmetry_unresolved() -> set[IndexTuple]:
    if not SOURCE_AUDIT.exists():
        raise SystemExit(f"ERROR: symmetry closure audit not found: {SOURCE_AUDIT}")
    data = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    raw = data.get("unresolved_targets")
    if not isinstance(raw, list) or not raw:
        raise SystemExit("ERROR: symmetry closure audit has no unresolved_targets")
    return {_parse(str(x)) for x in raw}


def generate() -> None:
    base = _read_target_file(BASE_TARGET_FILE)
    supplement = _load_symmetry_unresolved()
    union = base | supplement

    maxima = [0, 0, 0]
    for v in union:
        r, s, d = _bounds(v)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    rmax = max(maxima[0], TOP_SECTOR.bit_count())
    smax, dmax = maxima[1], maxima[2]

    UNION_TARGET_FILE.write_text("\n".join(_fmt(v) for v in sorted(union)) + "\n", encoding="utf-8", newline="\n")
    SUPPLEMENT_TARGET_FILE.write_text("\n".join(_fmt(v) for v in sorted(supplement)) + "\n", encoding="utf-8", newline="\n")

    REDUCE_JOB.write_text(
        "jobs:\n"
        "  - reduce_sectors:\n"
        "      reduce:\n"
        f"        - {{topologies: [{FAMILY}], sectors: [{TOP_SECTOR}], r: {rmax}, s: {smax}, d: {dmax}}}\n"
        "      select_integrals:\n"
        "        select_mandatory_list:\n"
        f"          - [{FAMILY},{UNION_TARGET_FILE.name}]\n"
        "      run_symmetries: true\n"
        "      run_initiate: true\n"
        "      run_triangular: false\n"
        "      run_back_substitution: false\n"
        "      run_firefly: true\n"
        "      iterative_reduction: sectorwise\n"
        f"      alt_dir: {ALT_DIR_NAME}\n",
        encoding="utf-8", newline="\n"
    )
    EXPORT_JOB.write_text(
        "jobs:\n"
        "  - kira2form:\n"
        "      target:\n"
        f"        - [{FAMILY},{SUPPLEMENT_TARGET_FILE.name}]\n"
        f"      alt_dir: {ALT_DIR_NAME}\n",
        encoding="utf-8", newline="\n"
    )

    print("QEDCalc Q01 closure1+symmetry FireFly generator")
    print("base closure-wave-1 targets:", len(base))
    print("symmetry supplemental targets:", len(supplement))
    print("union targets:", len(union))
    print("overlap:", len(base & supplement))
    print(f"seed bounds: r={rmax} s={smax} d={dmax}")
    print("alt_dir:", ALT_DIR_NAME)
    print("Q01 closure1+symmetry FireFly generation PASS")


def _find_export() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / "kira_q01_symmetry_union_export_targets.inc"
    if preferred.exists():
        return preferred
    cands = sorted((p for p in result_dir.glob("*.inc") if "symmetry_union" in p.name), key=lambda p: p.stat().st_mtime, reverse=True)
    if cands:
        return cands[0]
    raise SystemExit(f"ERROR: symmetry union FORM export not found under {result_dir}")


def audit() -> None:
    targets = _read_target_file(SUPPLEMENT_TARGET_FILE)
    form = _find_export()
    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form, family=FAMILY):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
        elif rule.is_zero:
            zeros.add(lhs)
    log_text = EXPORT_LOG.read_text(encoding="utf-8", errors="strict") if EXPORT_LOG.exists() else ""
    masters = {tuple(int(x.strip()) for x in m.group("args").split(",")) for m in _MASTER_RE.finditer(log_text)}
    unresolved = sorted(targets - rules - zeros - masters)
    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))
    status = {"rule": len(targets & rules), "zero": len(targets & zeros), "kira_master": len(targets & masters), "still_unresolved": len(unresolved)}
    summary = {"targets": len(targets), "target_status": status, "kira_unreduced_integrals_zero": unreduced_zero, "unresolved_targets": [_fmt(v) for v in unresolved], "pass": not unresolved and unreduced_zero}
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("QEDCalc Q01 closure1+symmetry FireFly audit")
    print("requested symmetry targets:", len(targets))
    print("target status:", status)
    print("Kira unreduced integrals = 0:", unreduced_zero)
    print("audit JSON:", OUTPUT_JSON)
    if unresolved:
        for v in unresolved[:12]:
            print("  unresolved:", _fmt(v))
        raise SystemExit(3)
    if not unreduced_zero:
        raise SystemExit(1)
    print("Q01 closure1+symmetry FireFly audit PASS")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("generate", "audit"))
    a = p.parse_args()
    generate() if a.mode == "generate" else audit()


if __name__ == "__main__":
    main()
