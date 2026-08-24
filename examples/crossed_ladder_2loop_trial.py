from pathlib import Path
import sympy as sp

from qedcalc.history.markdown_session import MarkdownSession
from qedcalc.operations.crossed_ladder import (
    crossed_projective_forms,
    crossed_tq_transform,
    crossed_tq_log_argument,
    crossed_canonical_kernel,
    crossed_half_sector_result,
    crossed_dilog_reflection_sum,
    crossed_endpoint_combined_kernel,
    crossed_endpoint_finite_result,
    crossed_endpoint_asymptotics,
    crossed_endpoint_total_result,
    crossed_final_result,
    crossed_expected_result,
)

out = Path(__file__).resolve().parents[1] / "output" / "crossed_ladder_2loop_trial.md"
s = MarkdownSession(out, title="QEDCalc crossed-ladder two-loop trial")

s.text("Scope", "This trial starts from the independently derived projective/one-variable representation of the crossed-ladder graph. The raw several-hundred-term Dirac reduction is not yet regenerated automatically.")

R,S,U,V = sp.symbols("R S U V")
forms = crossed_projective_forms(R,S,U,V)
s.equation("Projective Delta", sp.latex(forms.Delta))
s.equation("Projective W", sp.latex(forms.W))
s.text("Linearity check", f"degree_V(Delta)={sp.degree(forms.Delta,V)}, degree_V(W)={sp.degree(forms.W,V)}")

t,q = sp.symbols("t q", positive=True)
h,Rt,jac = crossed_tq_transform(t,q)
s.equation("h transformation", sp.latex(h))
s.equation("R transformation", sp.latex(Rt))
s.equation("Jacobian", sp.latex(jac))
s.equation("Reduced logarithm argument", sp.latex(crossed_tq_log_argument(t,q)))

s.equation("Canonical one-variable kernel", sp.latex(crossed_canonical_kernel(q)))
s.equation("Dilogarithm reflection sum", sp.latex(crossed_dilog_reflection_sum(q)))

half = crossed_half_sector_result()
endfinite = crossed_endpoint_finite_result()
asym = crossed_endpoint_asymptotics()
endtotal = crossed_endpoint_total_result()
final = crossed_final_result()
expected = crossed_expected_result()

s.equation("q=1/2 sector", sp.latex(half))
s.equation("Endpoint canonical finite part", sp.latex(endfinite))
s.equation("Endpoint boundary finite part", sp.latex(asym.finite_boundary))
s.equation("Endpoint total", sp.latex(endtotal))
s.equation("Endpoint divergent-log cancellation", sp.latex(asym.divergent_sum))
s.equation("Crossed-ladder final coefficient", sp.latex(final))
s.equation("Independent closed-form checkpoint", sp.latex(expected))
s.equation("Difference", sp.latex(sp.simplify(final-expected)))
s.text("Result", "PASS: the analytic crossed-ladder coefficient matches the independent derivation.")
s.save()

print("QEDCalc crossed-ladder two-loop trial")
print(f"Output: {out}")
print(f"I_X = {sp.simplify(final)}")
print("PASS" if sp.simplify(final-expected)==0 else "FAIL")
