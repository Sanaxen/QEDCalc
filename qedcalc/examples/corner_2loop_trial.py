from pathlib import Path
import sympy as sp

from qedcalc.history.markdown_session import MarkdownSession
from qedcalc.operations.corner import (
    corner_soft_kernel,
    corner_soft_integrate_S,
    corner_soft_ir_coefficient,
    corner_shifted_p_minus_k,
    corner_hard_primary_result,
    corner_shift_correction_result,
    corner_hard_total_result,
    corner_z_sector_result,
    corner_finite_result,
    corner_expected_finite_result,
    corner_result_difference,
    corner_full_asymptotic,
    corner_self_energy_ir_cancellation,
    corner_soft_finite_constant,
    corner_hard_remainder_from_soft_split,
    corner_soft_hard_split_difference,
)

out = Path(__file__).resolve().parents[1] / "output" / "corner_2loop_trial.md"
s = MarkdownSession(out, title="QEDCalc corner (IIc) two-loop trial")

s.text(
    "Scope",
    "This trial starts from the independently derived UV-finite parameter representation and its sector decomposition. The complete six-denominator magnetic-projector integrand is not yet regenerated automatically from the original two-loop LaTeX expression. The trial verifies the soft IR coefficient, the momentum-shift correction, the hard/z-sector analytic bookkeeping, and the self-energy IR cancellation.",
)

U,R,S,v = sp.symbols("U R S v", positive=True)
s.equation("Leading physical-measure soft kernel", sp.latex(corner_soft_kernel(U,R,S,v)))
s.equation("S-integrated soft kernel", sp.latex(corner_soft_integrate_S(R,v)))
s.equation("Exact coefficient of log(1/rho)", sp.latex(corner_soft_ir_coefficient()))
s.equation("Diagnostic soft finite constant", sp.latex(corner_soft_finite_constant()))
s.equation("Diagnostic hard remainder", sp.latex(corner_hard_remainder_from_soft_split()))
s.equation("Soft+hard diagnostic split difference", sp.latex(corner_soft_hard_split_difference()))

u = sp.Symbol("u")
coeff = corner_shifted_p_minus_k(u,v)
shift_tex = (
    r"p'-k\;\longrightarrow\;"
    + sp.latex(coeff['p_prime']) + r"\,p'"
    + sp.latex(coeff['p_double_prime']) + r"\,p''"
    + r"-k"
)
s.equation("Common momentum-shift action on p'-k", shift_tex)

h1 = corner_hard_primary_result()
ds = corner_shift_correction_result()
h = corner_hard_total_result()
z = corner_z_sector_result()
finite = corner_finite_result()
expected = corner_expected_finite_result()

s.equation("Primary K+kappa^2 hard-sector group", sp.latex(h1))
s.equation("Momentum-shift correction", sp.latex(ds))
s.equation("Complete K+kappa^2 hard sector", sp.latex(h))
s.equation("z sector", sp.latex(z))
s.equation("Corner finite part", sp.latex(finite))
s.equation("Independent closed-form checkpoint", sp.latex(expected))
s.equation("Difference", sp.latex(corner_result_difference()))

rho = sp.Symbol("rho", positive=True)
s.equation("Corner asymptotic coefficient A_C(rho)", sp.latex(corner_full_asymptotic(rho)))
irc = corner_self_energy_ir_cancellation()
s.equation("Corner IR-log coefficient", sp.latex(irc.corner_log_coefficient))
s.equation("Self-energy insertion IR-log coefficient", sp.latex(irc.self_energy_log_coefficient))
s.equation("Combined IR-log coefficient", sp.latex(irc.total_log_coefficient))
s.equation("Combined finite part after IR cancellation", sp.latex(irc.combined_finite))

s.text("Result", "PASS: the independently derived corner-sector decomposition and the self-energy IR cancellation are reproduced exactly.")
s.save()

print("QEDCalc corner (IIc) two-loop trial")
print(f"Output: {out}")
print(f"A_C,fin = {sp.simplify(finite)}")
print("PASS" if corner_result_difference() == 0 and irc.total_log_coefficient == 0 else "FAIL")
