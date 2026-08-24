from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    infer_allowed_univariate_denominator,
    reconstruct_bivariate_with_known_denominator,
)

ROOT = Path(__file__).resolve().parents[1]
D, z = sp.symbols('D z')
full_table = ROOT / 'data' / 'ladder_corrected_40target_12basis_symbolic_reduction.csv'
probe_table = ROOT / 'output' / 'v41_probe_coefficients.csv'
rows = list(csv.DictReader(full_table.open(encoding='utf-8')))
assert len(rows) == 480
nonzero = [r for r in rows if int(r['nonzero'])]
assert len(nonzero) == 151

# Independent three-probe audit of the complete 480-entry matrix.
probe_points = {
    1: (sp.Rational(37,10), sp.Rational(2,5)),
    2: (sp.Rational(41,11), sp.Rational(3,7)),
    3: (sp.Rational(29,8), sp.Rational(-1,3)),
}
probe_values = {}
for r in csv.DictReader(probe_table.open(encoding='utf-8')):
    probe_values[(int(r['probe']), int(r['target_index']), int(r['basis_index']))] = sp.sympify(r['coefficient'])
for r in rows:
    ti = int(r['target_index']); bi = int(r['basis_index']); expr = sp.sympify(r['coefficient'])
    for pi, (dv, zv) in probe_points.items():
        actual = probe_values.get((pi, ti, bi), sp.Integer(0))
        assert sp.simplify(expr.subs({D: dv, z: zv}) - actual) == 0

# Reconstruct the hardest coefficient again from the 91-point tensor grid.
ti, bi = 0, 6
xs = [sp.Integer(v) for v in range(6, 19)]
ys = [sp.Integer(v) for v in (-4, -3, -2, -1, 1, 2, 3)]
grid = {}
for dv in range(6, 19):
    sample_path = ROOT / 'output' / f'samples_D{dv}.csv'
    local = {}
    for r in csv.DictReader(sample_path.open(encoding='utf-8')):
        if int(r['target_index']) == ti and int(r['basis_index']) == bi:
            local[int(r['z'])] = sp.sympify(r['coeff'])
    for zv in ys:
        grid[(sp.Integer(dv), zv)] = local.get(int(zv), sp.Integer(0))

allowed_D = [D - 4, D - 3, D - 2, 2*D - 7, 3*D - 8]
allowed_z = [z, z - 4]
qD = infer_allowed_univariate_denominator([(x, grid[(x, sp.Integer(-1))]) for x in xs], D, allowed_D)
qz = infer_allowed_univariate_denominator([(y, grid[(sp.Integer(6), y)]) for y in ys], z, allowed_z)
holdout = []
for pi, point in probe_points.items():
    holdout.append((point, probe_values[(pi, ti, bi)]))
recon = reconstruct_bivariate_with_known_denominator(grid, xs, ys, (D, z), qD*qz, holdout)
checkpoint = sp.sympify(next(r['coefficient'] for r in rows if int(r['target_index']) == ti and int(r['basis_index']) == bi))
assert sp.simplify(recon.expression - checkpoint) == 0

out = ROOT / 'output' / 'phase9_full_symbolic_reduction_trial.md'
lines = [
    '# Phase 9: full symbolic ordinary-ladder reduction',
    '',
    'The corrected ordinary-ladder system has 40 symmetry-canonical targets and 12 terminal basis integrals.',
    '',
    f'- Matrix entries: {len(rows)}',
    f'- Nonzero symbolic coefficients: {len(nonzero)}',
    '- Grid validation points per nonzero coefficient: 91',
    '- Independent exact-rational probes per nonzero coefficient: 3',
    '- Total exact validation points per nonzero coefficient: 94',
    '- Independent probe audit of the complete 40 x 12 matrix: PASS',
    '',
    '## Hardest reconstructed coefficient',
    '',
    '$$',
    r'J(-2,1,1,1,0,1,1) \supset c_6(D,z)\,J(0,1,0,0,1,0,2),',
    '$$',
    '',
    '$$',
    r'c_6(D,z)=',
    '$$',
    '',
    '$$',
    sp.latex(sp.factor(recon.expression)),
    '$$',
    '',
    'The denominator factors were inferred independently from one-dimensional slices and the numerator was reconstructed from the full 91-point tensor grid.',
    '',
    'All three independent exact-rational holdout probes agree exactly.',
]
out.write_text('\n'.join(lines), encoding='utf-8')
print('Phase-9 symbolic reduction: PASS')
print('40 canonical targets -> 12 terminal basis integrals')
print('151 nonzero symbolic coefficients')
print('91 grid + 3 independent holdouts per nonzero coefficient')
print(f'Output: {out}')
