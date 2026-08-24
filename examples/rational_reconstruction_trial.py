from pathlib import Path
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    target_aware_closure,
    generate_ibp_system,
    canonicalize_ibp_system,
    prune_zero_sectors,
    specialize_ibp_system,
    laporta_forward_eliminate,
    reduce_integral,
    reconstruct_reduction_coefficients,
    integral_latex,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family,
    ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'rational_reconstruction_trial.md'

family = ordinary_ladder_ibp_family()
symmetries = ordinary_ladder_integral_symmetries()
D, z, m2 = sp.symbols('D z m2')

table = load_ladder_coefficient_table(ROOT / 'data' / 'ladder_corrected_spin_sum_72_coefficients.csv')
targets = [IntegralIndex(idx.as_tuple()) for idx in table]
closure_probes = (
    {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1},
    {D: sp.Rational(41,11), z: sp.Rational(3,7), m2: 1},
    {D: sp.Rational(29,8), z: sp.Rational(-1,3), m2: 1},
)
closure = target_aware_closure(
    family,
    targets,
    closure_probes,
    symmetries=symmetries,
    vectors=('k','l','p',"p'"),
    neighborhood_degree=1,
    max_rounds=4,
)
masters = tuple(closure.stable_candidates)
master_set = set(masters)

eqs = generate_ibp_system(family, closure.final_seeds, vectors=('k','l','p',"p'"))
eqs = canonicalize_ibp_system(eqs, symmetries)
eqs = prune_zero_sectors(family, eqs)

training_points = (
    {D:sp.Rational(7,2),  z:sp.Rational(1,5),  m2:1},
    {D:sp.Rational(18,5), z:sp.Rational(-1,4), m2:1},
    {D:sp.Rational(19,5), z:sp.Rational(1,3),  m2:1},
    {D:sp.Rational(21,5), z:sp.Rational(3,7),  m2:1},
    {D:sp.Rational(23,6), z:sp.Rational(-2,5), m2:1},
    {D:sp.Rational(17,5), z:sp.Rational(2,3),  m2:1},
    {D:sp.Rational(39,10),z:sp.Rational(1,7),  m2:1},
    {D:sp.Rational(31,8), z:sp.Rational(-1,2), m2:1},
    {D:sp.Rational(43,11),z:sp.Rational(4,9),  m2:1},
    {D:sp.Rational(27,7), z:sp.Rational(3,8),  m2:1},
    {D:sp.Rational(16,5), z:sp.Rational(-2,7), m2:1},
    {D:sp.Rational(22,5), z:sp.Rational(2,3),  m2:1},
)
holdout_points = (
    {D:sp.Rational(33,8), z:sp.Rational(5,11), m2:1},
    {D:sp.Rational(25,7), z:sp.Rational(-3,8), m2:1},
    {D:sp.Rational(47,12),z:sp.Rational(1,4),  m2:1},
)

sample_points = training_points + holdout_points
rules_by_point = []
for point in sample_points:
    peqs = specialize_ibp_system(eqs, point)
    rules = laporta_forward_eliminate(
        peqs,
        family=None,
        prune_scaleless=False,
        protected=master_set,
    )
    rules_by_point.append(rules)

# Two representative corrected-route targets: one exposes z dependence,
# the other a genuinely rational D dependence.
representatives = (
    IntegralIndex((-1,0,0,1,1,1,1)),
    IntegralIndex((0,0,1,1,0,1,1)),
)

results = []
for target in representatives:
    sampled_reductions = [reduce_integral(target, rules) for rules in rules_by_point]
    for red in sampled_reductions:
        if not set(red).issubset(master_set):
            raise RuntimeError(f'Reduction of {target.powers} contains a non-master candidate.')
    ntrain = len(training_points)
    recon = reconstruct_reduction_coefficients(
        sampled_reductions[:ntrain],
        training_points,
        masters,
        (D,z),
        holdout_reductions=sampled_reductions[ntrain:],
        holdout_points=holdout_points,
        max_numerator_degree=2,
        max_denominator_degree=2,
    )
    results.append((target, recon))

lines = ['# QEDCalc exact rational reconstruction trial', '']
lines += ['## 1. Purpose', '']
lines += ['This trial reconstructs symbolic $D,z$-dependent Laporta reduction coefficients from exact-rational generic-point samples of the corrected ordinary-ladder route.', '']
lines += [f'Training points: **{len(training_points)}**. Holdout points: **{len(holdout_points)}**.', '']
lines += ['No floating-point samples are used. A reconstructed rational function is accepted only when it reproduces every training point and every independent holdout point exactly.', '']

lines += ['## 2. Stable candidate basis used by the probe reduction', '']
for n, master in enumerate(masters, 1):
    lines += [f'$M_{n}$:', '', '$$', integral_latex(master), '$$', '']

lines += ['## 3. Reconstructed representative reductions', '']
for target, recon in results:
    lines += ['Target:', '', '$$', integral_latex(target), '$$', '']
    pieces = []
    for master, result in recon.items():
        midx = masters.index(master) + 1
        pieces.append((midx, result.expression, result))
    if not pieces:
        lines += ['No nonzero master coefficient was reconstructed.', '']
        continue
    rhs = ' + '.join(rf'\left({sp.latex(expr)}\right)M_{{{midx}}}' for midx, expr, _ in pieces)
    lines += ['$$', integral_latex(target) + '=' + rhs, '$$', '']
    for midx, expr, meta in pieces:
        lines += [f'- $M_{midx}$ coefficient: `{sp.sstr(expr)}`; numerator degree {meta.numerator_degree}, denominator degree {meta.denominator_degree}; holdout checks {meta.holdout_count}.']
    lines += ['']

lines += ['## 4. Interpretation', '']
lines += ['This is the first QEDCalc step that reconstructs an analytic Laporta coefficient as a function of symbolic kinematics from generic exact-rational reductions rather than merely measuring rank at probe points.', '']
lines += ['The present demo intentionally reconstructs two low-complexity representative targets. Extending this to every corrected target requires adaptive degree bounds, sample scheduling, pole avoidance, and preferably modular/finite-field acceleration.', '']

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
for target, recon in results:
    print('Target', target.powers)
    for master, result in recon.items():
        print(' ', master.powers, '->', sp.factor(result.expression))
