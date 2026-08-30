import sympy as sp
from qedcalc.operations.ibp import (
    IntegralIndex, IBPEquation, ReductionRule, ResidueImpact,
    reduce_ibp_equation_with_rules, extend_laporta_rules_incrementally,
    NeighborhoodSeedImpact, schedule_neighborhood_seeds,
)


def test_reduce_ibp_equation_with_existing_rule():
    a=IntegralIndex((2,)); b=IntegralIndex((1,)); c=IntegralIndex((0,))
    base=(ReductionRule(a,{b:sp.Integer(2)}),)
    eq=IBPEquation({a:sp.Integer(3),c:sp.Integer(1)})
    red=reduce_ibp_equation_with_rules(eq,base)
    assert red.terms == {b:sp.Integer(6), c:sp.Integer(1)}


def test_incremental_extension_adds_only_new_pivot():
    a=IntegralIndex((3,)); b=IntegralIndex((2,)); c=IntegralIndex((1,))
    base=(ReductionRule(a,{b:sp.Integer(1)}),)
    eq=IBPEquation({a:sp.Integer(1),b:sp.Integer(1),c:sp.Integer(-1)})
    rules=extend_laporta_rules_incrementally(base,(eq,))
    assert {r.lhs for r in rules} == {a,b}


def test_neighborhood_batch_uses_marginal_target_coverage():
    s1=IntegralIndex((1,0)); s2=IntegralIndex((0,1)); s3=IntegralIndex((1,1))
    t1=IntegralIndex((2,0)); t2=IntegralIndex((0,2)); t3=IntegralIndex((2,2))
    impacts=(
      NeighborhoodSeedImpact(s1,8,(),(t1,t2)),
      NeighborhoodSeedImpact(s2,8,(),(t2,t3)),
      NeighborhoodSeedImpact(s3,8,(),(t1,)),
    )
    batch=schedule_neighborhood_seeds(impacts,max_new_seeds=2)
    assert len(batch.selected)==2
    assert set(batch.covered_targets)=={t1,t2,t3}
