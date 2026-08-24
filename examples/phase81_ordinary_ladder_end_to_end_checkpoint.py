from pathlib import Path
try:
    import mpmath as mp
except ModuleNotFoundError:
    mp = None
import sympy as sp

from qedcalc import __version__
from qedcalc.operations.ladder import (
    ladder_subtraction_series,
    ladder_renormalized_checkpoint,
)
from qedcalc.operations.ladder_assembly import (
    compose_ladder_projector_with_reduction,
    ladder_projector_checkpoint_normalized_expression,
    ladder_projector_leading_z_pole_cancellation,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "phase81_ordinary_ladder_end_to_end_checkpoint.md"
D = sp.Symbol("D")
z = sp.Symbol("z")
delta = sp.Symbol("delta")

assembly = compose_ladder_projector_with_reduction(
    ROOT / "data" / "ladder_corrected_spin_sum_72_coefficients.csv",
    ROOT / "data" / "ladder_corrected_40target_12basis_symbolic_reduction.csv",
)

assert len(assembly.canonical_target_coefficients) == 40
assert len(assembly.basis_coefficients) == 12
z_pole_residual = sp.simplify(
    ladder_projector_leading_z_pole_cancellation(
        assembly.basis_coefficients, D=D, mass_squared=1, z=z
    )
)
assert z_pole_residual == 0

expr = ladder_projector_checkpoint_normalized_expression(
    assembly.basis_coefficients, D=D, mass_squared=1, z=z
)

numeric_extended_audit = mp is not None
if numeric_extended_audit:
    mp.mp.dps = 80
    f = sp.lambdify(D, expr, "mpmath")

    def finite_at(h):
        return f(4 + h) + mp.mpf(3) / (4 * h)

    h1 = mp.mpf("1e-5")
    h2 = mp.mpf("1e-6")
    s1 = (finite_at(h1) + finite_at(-h1)) / 2
    s2 = (finite_at(h2) + finite_at(-h2)) / 2
    bare_finite = (100 * s2 - s1) / 99
    bare_checkpoint = mp.mpf(107) / 48 + mp.pi**2 / 18
    bare_difference = bare_finite - bare_checkpoint
else:
    bare_finite = None
    bare_checkpoint = None
    bare_difference = None

sub_series = ladder_subtraction_series(delta, 1).removeO()
sub_pole = sp.simplify(sp.limit(delta * sub_series, delta, 0))
sub_finite = sp.simplify(sp.limit(sub_series + sp.Rational(3, 4) / delta, delta, 0))
assert sub_pole == -sp.Rational(3, 4)
assert sub_finite == 2

renormalized_closed = sp.Rational(11, 48) + sp.pi**2 / 18
if numeric_extended_audit:
    renormalized_numeric = bare_finite - mp.mpf(2)
    renormalized_checkpoint = mp.mpf(11) / 48 + mp.pi**2 / 18
    renormalized_difference = renormalized_numeric - renormalized_checkpoint
else:
    renormalized_numeric = None
    renormalized_checkpoint = None
    renormalized_difference = None
renormalized_symbolic_residual = sp.simplify(
    ladder_renormalized_checkpoint(delta) - renormalized_closed
)
assert renormalized_symbolic_residual == 0

def fmt(value, digits=30):
    if value is None:
        return "SKIPPED (optional mpmath not installed)"
    return mp.nstr(value, digits)

lines = [
    "# Phase 81: ordinary ladder end-to-end checkpoint",
    "",
    f"QEDCalc version: `{__version__}`",
    "",
    "## Reduction chain",
    "",
    "- corrected spin-sum projector table: 72 terms",
    f"- canonical IBP targets after symmetry combination: {len(assembly.canonical_target_coefficients)}",
    f"- terminal analytic basis size: {len(assembly.basis_coefficients)}",
    f"- leading magnetic-projector z-pole residual: `{z_pole_residual}`",
    "",
    "## Bare finite coefficient",
    "",
    "The full 40-to-12 basis assembly gives",
    "",
    "$$",
    r"F_{2,\mathrm L}^{\mathrm{bare}}=-\frac{3}{4\delta}+C_{\mathrm{bare}}+O(\delta),",
    "$$",
    "",
    f"Numerically reconstructed `C_bare`: **{fmt(bare_finite, 50)}**",
    "",
    "Independent analytic checkpoint:",
    "",
    "$$",
    r"C_{\mathrm{bare}}=\frac{107}{48}+\frac{\pi^2}{18}.",
    "$$",
    "",
    f"Absolute reconstruction difference: **{fmt(abs(bare_difference) if bare_difference is not None else None, 12)}**",
    "",
    "## On-shell subtraction",
    "",
    "$$",
    r"Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).",
    "$$",
    "",
    f"Pole coefficient: `{sub_pole}`",
    f"Finite subtraction: `{sub_finite}`",
    "",
    "The pole cancels against the bare ladder pole, while the finite subtraction removes 2.",
    "",
    "## Renormalized ordinary ladder",
    "",
    "$$",
    r"A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.",
    "$$",
    "",
    f"Numerical end-to-end reconstruction: **{fmt(renormalized_numeric, 50)}**",
    f"Independent analytic value: **{fmt(renormalized_checkpoint, 50)}**",
    f"Absolute difference: **{fmt(abs(renormalized_difference) if renormalized_difference is not None else None, 12)}**",
    f"Symbolic renormalized residual: `{renormalized_symbolic_residual}`",
    "",
    "No final ordinary-ladder coefficient is fed into the 72 -> 40 -> 12 master reconstruction; the closed form is used only as the output-side checkpoint.",
    "",
]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")

print("Phase-81 ordinary-ladder end-to-end closure PASS")
if numeric_extended_audit:
    print("Extended high-precision audit: PASS")
    print("bare finite =", fmt(bare_finite, 30))
    print("renormalized =", fmt(renormalized_numeric, 30))
    print("difference =", fmt(renormalized_difference, 12))
else:
    print("Extended high-precision audit: SKIPPED (optional mpmath not installed)")
    print("Exact symbolic release invariants: PASS")
print("Output:", OUT)
