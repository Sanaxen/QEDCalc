from pathlib import Path
from qedcalc.operations.crossed_ladder import (
    crossed_h_u_integrated_kernel_checks,
    crossed_tq_preintegration_checks,
)

ROOT = Path(__file__).resolve().parents[1]
u = crossed_h_u_integrated_kernel_checks()
tq = crossed_tq_preintegration_checks()
assert u["upper_endpoint_S"] == 1
assert tq["jacobian_difference"] == 0
assert tq["log_argument_difference"] == 0

lines = [
    "# Phase 23: crossed-ladder analytic U integration and triangular bridge", "",
    "After V integration use h=S(R+U)-1. The original S>=1 domain gives", "",
    "$$", r"0\le U\le h-R+1.", "$$", "",
    "With Y=R+U, every generated U integrand is polynomial(Y)/Y^p, so the U integral is evaluated exactly by monomial primitives and log((h+1)/R).", "",
    "After", "",
    "$$", r"h=\frac{1-t}{t},\qquad R=\frac{q}{t},", "$$", "",
    "the Jacobian is 1/t^3 and the domain becomes", "",
    "$$", r"0<t<q<1.", "$$", "",
    "The generated logarithm argument is", "",
    "$$", r"\frac{q^2+(1-2q)t}{q^2(1-t)}.", "$$", "",
    f"U-integrated component operation counts: `{u['component_operation_counts']}`", "",
    f"(t,q) component operation counts: `{tq['component_operation_counts']}`", "",
]
(ROOT / "output" / "phase23_crossed_u_tq_bridge_trial.md").write_text("\n".join(lines), encoding="utf-8")
print("Phase-23 crossed U/tq bridge: PASS")
