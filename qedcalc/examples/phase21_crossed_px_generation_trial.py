from pathlib import Path
import sympy as sp
from qedcalc.operations.crossed_ladder import (
    crossed_projective_numerator_px,
    crossed_projective_numerator_px_checks,
)

ROOT = Path(__file__).resolve().parents[1]
r = crossed_projective_numerator_px()
c = crossed_projective_numerator_px_checks()
assert c["term_count"] == 244
assert c["total_degree"] == 8
assert c["homogeneous"]
assert c["integer_real_coefficients"]
assert c["reversal_difference"] == 0
assert c["apparent_gamma0_coefficient"] == 0
assert c["projective_term_count"] == 227
assert c["projective_v_degree"] == 4

lines = [
    "# Phase 21: automatic crossed-ladder P_X generation", "",
    "The long projective numerator is reconstructed from the raw crossed Dirac chain; no stored P_X table is read.", "",
    "## Streaming route", "",
    "1. Differentiate the two p'=p+q electron numerators before distributing the Dirac chain.",
    "2. Apply the Breit magnetic projector at O(q).",
    "3. Include the q-linear denominator correction D^-6 -> D^-6 - 6 deltaD D^-7.",
    "4. Wick rotate and square-complete both loop momenta.",
    "5. Reduce centered monomials by bivariate Gaussian/Wick moments term by term.",
    "6. Collect only by powers of Delta and W, then form the common denominator.", "",
    f"P_X monomials: **{c['term_count']}**.", "",
    f"Total degree: **{c['total_degree']}**; homogeneous: **{c['homogeneous']}**.", "",
    f"Projective P_X monomials after scale removal: **{c['projective_term_count']}**.", "",
    "## Exact checks", "",
    f"Apparent Gamma(0) coefficient after the full sum: **{c['apparent_gamma0_coefficient']}**.", "",
    f"Graph-reversal difference x<->z, u<->v: **{c['reversal_difference']}**.", "",
    f"deg_V(projective P_X) = **{c['projective_v_degree']}**. Since Delta^4 W^2 has V-degree 6, the V-integrand is O(V^-2); the logarithmic 1/V coefficient therefore vanishes.", "",
    "The generated integrand is", "",
    "$$", r"G_{\mathrm X}=\frac{yP_{\mathrm X}}{4\Delta^4W^2}.", "$$", "",
    "The complete 244-term polynomial is written to output/crossed_PX_generated.txt rather than expanded inline here.", "",
]
(ROOT / "output" / "phase21_crossed_px_generation_trial.md").write_text("\n".join(lines), encoding="utf-8")
(ROOT / "output" / "crossed_PX_generated.txt").write_text(str(r.P_X), encoding="utf-8")
(ROOT / "output" / "crossed_PX_projective_generated.txt").write_text(str(r.projective_P_X), encoding="utf-8")
print("Phase-21 crossed P_X generation: PASS")
print("P_X terms:", c["term_count"], "projective terms:", c["projective_term_count"])
print("Gamma(0) coefficient:", c["apparent_gamma0_coefficient"])
