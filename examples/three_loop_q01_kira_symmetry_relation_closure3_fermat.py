"""Close the third Q01 symmetry-relation reduction wave with Kira/Fermat.

This stage consumes the remaining lower-sector integrals reported by the
wave-2 relation probe and reduces them with ordinary Kira triangular +
back-substitution. FireFly is deliberately not used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT
from three_loop.kira_form_parser import iter_kira_form_rules

IndexTuple = tuple[int, ...]
SOURCE_JSON = PROJECT / "q01_kira_symmetry_linear_relation_probe.json"
TARGET_FILE = PROJECT / "q01_symmetry_relation_closure3_fermat_targets"
JOB_FILE = PROJECT / "jobs_q01_symmetry_relation_closure3_fermat.yaml"
LOG_FILE = PROJECT / "q01_symmetry_relation_closure3_fermat.log"
ALT_DIR_NAME = "symmetry_relation_closure3_fermat"
ALT_ROOT = PROJECT / ALT_DIR_NAME
OUTPUT_JSON = PROJECT / "q01_symmetry_relation_closure3_fermat_audit.json"
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


def _load_targets() -> tuple[IndexTuple, ...]:
    if not SOURCE_JSON.exists():
        raise SystemExit(f"ERROR: relation-probe JSON not found: {SOURCE_JSON}")
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    missing_occurrences = int(data.get("expanded_integrals_missing_from_merged_reduction_graph", 0) or 0)
    raw = data.get("missing_integral_samples")
    if not isinstance(raw, list) or not raw:
        raise SystemExit("ERROR: relation-probe JSON has no missing_integral_samples")
    # The current probe records up to 12 unique samples. Only proceed when the
    # total number of missing occurrences is <=12, which guarantees the sample
    # list contains the complete unique missing set rather than a truncation.
    if missing_occurrences > 12:
        raise SystemExit(
            "ERROR: relation probe reported more than 12 missing occurrences; "
            "the saved sample list may be truncated"
        )
    return tuple(sorted({_parse(str(x)) for x in raw}))


def generate() -> None:
    targets = _load_targets()
    maxima = [0, 0, 0]
    for v in targets:
        r, s, d = _bounds(v)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    rmax = max(maxima[0], TOP_SECTOR.bit_count())
    smax, dmax = maxima[1], maxima[2]

    TARGET_FILE.write_text("\n".join(_fmt(v) for v in targets) + "\n", encoding="utf-8", newline="\n")
    JOB_FILE.write_text(
        "jobs:\n"
        "  - reduce_sectors:\n"
        "      reduce:\n"
        f"        - {{topologies: [{FAMILY}], sectors: [{TOP_SECTOR}], r: {rmax}, s: {smax}, d: {dmax}}}\n"
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
        encoding="utf-8", newline="\n"
    )

    print("QEDCalc Q01 symmetry relation closure-wave-3 Fermat generator")
    print("mode: ordinary triangular + back substitution; FireFly disabled")
    print("closure-wave-3 targets:", len(targets))
    print(f"seed bounds: r={rmax} s={smax} d={dmax}")
    print("alt_dir:", ALT_DIR_NAME)
    print("generated target list:", TARGET_FILE)
    print("generated job:", JOB_FILE)
    print("Q01 symmetry relation closure-wave-3 Fermat generation PASS")


def _find_export() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / "kira_q01_symmetry_relation_closure3_fermat_targets.inc"
    if preferred.exists():
        return preferred
    cands = sorted((p for p in result_dir.glob("*.inc") if "closure3_fermat" in p.name), key=lambda p: p.stat().st_mtime, reverse=True)
    if cands:
        return cands[0]
    raise SystemExit(f"ERROR: closure-wave-3 FORM export not found under {result_dir}")


def audit() -> None:
    targets = set(_load_targets())
    form = _find_export()
    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    rhs: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form, family=FAMILY):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
            rhs.update(tuple(int(v) for v in term.integral.indices) for term in rule.terms)
        elif rule.is_zero:
            zeros.add(lhs)

    log_text = LOG_FILE.read_text(encoding="utf-8", errors="strict") if LOG_FILE.exists() else ""
    masters = {tuple(int(x.strip()) for x in m.group("args").split(",")) for m in _MASTER_RE.finditer(log_text)}
    unresolved = sorted(targets - rules - zeros - masters)
    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))
    status = {
        "rule": len(targets & rules),
        "zero": len(targets & zeros),
        "kira_master": len(targets & masters),
        "still_unresolved": len(unresolved),
    }
    summary = {
        "mode": "Q01 symmetry relation closure-wave-3 ordinary Kira/Fermat reduction",
        "targets": len(targets),
        "form_export": str(form),
        "target_status": status,
        "rhs_integrals": len(rhs),
        "kira_unreduced_integrals_zero": unreduced_zero,
        "unresolved_targets": [_fmt(v) for v in unresolved],
        "pass": not unresolved and unreduced_zero,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("QEDCalc Q01 symmetry relation closure-wave-3 Fermat audit")
    print("requested targets:", len(targets))
    print("exported reduction rules:", len(rules))
    print("exported zero rules:", len(zeros))
    print("Kira-reported masters:", len(masters))
    print("target status:", status)
    print("unique RHS integrals:", len(rhs))
    print("Kira unreduced integrals = 0:", unreduced_zero)
    print("audit JSON:", OUTPUT_JSON)
    if unresolved:
        for v in unresolved[:12]:
            print("  unresolved:", _fmt(v))
        raise SystemExit(3)
    if not unreduced_zero:
        raise SystemExit(1)
    print("Q01 symmetry relation closure-wave-3 Fermat audit PASS")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("generate", "audit"))
    a = p.parse_args()
    generate() if a.mode == "generate" else audit()


if __name__ == "__main__":
    main()
