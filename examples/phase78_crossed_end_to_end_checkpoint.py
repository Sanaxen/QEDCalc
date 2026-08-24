from pathlib import Path
import sympy as sp
from qedcalc.operations.crossed_ladder import crossed_phase78_end_to_end_checkpoint

c = crossed_phase78_end_to_end_checkpoint()
for key in (
    "projector_residual_F1", "projector_residual_F2",
    "endpoint_divergent_residual", "final_closed_form_residual",
):
    assert sp.simplify(c[key]) == 0, (key, c[key])

out = Path(__file__).resolve().parents[1] / "output" / "phase78_crossed_end_to_end_checkpoint.md"
lines = [
    "# Phase 78: crossed-ladder end-to-end closure checkpoint", "",
    "The release-validation path checks the exact modern-route invariants without the expensive full raw-q-kernel regeneration.", "",
]
for key in (
    "projector_F1_coefficient", "projector_F2_coefficient",
    "endpoint_divergent_residual", "half_sector", "endpoint_total",
    "final", "closed_form", "final_closed_form_residual",
    "historical_karplus_kroll_gap",
):
    lines += [f"## {key}", "", "$$", sp.latex(c[key]), "$$", ""]
lines += [
    "## Heavy raw regeneration", "",
    "The existing raw-one-variable-kernel to automatic-Hermite/canonical residual audit remains available separately because rebuilding it is intentionally excluded from the fast release validation.", "",
    "## Historical 1/32 status", "",
    "The magnitude 1/32 is retained as a historical audit target only. Its precise location in the 1950 Karplus--Kroll algebra is not claimed to be resolved by this checkpoint.", "",
    "## Result", "", "PASS: projector normalization, endpoint cancellation, and final analytic assembly close exactly.", "",
]
out.write_text("\n".join(lines), encoding="utf-8")
print("Phase-78 crossed end-to-end closure PASS")
print(f"Output: {out}")
