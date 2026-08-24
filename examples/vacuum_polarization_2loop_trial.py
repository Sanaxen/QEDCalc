from pathlib import Path
import sympy as sp

from qedcalc import parse_loop_integral_latex, render_latex
from qedcalc.history.markdown_session import MarkdownSession
from qedcalc.operations.bare_diagram import find_dirac_traces
from qedcalc.operations.vacuum_polarization import (
    reduce_vp_subdiagram_from_bare_2loop_4d,
    vp_hat_renormalized_integrand,
    vp_gminus2_double_integrand,
    vp_z_integrated_kernel,
    vp_numeric_coefficient,
    vp_recognize_analytic,
    vp_expected_analytic,
)

ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "input" / "vacuum_polarization_2loop_bare.tex"
out_path = ROOT / "output" / "vacuum_polarization_2loop_trial.md"

source = source_path.read_text(encoding="utf-8").strip()
diagram = parse_loop_integral_latex(source)
bridge = reduce_vp_subdiagram_from_bare_2loop_4d(diagram)
tr = bridge.trace_reduction

x, z, k2, m = sp.symbols("x z k2 m", positive=True)
pi_hat_integrand = vp_hat_renormalized_integrand(k2, m, z)
double_kernel = vp_gminus2_double_integrand(x, z)
H = vp_z_integrated_kernel(x)
numeric = vp_numeric_coefficient(40)
recognized = vp_recognize_analytic(numeric, 40)
expected = vp_expected_analytic()

session = MarkdownSession(out_path, title="QEDCalc two-loop trial: vacuum polarization")
session.text(
    "Scope",
    "v0.21 parses the bare two-loop RHS as one LoopIntegralExpression. The overall normalization is preserved as LaTeX, "
    "the k/l loop measures are structural objects, and the closed electron loop is discovered from an explicit DiracTrace node. "
    "The trace propagators are scalarized automatically before the trace numerator is evaluated. The final renormalized scalar VP kernel "
    "is still supplied by the dedicated renormalization layer rather than reconstructed from the complete outer diagram in one command.",
)
session.equation("Bare two-loop RHS parsed from LaTeX", diagram)
session.text("Detected Dirac traces", str(len(find_dirac_traces(diagram.integrand))))
session.equation("Scalarized closed-loop fraction", tr.scalarized)
session.equation("Closed-loop trace numerator", tr.traced_numerator)
session.equation("Closed-loop scalar denominator", tr.scalar_denominator)
session.equation("After l = r - z k", bridge.shifted_trace_numerator)
session.equation("After removing odd powers of r", bridge.even_trace_numerator)
session.equation("After rank-2 symmetric tensor reduction", bridge.tensor_reduced_trace_numerator)

session.equation(
    "Reference transverse tensor checkpoint",
    r"\Pi^{\alpha\beta}(k)=\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)",
)
session.equation(
    "On-shell subtraction condition",
    r"\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0",
)
session.equation("Renormalized scalar vacuum-polarization integrand", sp.latex(pi_hat_integrand))
session.equation("Two-parameter g-2 coefficient kernel", sp.latex(double_kernel))
session.equation("z-integrated kernel H(x)", sp.latex(H))
session.text("Numerical coefficient", f"A_VP = {numeric}")
session.equation("Analytic recognition from the numerical value", sp.latex(recognized))
session.equation("Reference analytic coefficient", sp.latex(expected))
session.text("Recognition check", "PASS" if sp.simplify(recognized - expected) == 0 else "FAIL")
session.equation(
    "Two-loop anomalous-moment contribution",
    r"a_{\mathrm{VP}}=\left(\frac{\alpha}{\pi}\right)^2\left(\frac{119}{36}-\frac{\pi^2}{3}\right)",
)
session.save()

print("QEDCalc two-loop vacuum-polarization trial")
print(f"Input: {source_path}")
print(f"Output: {out_path}")
print(f"Loop momenta: {[v.name for v in diagram.loops]}")
print(f"Dirac traces found: {len(find_dirac_traces(diagram.integrand))}")
print(f"A_VP (numeric) = {numeric}")
print(f"A_VP (recognized) = {recognized}")
print("PASS" if sp.simplify(recognized - expected) == 0 else "FAIL")
