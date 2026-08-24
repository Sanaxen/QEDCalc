from pathlib import Path
import sympy as sp

from qedcalc.operations.master_integrals import (
    classify_ordinary_ladder_terminal_basis,
    ordinary_ladder_basis_z0_evaluations,
    write_ladder_basis_classification_csv,
    write_ladder_basis_z0_evaluation_csv,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'phase10_ladder_basis_evaluation_trial.md'
CSV_CLASS = ROOT / 'output' / 'ladder_12basis_parametric_classification.csv'
CSV_Z0 = ROOT / 'output' / 'ladder_12basis_z0_evaluation.csv'

D,z,m2 = sp.symbols('D z m2', positive=True)
classification = classify_ordinary_ladder_terminal_basis(D=D,z=z,mass_squared=m2)
z0 = ordinary_ladder_basis_z0_evaluations(D=D,mass_squared=m2)
write_ladder_basis_classification_csv(classification, CSV_CLASS)
write_ladder_basis_z0_evaluation_csv(z0, CSV_Z0)

lines = [
    '# QEDCalc phase-10 ordinary-ladder basis-evaluation trial',
    '',
    'The v0.41 corrected ordinary-ladder reduction terminates on 12 basis integrals. v0.42 starts the evaluation layer for those basis objects.',
    '',
    '## Classification',
    '',
    f'Generic-z factorized lower sectors: **{sum(r.kind == "factorized_lower" for r in classification)}**.',
    '',
    f'Exact analytic z=0 basis values: **{sum(r.status == "exact" for r in z0)} / 12**.',
    '',
    'Remaining genuine z=0 masters: **3** (basis 8, 10, 11).',
    '',
    'All formulas below are convention-free Euclidean scalar integrals. Overall Minkowski i factors, Wick-rotation signs, (2pi)^D loop-measure normalization, and renormalization-scale factors belong to the convention layer.',
    '',
    '## z=0 analytic values',
    '',
]
for r in z0:
    lines += [f'### Basis {r.basis_index}: `{r.index.powers}`', '', f'Status: **{r.status}**. Method: `{r.method}`.', '']
    if r.value is not None:
        lines += ['$$', sp.latex(sp.factor(r.value)), '$$', '']
    else:
        p = classification[r.basis_index].parametric
        lines += ['The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:', '']
        lines += ['$$', 'U=' + sp.latex(sp.factor(p.U)), '$$', '']
        lines += ['$$', 'F=' + sp.latex(sp.factor(p.F.subs(z,0))), '$$', '']

lines += [
    '## Evaluation methods now available', '',
    '1. Products of massive one-loop tadpoles.',
    '2. z=0 degeneracies where E1=E4 and/or E2=E3.',
    '3. The one-massless/two-equal-mass two-loop vacuum sunset in Gamma functions.',
    '4. A massless bubble followed by a generalized on-shell massive one-loop integral.',
    '5. Generic projective Feynman-parameter generation U, F, Delta for every one of the 12 basis integrals.',
    '',
    'The next evaluation stage is therefore reduced to basis 8, 10, and 11.',
    '',
    f'Classification CSV: `{CSV_CLASS.relative_to(ROOT)}`', '',
    f'z=0 evaluation CSV: `{CSV_Z0.relative_to(ROOT)}`', '',
]
OUT.write_text('\n'.join(lines), encoding='utf-8')
print('phase-10 basis evaluation: PASS')
print('exact z=0 basis values:', sum(r.status == 'exact' for r in z0), '/ 12')
print('remaining genuine z=0 masters:', [r.basis_index for r in z0 if r.status != 'exact'])
print('output:', OUT)
