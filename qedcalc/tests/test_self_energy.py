import sympy as sp
from qedcalc import parse_latex
from qedcalc.operations.algebra import expand_expression, normalize_noncommutative_products
from qedcalc.operations.dirac import contract_gamma
from qedcalc.operations.simplify import simplify_expression
from qedcalc.operations.self_energy import *

def test_self_energy_gamma_outer_scalar_identity():
    e=parse_latex(r"\gamma^\alpha(m+\rlap{/}r-\rlap{/}l)\gamma_\alpha")
    out=simplify_expression(contract_gamma(normalize_noncommutative_products(expand_expression(e))))
    assert out is not None

def test_uv_cancellation():
    a,m,s=sp.symbols('a m s')
    assert sp.simplify(uv_cancellation_numerator(a,m,s)) == 0

def test_delta_onshell():
    a,m,lam,r2=sp.symbols('a m lam r2')
    assert sp.simplify(self_energy_delta(a,r2,m,lam).subs(r2,m**2)-self_energy_delta0(a,m,lam)) == 0

def test_finite_expected():
    assert finite_part_expected() == -sp.Rational(1,24)-sp.pi**2/18

def test_total_coefficient():
    rho=sp.symbols('rho', positive=True)
    assert sp.simplify(total_self_energy_coefficient(rho) - (sp.log(rho)+sp.Rational(11,24)-sp.pi**2/18)) == 0
