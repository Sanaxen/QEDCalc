from pathlib import Path
import sympy as sp

from qedcalc import parse_loop_integral_latex, render_latex
from qedcalc.operations.vacuum_polarization import (
    reduce_vp_subdiagram_from_bare_2loop_4d,
    vp_raw_to_final_audit,
    vp_expected_analytic,
)

ROOT=Path(__file__).resolve().parents[1]
diagram=parse_loop_integral_latex((ROOT/'input'/'vacuum_polarization_2loop_bare.tex').read_text(encoding='utf-8'))
raw=reduce_vp_subdiagram_from_bare_2loop_4d(diagram)
a=vp_raw_to_final_audit()

print('Phase-27 vacuum-polarization raw-to-final bridge')
print('Raw tensor-reduced numerator:')
print(render_latex(raw.tensor_reduced_trace_numerator))
print('Transverse residual:', a.transverse_residual)
print('D->4 subtracted VP integrand:', sp.factor(a.four_dimensional_integrand))
print('Generated double kernel:', sp.factor(a.double_kernel))
print('Generated z kernel H(x):', sp.factor(a.z_kernel))
print('Primitive derivative residual:', a.primitive_derivative_residual)
print('F(1):', a.endpoint_one)
print('F(0):', a.endpoint_zero)
print('Generated A_VP:', a.final_coefficient)
print('Checkpoint difference:', sp.simplify(a.final_coefficient-vp_expected_analytic()))
print('Phase-27 vacuum-polarization raw-to-final bridge: PASS' if sp.simplify(a.final_coefficient-vp_expected_analytic())==0 else 'FAIL')
