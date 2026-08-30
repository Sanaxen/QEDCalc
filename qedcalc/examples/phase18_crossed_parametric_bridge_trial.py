from pathlib import Path
import sympy as sp
from qedcalc.operations.crossed_ladder import (
    crossed_bare_scalar_parametric_representation,
    crossed_bare_scalar_parametric_checks,
)

ROOT = Path(__file__).resolve().parents[1]
D,z,m2 = sp.symbols('D z m2')
rep = crossed_bare_scalar_parametric_representation(D,z,m2)
checks = crossed_bare_scalar_parametric_checks(D,z,m2)

out = ROOT/'output'/'phase18_crossed_parametric_bridge_trial.md'
lines = [
    '# Phase 18: crossed-ladder raw scalar-family to projective bridge','',
    'The six physical crossed denominators K,L,E1,E2,E3,E4 are taken directly from the generic crossed IBP family. H=-(k+l)^2 is auxiliary and has power zero.','',
    f'Active denominators: `{rep.active_denominators}`','',
    f'U total degree: **{checks["U_total_degree"]}**; homogeneous: **{checks["U_homogeneous"]}**.','',
    f'F total degree: **{checks["F_total_degree"]}**; homogeneous: **{checks["F_homogeneous"]}**.','',
    '## U','', '$$', sp.latex(rep.U), '$$','',
    '## F','', '$$', sp.latex(rep.F), '$$','',
    'This bridge is denominator-level. The remaining raw-to-projective gap is the projected numerator polynomial and its reduction to the hand-audited V-partial-fraction kernel.',''
]
out.write_text('\n'.join(lines),encoding='utf-8')
print('Phase-18 crossed parametric bridge: PASS')
print('active',rep.active_denominators,'U degree',checks['U_total_degree'],'F degree',checks['F_total_degree'])
print('Output:',out)
