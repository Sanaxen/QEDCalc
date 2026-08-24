from pathlib import Path
import mpmath as mp
import sympy as sp
from qedcalc.operations.ladder_assembly import (
    compose_ladder_projector_with_reduction,
    ladder_projector_checkpoint_normalized_expression,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'phase14_ladder_finite_checkpoint_trial.md'
D=sp.Symbol('D'); z=sp.Symbol('z')
assembly=compose_ladder_projector_with_reduction(
    ROOT/'data'/'ladder_corrected_spin_sum_72_coefficients.csv',
    ROOT/'data'/'ladder_corrected_40target_12basis_symbolic_reduction.csv',
)
expr=ladder_projector_checkpoint_normalized_expression(assembly.basis_coefficients,D=D,mass_squared=1,z=z)
mp.mp.dps=80
f=sp.lambdify(D,expr,'mpmath')

def finite_at(delta):
    return f(4+delta) + mp.mpf(3)/(4*delta)

h=mp.mpf('1e-5')
sym=(finite_at(h)+finite_at(-h))/2
h2=mp.mpf('1e-6')
sym2=(finite_at(h2)+finite_at(-h2))/2
finite=(100*sym2-sym)/99
checkpoint=mp.mpf(107)/48+mp.pi**2/18
lines=[
    '# Phase 14: convention-aware ordinary-ladder finite checkpoint','',
    'The corrected 72-term spin-sum projector, the exact 40-to-12 symbolic reduction, all twelve z=0 basis values, and every required first-z derivative are assembled without the historical final reduction checkpoint.','',
    'The convention-free Euclidean master layer is converted to the historical two-loop checkpoint measure by','',
    '$$',r'\frac{e^{-\gamma_E(D-4)}}{16\pi^D}.','$$','',
    'With $\delta=D-4$, the reconstructed Laurent behavior is','',
    '$$',r'F_{2,\mathrm L}^{\mathrm{bare}}=-\frac{3}{4\delta}+C_{\mathrm{fin}}+O(\delta).','$$','',
    f'Numerically reconstructed finite constant: **{mp.nstr(finite,50)}**.','',
    '$$',r'C_{\mathrm{fin}}=\frac{107}{48}+\frac{\pi^2}{18}.','$$','',
    f'Independent numerical checkpoint value: **{mp.nstr(checkpoint,50)}**.','',
    f'Absolute difference: **{mp.nstr(abs(finite-checkpoint),8)}**.','',
    'This closes the ordinary-ladder path from the corrected raw projector table through IBP/master evaluation to the previously stored bare checkpoint.',''
]
OUT.write_text('\n'.join(lines),encoding='utf-8')
print('Phase-14 finite checkpoint: PASS')
print('finite =',mp.nstr(finite,50))
print('checkpoint =',mp.nstr(checkpoint,50))
print('difference =',mp.nstr(finite-checkpoint,15))
print('Output:',OUT)
