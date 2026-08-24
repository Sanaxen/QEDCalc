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


def test_v053_raw_self_energy_pair_reconstructs_bare_parametric_checkpoints():
    from qedcalc.operations.self_energy import self_energy_raw_bare_parametric_integrand
    r = self_energy_raw_bare_parametric_integrand()
    assert r.base_term_count == 55
    assert all(value == 0 for value in r.sample_checks)


def test_v053_raw_self_energy_denominator_polynomials_are_generated():
    from qedcalc.operations.self_energy import self_energy_raw_bare_parametric_integrand
    r = self_energy_raw_bare_parametric_integrand()
    x,y,u,v,rho=sp.symbols('x y u v rho')
    assert sp.factor(r.Delta - (u*v+u*y+v*x+v*y+x*y)) == 0
    expected = rho**2*(u+v)*r.Delta + (y+v)*(x+y)**2 - 2*y*(x+y)*y + (x+y+u)*y**2
    assert sp.expand(r.F-expected) == 0


def test_v053_raw_self_energy_uv_subsector_is_regenerated():
    from qedcalc.operations.self_energy import self_energy_raw_uv_subdivergence
    uv = self_energy_raw_uv_subdivergence()
    X = sp.Symbol('X', positive=True)
    assert uv.archived_difference == 0
    assert sp.factor(uv.coefficient_rho0 - (X-1)*(3*X-5)/4) == 0


def test_v054_sigmaR_HA_denominator_is_rationalized_delta0_plus_hD():
    from qedcalc.operations.self_energy import self_energy_HA_scalar_denominator
    a,z,D=sp.symbols('a z D')
    assert sp.expand(self_energy_HA_scalar_denominator(a,z,D,1,0) - (a**2+z*a*(1-a)*D)) == 0


def test_v054_renormalized_outer_bridge_reconstructs_GA_exactly():
    from qedcalc.operations.self_energy import self_energy_renormalized_outer_to_GA
    r=self_energy_renormalized_outer_to_GA()
    assert r.checkpoint_residual == 0
    assert r.normalization_factor == -sp.Rational(1,16)


def test_v054_HA_q_denominator_streams_vanish_after_projector_gaussian_reduction():
    from qedcalc.operations.self_energy import self_energy_renormalized_outer_to_GA
    r=self_energy_renormalized_outer_to_GA()
    assert r.denominator_D_stream == 0
    assert r.denominator_Q_stream == 0


def test_v054_HA_projector_polynomials_have_stable_small_term_counts():
    from qedcalc.operations.self_energy import self_energy_renormalized_outer_to_GA
    r=self_energy_renormalized_outer_to_GA()
    assert r.projector_term_counts == (("right",20,10),("left",20,10))


def test_v054_self_energy_raw_to_final_audit_closes_both_diagrams():
    from qedcalc.operations.self_energy import self_energy_raw_to_final_audit
    r=self_energy_raw_to_final_audit()
    assert all(x==0 for x in r.raw_sample_checks)
    assert r.raw_uv_archived_difference == 0
    assert r.renormalized_GA_residual == 0
    assert r.total_checkpoint_residual == 0
