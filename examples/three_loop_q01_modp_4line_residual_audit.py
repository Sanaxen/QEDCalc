from __future__ import annotations

import json
import time
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.modp_sector_residual_audit import audit_sector_residual_pivots, residual_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_largest_4line_descent.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_residual_audit.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if "unsolved_target_indices" not in data:
        raise RuntimeError(
            "saved 4-line descent JSON lacks unsolved_target_indices; rerun "
            "run_three_loop_q01_modp_largest_4line_descent.bat first"
        )

    unsolved = tuple(IntegralIndex(tuple(p)) for p in data["unsolved_target_indices"])
    same = tuple(IntegralIndex(tuple(p)) for p in data["same_sector_terminal_indices"])
    residuals = residual_union(unsolved, same)

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    start = time.perf_counter()

    def progress(stage, current=None, total=None):
        elapsed = time.perf_counter() - start
        suffix = ""
        if current is not None and total:
            suffix = f" {current}/{total} ({100.0 * current / total:.1f}%)"
        print(f"[progress {elapsed:8.1f}s] {stage}{suffix}", flush=True)

    profile = audit_sector_residual_pivots(
        family, residuals, templates=templates, progress=progress
    )

    out = {
        "sector": data["sector"],
        "unsolved_target_count": len(unsolved),
        "same_sector_terminal_count": len(same),
        "residual_union_count": profile.residual_count,
        "direct_pivotable_count": profile.direct_pivotable_count,
        "reverse_only_pivotable_count": profile.reverse_only_pivotable_count,
        "rescued_count": profile.rescued_count,
        "unresolved_count": profile.unresolved_count,
        "direct_pivotable_indices": profile.direct_pivotable_indices,
        "reverse_only_pivotable_indices": profile.reverse_only_pivotable_indices,
        "unresolved_indices": profile.unresolved_indices,
        "elapsed_seconds": time.perf_counter() - start,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 4-line residual pivot audit")
    print(f"sector: {tuple(data['sector'])}")
    print(f"unsolved targets: {len(unsolved)}")
    print(f"same-sector terminals: {len(same)}")
    print(f"residual union: {profile.residual_count}")
    print(f"direct pivotable residuals: {profile.direct_pivotable_count}")
    print(f"reverse-only pivotable residuals: {profile.reverse_only_pivotable_count}")
    print(f"rescued by direct/reverse: {profile.rescued_count}")
    print(f"still unresolved: {profile.unresolved_count}")
    print(f"generated: {OUTPUT}")
    print("Q01 4-line residual pivot audit PASS")


if __name__ == "__main__":
    main()
