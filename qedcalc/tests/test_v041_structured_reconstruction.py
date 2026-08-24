from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    infer_allowed_univariate_denominator,
    reconstruct_bivariate_with_known_denominator,
)


def test_infer_allowed_univariate_denominator():
    x = sp.Symbol('x')
    expr = (x + 2) / ((x - 3) * (2*x - 5))
    samples = [(sp.Integer(v), sp.cancel(expr.subs(x, v))) for v in range(6, 13)]
    den = infer_allowed_univariate_denominator(samples, x, [x - 3, 2*x - 5])
    expected = sp.Poly((x - 3) * (2*x - 5), x).monic().as_expr()
    assert sp.simplify(den - expected) == 0


def test_reconstruct_bivariate_with_known_denominator():
    x, y = sp.symbols('x y')
    expr = (x*y + 2*x - y + 3) / ((x - 1) * (y - 2))
    xs = [sp.Integer(v) for v in (3, 4, 5, 6)]
    ys = [sp.Integer(v) for v in (-2, -1, 0, 1, 3)]
    grid = {(a, b): sp.cancel(expr.subs({x: a, y: b})) for a in xs for b in ys}
    holdouts = [
        ((sp.Rational(7, 2), sp.Rational(1, 2)), sp.cancel(expr.subs({x: sp.Rational(7,2), y: sp.Rational(1,2)}))),
        ((sp.Rational(11, 3), sp.Rational(-3, 2)), sp.cancel(expr.subs({x: sp.Rational(11,3), y: sp.Rational(-3,2)}))),
    ]
    out = reconstruct_bivariate_with_known_denominator(
        grid, xs, ys, (x, y), (x - 1)*(y - 2), holdout_samples=holdouts
    )
    assert sp.simplify(out.expression - expr) == 0
    assert out.training_count == len(xs) * len(ys)
    assert out.holdout_count == 2


def test_v041_symbolic_reduction_checkpoint_shape_and_hard_coefficient():
    root = Path(__file__).resolve().parents[1]
    path = root / 'data' / 'ladder_corrected_40target_12basis_symbolic_reduction.csv'
    rows = list(csv.DictReader(path.open(encoding='utf-8')))
    assert len(rows) == 40 * 12
    assert sum(int(r['nonzero']) for r in rows) == 151
    hard = next(r for r in rows if int(r['target_index']) == 0 and int(r['basis_index']) == 6)
    D, z = sp.symbols('D z')
    got = sp.sympify(hard['coefficient'])
    expected = (
        3*D**4*z**3 - 10*D**4*z**2 - 528*D**4*z - 512*D**4
        - 35*D**3*z**3 + 170*D**3*z**2 + 6368*D**3*z + 6016*D**3
        + 150*D**2*z**3 - 1002*D**2*z**2 - 28528*D**2*z - 26624*D**2
        - 280*D*z**3 + 2504*D*z**2 + 56240*D*z + 52704*D
        + 192*z**3 - 2272*z**2 - 41152*z - 39424
    ) / (4*(D - 4)*(D - 3)*(D - 2)*(2*D - 7)*(3*D - 8)*(z - 4))
    assert sp.simplify(got - expected) == 0
    assert hard['validation'] == 'exact'
    assert int(hard['grid_validation_points']) == 91
    assert int(hard['independent_probe_points']) == 3
