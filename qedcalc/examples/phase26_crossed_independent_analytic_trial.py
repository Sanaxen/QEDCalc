from pathlib import Path
import sympy as sp

from qedcalc.operations.crossed_ladder import crossed_independent_analytic_checks

checks = crossed_independent_analytic_checks()
assert checks["divergent_sum"] == 0
assert checks["checkpoint_difference"] == 0

out = Path(__file__).resolve().parents[1] / "output" / "phase26_crossed_independent_analytic_trial.md"
lines = [
    "# Phase 26: crossed-ladder independent analytic evaluation", "",
    "The final analytic constant is assembled from the regenerated canonical kernel.",
    "The final closed-form checkpoint is used only after the derivation as a regression comparison.", "",
]
for key in ["A","B","C","half","endpoint_canonical_finite","boundary_finite","endpoint_total","divergent_sum","final","checkpoint_difference"]:
    lines += [f"## {key}", "", "$$", sp.latex(checks[key]), "$$", ""]
lines += ["## Result", "", "PASS: canonical standard integrals, endpoint finite part, automatic boundary term, and the final crossed-ladder constant are independently regenerated.", ""]
out.write_text("\n".join(lines), encoding="utf-8")
print("Phase-26 crossed independent analytic evaluation: PASS")
print(f"Output: {out}")
