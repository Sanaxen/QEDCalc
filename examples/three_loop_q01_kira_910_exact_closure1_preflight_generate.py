"""Generate closure-wave-1 mandatory list and Kira preflight for Q01 exact944.

This script never runs Kira itself. It combines the original 944 demanded
integrals with the unresolved non-master RHS leaves discovered in the completed
exact944 FORM export. The resulting mandatory list is used for a fresh isolated
preflight under alt_dir=exact944closure1.
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
ORIGINAL_TARGETS = PROJECT / "q01_944_targets"
MANDATORY_FILE = PROJECT / "q01_exact944_closure1_targets"
JOB_FILE = PROJECT / "jobs_exact944_closure1_preflight.yaml"
FAMILY = "Q01_full"
ALT_DIR = "exact944closure1"
EXPECTED_ORIGINAL = 944
IndexTuple = tuple[int, ...]


def _parse_target_line(line: str) -> IndexTuple:
    text = line.strip()
    prefix = FAMILY + "["
    if not text.startswith(prefix) or not text.endswith("]"):
        raise ValueError(f"unexpected target syntax: {text!r}")
    values = tuple(int(v.strip()) for v in text[len(prefix):-1].split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices: {text!r}")
    return values


def _format_target(indices: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in indices)}]"


def _bounds(indices: IndexTuple) -> tuple[int, int, int]:
    r = sum(v for v in indices if v > 0)
    s = sum(-v for v in indices if v < 0)
    d = sum(max(v - 1, 0) for v in indices if v > 0)
    return r, s, d


def main() -> None:
    print("QEDCalc Q01 exact944 closure-wave-1 preflight generator")
    print("mode: saved exact944 artifacts only; no Kira reduction rerun here")

    for path in (FORM_FILE, MASTERS_FILE, ORIGINAL_TARGETS):
        if not path.exists():
            raise SystemExit(f"ERROR: required artifact not found: {path}")

    original_lines = [line.strip() for line in ORIGINAL_TARGETS.read_text(encoding="utf-8").splitlines() if line.strip()]
    original = tuple(_parse_target_line(line) for line in original_lines)
    if len(original) != EXPECTED_ORIGINAL or len(set(original)) != EXPECTED_ORIGINAL:
        raise SystemExit(
            f"ERROR: expected {EXPECTED_ORIGINAL} unique original targets; "
            f"got total={len(original)} unique={len(set(original))}"
        )

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

    all_rhs = {child for rhs in rules.values() for child in rhs}
    leaves = {
        child for child in all_rhs
        if child not in masters and child not in zero_rules and child not in rules
    }

    combined = tuple(dict.fromkeys([*original, *sorted(leaves)]))
    MANDATORY_FILE.write_text(
        "\n".join(_format_target(v) for v in combined) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    maxima = [0, 0, 0]
    for indices in combined:
        r, s, d = _bounds(indices)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    rmax, smax, dmax = maxima

    JOB_FILE.write_text(
        f'''jobs:\n  - reduce_sectors:\n      reduce:\n        - {{topologies: [{FAMILY}], sectors: [511], r: {rmax}, s: {smax}, d: {dmax}}}\n      select_integrals:\n        select_mandatory_list:\n          - [{FAMILY},{MANDATORY_FILE.name}]\n      run_symmetries: true\n      run_initiate: true\n      run_triangular: false\n      run_back_substitution: false\n      alt_dir: {ALT_DIR}\n''',
        encoding="utf-8",
        newline="\n",
    )

    print("original demanded targets:", len(original))
    print("unresolved exact944 RHS leaves:", len(leaves))
    print("closure-wave-1 mandatory targets:", len(combined))
    print(f"required target maxima: r={rmax} s={smax} d={dmax}")
    print("mandatory list:", MANDATORY_FILE)
    print("alt_dir:", ALT_DIR)
    print("generated:", JOB_FILE)
    print("Q01 exact944 closure-wave-1 preflight generation PASS")


if __name__ == "__main__":
    main()
