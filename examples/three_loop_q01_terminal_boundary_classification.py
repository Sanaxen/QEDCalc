from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.terminal_boundary_classification import classify_terminal_boundary

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "output" / "3loop_q01_merged_symbolic_closure.json"
MANIFEST = ROOT / "output" / "3loop_q01_master_candidate_manifest.json"
OUTPUT = ROOT / "output" / "3loop_q01_terminal_boundary_classification.json"


def main() -> None:
    closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    terminals = tuple(IntegralIndex(tuple(x)) for x in closure["distinct_unresolved_terminals"])
    known = tuple(IntegralIndex(tuple(row["index"])) for row in manifest["entries"])
    family = q01_integral_family()
    profile = classify_terminal_boundary(family, terminals, known_manifest_indices=known)

    complexity_hist = Counter(record.corrected_complexity for record in profile.records)
    active_hist = Counter(record.active_physical_lines for record in profile.records)
    out = {
        "terminal_count": profile.terminal_count,
        "known_manifest_count": profile.known_manifest_count,
        "conservative_zero_count": profile.conservative_zero_count,
        "scalar_factorized_count": profile.scalar_factorized_count,
        "scalar_connected_count": profile.scalar_connected_count,
        "nonscalar_count": profile.nonscalar_count,
        "category_histogram": dict(profile.category_histogram),
        "corrected_complexity_histogram": dict(sorted(complexity_hist.items())),
        "active_physical_line_histogram": dict(sorted(active_hist.items())),
        "records": [record.__dict__ for record in profile.records],
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 symbolic terminal boundary classification")
    print(f"distinct unresolved terminals: {profile.terminal_count}")
    print(f"known 29-manifest terminals: {profile.known_manifest_count}")
    print(f"conservative/structural zero terminals: {profile.conservative_zero_count}")
    print(f"scalar factorized terminals: {profile.scalar_factorized_count}")
    print(f"scalar connected terminals: {profile.scalar_connected_count}")
    print(f"nonscalar terminals: {profile.nonscalar_count}")
    print(f"category histogram: {dict(profile.category_histogram)}")
    print(f"corrected-complexity histogram: {dict(sorted(complexity_hist.items()))}")
    print(f"active-line histogram: {dict(sorted(active_hist.items()))}")
    print(f"generated: {OUTPUT}")
    print("Q01 symbolic terminal boundary classification PASS")


if __name__ == "__main__":
    main()
