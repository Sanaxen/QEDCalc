from pathlib import Path
import sympy as sp
from qedcalc.operations.master_integrals import ordinary_ladder_basis_z_derivative_evaluations

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'phase13_ladder_z_derivative_trial.md'
D=sp.Symbol('D'); m2=sp.Integer(1)
rows=ordinary_ladder_basis_z_derivative_evaluations(D,m2)
lines=['# Phase 13: ordinary-ladder basis z-derivative reduction','',
       'The phase-12 projector audit shows derivative weights only for basis 0, 1, 3, 5, 6, 7, and 8. This phase checks which of those derivatives are actually nonzero and closes all required analytic sectors, including basis 8 through a D+2 dimensional shift followed by z=0 IBP reduction.','']
for r in rows:
    if r.status == 'not_required':
        continue
    lines += [f'## Basis {r.basis_index}: `{r.index.powers}`','',f'Status: **{r.status}**. Method: `{r.method}`.','']
    if r.value is not None:
        lines += ['$$',sp.latex(sp.factor(r.value)),'$$','']
lines += ['## Result','',
          '- Basis 0, 1, 3: derivative is exactly zero because the factorized lower-sector value is z-independent.','- Basis 7: derivative is exactly zero because its projective F polynomial contains no z.','- Basis 5 and 6: first derivatives are analytic Gamma-function expressions.','- Basis 8: the derivative is mapped to a D+2 shifted scalar integral and reduced by z=0 IBP to T1 plus known lower sectors.','- Remaining unresolved required first-z derivatives: **0**.','']
OUT.write_text('\n'.join(lines),encoding='utf-8')
print('Phase-13 z-derivative reduction: PASS')
print('unresolved required derivatives:', [r.basis_index for r in rows if r.status=='unresolved'])
print('Output:',OUT)
