from pathlib import Path
import sympy as sp
from qedcalc.parser.qed_latex import parse_loop_integral_latex
from qedcalc.operations.crossed_ladder import (
    analyze_raw_crossed_ladder,
    crossed_raw_numerator_q_expansion,
    crossed_q0_parametric_bridge,
    crossed_q0_parametric_bridge_checks,
    crossed_denominator_q1_correction,
    crossed_breit_projector_check,
)

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
raw=analyze_raw_crossed_ladder(parse_loop_integral_latex(source))
qs=crossed_raw_numerator_q_expansion(raw)
br=crossed_q0_parametric_bridge(D=4,mass_squared=1)
chk=crossed_q0_parametric_bridge_checks(D=4,mass_squared=1)

assert (qs.q0_terms,qs.q1_terms,qs.total_terms)==(144,84,228)
assert chk['Delta_difference']==0
assert chk['W_difference']==0
assert chk['measure_difference']==0

x,y=sp.symbols('x y')
delta1=crossed_denominator_q1_correction(x,y)
proj=crossed_breit_projector_check()
assert proj.F1_coefficient==0 and proj.F2_coefficient==1
lines=[
 '# Phase 20: crossed-ladder q-linear magnetic-projector bridge','',
 'The raw crossed numerator is rewritten with p\' = p + q and truncated at first order before the magnetic projector is assembled.','',
 f'q^0 Dirac-chain terms: **{qs.q0_terms}**.','',
 f'q^1 Dirac-chain terms: **{qs.q1_terms}** (=48+36).','',
 f'Total through O(q): **{qs.total_terms}**.','',
 '## q=0 five-denominator Feynman-parameter bridge','',
 'At q=0 the two central electron denominators coincide.  The scalar core is therefore K L Dk Dkl^2 Dl and the parameter powers are (1,1,1,2,1).','',
 '$$',r'a=x+y+u,\qquad b=y+z+v,\qquad c=y,\qquad r=x+y,\qquad s=y+z','$$','',
 'Automatically generated U:','', '$$',sp.latex(br.Delta),'$$','',
 'Automatically generated F at rho=0:','', '$$',sp.latex(br.W),'$$','',
 f'Feynman-parameter numerator monomial: `${sp.latex(br.expected_measure_monomial)}` (expected y).','',
 'Exact checks: U-Delta = 0, F-W = 0, measure-y = 0.','',
 '## Breit-frame projector normalization','',
 f'F1 coefficient: **{proj.F1_coefficient}**; F2 coefficient: **{proj.F2_coefficient}**.','',
 '## q-linear denominator correction','', '$$',sp.latex(delta1),'$$','',
 'This reproduces delta D = 2 x k.q + y (k+l).q.','',
 'The remaining gap to P_X is now isolated to external-spinor O(q), the 84 q-linear numerator chains, loop shifts/tensor reduction, and Gaussian recombination.',''
]
out=ROOT/'output'/'phase20_crossed_qlinear_bridge_trial.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print('Phase-20 crossed q-linear bridge: PASS')
print('q terms:',qs.q0_terms,qs.q1_terms,qs.total_terms)
print('Delta diff:',chk['Delta_difference'],'W diff:',chk['W_difference'],'measure diff:',chk['measure_difference'])
print('Output:',out)
