import sympy as sp
from qedcalc.operations.ibp import (
    IntegralFamily, IntegralIndex, ReductionRule,
    diagnose_first_neighbor_irreducibility, promote_local_master_candidates,
    sp_atom,
)


def test_local_irreducibility_diagnostic_can_promote_when_no_neighbor_pivots_target():
    D = sp.Symbol('D')
    k2 = sp_atom('k','k')
    T = sp.Symbol('T')
    fam = IntegralFamily(
        name='toy', denominator_names=('T',), denominator_exprs=(k2,),
        loop_momenta=('k',), external_momenta=(), scalar_product_rules={k2:T},
        dimension_symbol=D,
    )
    residue = IntegralIndex((1,))
    # Protect the residue so no local row is allowed to pivot on it.
    diag = diagnose_first_neighbor_irreducibility(
        fam, residue, (), {D: sp.Rational(7,2)}, protected=(residue,), vectors=('k',)
    )
    assert diag.locally_irreducible
    assert promote_local_master_candidates((diag,)) == (residue,)


def test_local_irreducibility_diagnostic_reports_metadata():
    D = sp.Symbol('D')
    k2 = sp_atom('k','k')
    T = sp.Symbol('T')
    fam = IntegralFamily(
        name='toy', denominator_names=('T',), denominator_exprs=(k2,),
        loop_momenta=('k',), external_momenta=(), scalar_product_rules={k2:T},
        dimension_symbol=D,
    )
    diag = diagnose_first_neighbor_irreducibility(
        fam, IntegralIndex((1,)), (), {D: sp.Rational(7,2)}, vectors=('k',)
    )
    assert diag.tested_seeds
    assert diag.max_new_pivots >= 0
