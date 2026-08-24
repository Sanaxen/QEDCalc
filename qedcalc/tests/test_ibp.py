import sympy as sp

from qedcalc.operations.ibp import (
    IntegralFamily, IntegralIndex, sp_atom,
    directional_derivative, generate_ibp_equation,
    laporta_eliminate, reduce_integral,
)
from qedcalc.operations.ladder import ordinary_ladder_ibp_family, ladder_ibp_seed_equations


def tadpole_family():
    D, m2, T = sp.symbols("D m2 T")
    kk = sp_atom("k","k")
    return IntegralFamily(
        name="tadpole",
        denominator_names=("T",),
        denominator_exprs=(kk-m2,),
        loop_momenta=("k",),
        external_momenta=(),
        scalar_product_rules={kk:T+m2},
        dimension_symbol=D,
    )


def test_directional_derivative_k2():
    kk = sp_atom("k","k")
    assert directional_derivative(kk, "k", "k") == 2*kk


def test_tadpole_ibp_identity():
    D, m2 = sp.symbols("D m2")
    fam = tadpole_family()
    eq = generate_ibp_equation(fam, (1,), "k", "k")
    J1 = IntegralIndex((1,))
    J2 = IntegralIndex((2,))
    assert sp.simplify(eq.coefficient(J1) - (D-2)) == 0
    assert sp.simplify(eq.coefficient(J2) + 2*m2) == 0


def test_tadpole_laporta_reduction():
    D, m2 = sp.symbols("D m2")
    fam = tadpole_family()
    eq = generate_ibp_equation(fam, (1,), "k", "k")
    rules = laporta_eliminate((eq,), protected=(IntegralIndex((1,)),))
    result = reduce_integral((2,), rules)
    assert set(result) == {IntegralIndex((1,))}
    assert sp.simplify(result[IntegralIndex((1,))] - (D-2)/(2*m2)) == 0


def test_ordinary_ladder_family_has_seven_denominators():
    fam = ordinary_ladder_ibp_family()
    assert fam.denominator_names == ("K","L","H","E1","E2","E3","E4")
    assert fam.loop_momenta == ("k","l")


def test_ordinary_ladder_base_seed_generates_eight_ibps():
    fam, equations = ladder_ibp_seed_equations()
    assert len(equations) == 8
    assert all(eq.terms for eq in equations)
    assert {eq.label for eq in equations} == {
        "d/dk · k", "d/dk · l", "d/dk · p", "d/dk · p'",
        "d/dl · k", "d/dl · l", "d/dl · p", "d/dl · p'",
    }


def test_ordinary_ladder_ibp_has_no_scalar_product_atoms():
    _, equations = ladder_ibp_seed_equations()
    for eq in equations:
        for coeff in eq.terms.values():
            assert not any(str(s).startswith("SP__") for s in coeff.free_symbols)


def test_sector_and_first_neighbor_seed_generation():
    from qedcalc.operations.ibp import sector_signature, sector_id, first_neighbor_seeds
    base = IntegralIndex((1,1,0,1,1,1,1))
    assert sector_signature(base) == (1,1,0,1,1,1,1)
    assert sector_id(base) == 123
    seeds = first_neighbor_seeds(base)
    assert len(seeds) == 8
    assert IntegralIndex((1,1,-1,1,1,1,1)) in seeds
    assert IntegralIndex((2,1,0,1,1,1,1)) in seeds



def test_ordinary_ladder_scaleless_massless_vacuum_sectors():
    from qedcalc.operations.ibp import is_scaleless_zero_sector, zero_sector_ids
    fam = ordinary_ladder_ibp_family()
    assert is_scaleless_zero_sector(fam, IntegralIndex((1,1,1,0,0,0,0)))
    assert is_scaleless_zero_sector(fam, IntegralIndex((1,0,0,0,0,0,0)))
    assert not is_scaleless_zero_sector(fam, IntegralIndex((1,0,0,1,0,0,0)))
    assert set(zero_sector_ids(fam)) == set(range(8))


def test_zero_sector_pruning_removes_scaleless_integrals():
    from qedcalc.operations.ibp import IBPEquation, prune_zero_sectors
    fam = ordinary_ladder_ibp_family()
    zero = IntegralIndex((1,1,0,0,0,0,0))
    physical = IntegralIndex((1,0,0,1,0,0,0))
    eq = IBPEquation({zero: sp.Integer(3), physical: sp.Integer(5)})
    pruned = prune_zero_sectors(fam, (eq,))
    assert len(pruned) == 1
    assert zero not in pruned[0].terms
    assert pruned[0].coefficient(physical) == 5


def test_bounded_seed_degree_two_extends_first_neighbor():
    from qedcalc.operations.ibp import bounded_seed_domain
    base = IntegralIndex((1,1,0,1,1,1,1))
    degree1 = set(bounded_seed_domain(base, 1))
    degree2 = set(bounded_seed_domain(base, 2))
    assert len(degree1) == 8
    assert degree1 < degree2
    assert IntegralIndex((3,1,0,1,1,1,1)) in degree2
    assert IntegralIndex((2,2,0,1,1,1,1)) in degree2
    assert IntegralIndex((1,1,-2,1,1,1,1)) in degree2


def test_sector_rank_prefers_higher_sector_and_more_dots():
    from qedcalc.operations.ibp import sector_rank
    lower = IntegralIndex((1,1,0,1,0,0,0))
    higher = IntegralIndex((1,1,0,1,1,0,0))
    dotted = IntegralIndex((2,1,0,1,1,0,0))
    assert sector_rank(higher) > sector_rank(lower)
    assert sector_rank(dotted) > sector_rank(higher)



def test_forward_laporta_tadpole_reduction():
    from qedcalc.operations.ibp import laporta_forward_eliminate
    D, m2 = sp.symbols("D m2")
    fam = tadpole_family()
    eq = generate_ibp_equation(fam, (1,), "k", "k")
    rules = laporta_forward_eliminate((eq,), protected=(IntegralIndex((1,)),))
    result = reduce_integral((2,), rules)
    assert set(result) == {IntegralIndex((1,))}
    assert sp.simplify(result[IntegralIndex((1,))] - (D-2)/(2*m2)) == 0


def test_ordinary_ladder_symmetry_group_has_four_elements():
    from qedcalc.operations.ladder import ordinary_ladder_integral_symmetries
    syms = ordinary_ladder_integral_symmetries()
    assert len(syms) == 4
    perms = {s.permutation for s in syms}
    assert (0,1,2,6,5,4,3) in perms
    assert (2,1,0,4,3,6,5) in perms


def test_ordinary_ladder_symmetry_maps_expected_integral():
    from qedcalc.operations.ladder import ordinary_ladder_integral_symmetries
    from qedcalc.operations.ibp import canonicalize_integral
    syms = ordinary_ladder_integral_symmetries()
    a = IntegralIndex((2,1,0,3,4,5,6))
    orbit = {s.apply(a).powers for s in syms}
    assert (0,1,2,4,3,6,5) in orbit
    assert (2,1,0,6,5,4,3) in orbit
    assert canonicalize_integral(a, syms).powers == min(orbit)


def test_degree_two_seed_symmetry_reduces_36_to_24():
    from qedcalc.operations.ibp import bounded_seed_domain, canonicalize_seed_set
    from qedcalc.operations.ladder import ordinary_ladder_integral_symmetries
    base = IntegralIndex((1,1,0,1,1,1,1))
    raw = bounded_seed_domain(base, 2)
    canonical = canonicalize_seed_set(raw, ordinary_ladder_integral_symmetries())
    assert len(raw) == 36
    assert len(canonical) == 24


def test_specialized_degree_two_symmetry_probe():
    from qedcalc.operations.ibp import (
        bounded_seed_domain, generate_ibp_system, canonicalize_ibp_system,
        prune_zero_sectors, specialize_ibp_system, laporta_forward_eliminate,
    )
    from qedcalc.operations.ladder import ordinary_ladder_integral_symmetries
    fam = ordinary_ladder_ibp_family()
    base = IntegralIndex((1,1,0,1,1,1,1))
    eqs = generate_ibp_system(fam, bounded_seed_domain(base, 2), vectors=("k","l","p","p'"))
    ceqs = prune_zero_sectors(fam, canonicalize_ibp_system(eqs, ordinary_ladder_integral_symmetries()))
    assert len({i for eq in ceqs for i in eq.terms}) == 335
    D, z, m2 = sp.symbols("D z m2")
    probe = specialize_ibp_system(ceqs, {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1})
    rules = laporta_forward_eliminate(probe, family=None, prune_scaleless=False)
    assert len(rules) == 162



def test_target_aware_closure_finds_probe_stable_ladder_candidates():
    from qedcalc.operations.ibp import target_aware_closure, IntegralIndex
    from qedcalc.operations.ladder import (
        ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries,
        load_ladder_coefficient_table,
    )
    fam = ordinary_ladder_ibp_family()
    syms = ordinary_ladder_integral_symmetries()
    table = load_ladder_coefficient_table('data/ladder_Ddim_75_coefficients.csv')
    targets = [IntegralIndex(i.as_tuple()) for i in table]
    D, z, m2 = sp.symbols('D z m2')
    probes = (
        {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1},
        {D: sp.Rational(41,11), z: sp.Rational(3,7), m2: 1},
        {D: sp.Rational(29,8), z: sp.Rational(-1,3), m2: 1},
    )
    result = target_aware_closure(
        fam, targets, probes, symmetries=syms,
        vectors=('k','l','p',"p'"), max_rounds=4,
    )
    assert len(result.targets) == 42
    assert result.status == 'stable_candidates'
    assert [r.seed_count for r in result.rounds] == [42, 80]
    assert [r.pivot_counts for r in result.rounds] == [(286,286,286), (562,562,562)]
    assert len(result.stable_candidates) == 7
    assert all(r.stable_across_probes for r in result.rounds)


def test_exact_bivariate_rational_reconstruction_with_holdouts():
    import sympy as sp
    from qedcalc.operations.ibp import reconstruct_rational_function
    D, z = sp.symbols('D z')
    f = -(D - 2) / (2 * (D - 3)) + z / 2
    train_points = [
        (sp.Rational(7,2), sp.Rational(1,5)),
        (sp.Rational(18,5), sp.Rational(-1,4)),
        (sp.Rational(19,5), sp.Rational(1,3)),
        (sp.Rational(21,5), sp.Rational(3,7)),
        (sp.Rational(23,6), sp.Rational(-2,5)),
        (sp.Rational(17,5), sp.Rational(2,3)),
        (sp.Rational(39,10), sp.Rational(1,7)),
        (sp.Rational(31,8), sp.Rational(-1,2)),
        (sp.Rational(43,11), sp.Rational(4,9)),
        (sp.Rational(27,7), sp.Rational(3,8)),
    ]
    hold_points = [
        (sp.Rational(16,5), sp.Rational(-2,7)),
        (sp.Rational(44,11), sp.Rational(5,13)),
    ]
    train = [(pt, sp.cancel(f.subs({D:pt[0], z:pt[1]}))) for pt in train_points]
    hold = [(pt, sp.cancel(f.subs({D:pt[0], z:pt[1]}))) for pt in hold_points]
    result = reconstruct_rational_function(train, (D,z), 2, 2, hold)
    assert sp.simplify(result.expression - f) == 0
    assert result.holdout_count == 2


def test_reconstruct_reduction_coefficients_skips_zero_masters():
    import sympy as sp
    from qedcalc.operations.ibp import IntegralIndex, reconstruct_reduction_coefficients
    D, z = sp.symbols('D z')
    m1, m2, m3 = IntegralIndex((1,0)), IntegralIndex((0,1)), IntegralIndex((1,1))
    points = [
        {D:sp.Rational(7,2), z:sp.Rational(1,5)},
        {D:sp.Rational(18,5), z:sp.Rational(-1,4)},
        {D:sp.Rational(19,5), z:sp.Rational(1,3)},
        {D:sp.Rational(21,5), z:sp.Rational(3,7)},
        {D:sp.Rational(23,6), z:sp.Rational(-2,5)},
        {D:sp.Rational(17,5), z:sp.Rational(2,3)},
    ]
    reductions=[]
    for pt in points:
        reductions.append({m1: sp.cancel(pt[z]/2-2), m2: sp.Integer(1)})
    result = reconstruct_reduction_coefficients(reductions, points, (m1,m2,m3), (D,z), max_numerator_degree=1, max_denominator_degree=1)
    assert set(result) == {m1,m2}
    assert sp.simplify(result[m1].expression - (z/2-2)) == 0
    assert result[m2].expression == 1


def test_batch_reconstruction_refuses_nonmaster_residue():
    import sympy as sp
    from qedcalc.operations.ibp import (
        IntegralIndex, ReductionRule, batch_reconstruct_targets,
    )
    D, z = sp.symbols('D z')
    target = IntegralIndex((2,0))
    master = IntegralIndex((1,0))
    residue = IntegralIndex((0,1))
    points = ({D:sp.Rational(7,2), z:sp.Rational(1,5)}, {D:sp.Rational(18,5), z:sp.Rational(1,3)})
    rules = ((ReductionRule(target, {master:1, residue:1}),),) * 2
    result = batch_reconstruct_targets((target,), (master,), rules, points, (D,z), 1, 1, 1)
    assert len(result.residual) == 1
    assert result.residual[0].residuals == (residue,)
    assert not result.reconstructed


def test_batch_reconstruction_accepts_closed_exact_relation():
    import sympy as sp
    from qedcalc.operations.ibp import IntegralIndex, ReductionRule, batch_reconstruct_targets
    D, z = sp.symbols('D z')
    target = IntegralIndex((2,0)); master = IntegralIndex((1,0))
    pts = (
        {D:sp.Rational(7,2), z:sp.Rational(1,5)},
        {D:sp.Rational(18,5), z:sp.Rational(1,3)},
        {D:sp.Rational(19,5), z:sp.Rational(-1,4)},
        {D:sp.Rational(21,5), z:sp.Rational(3,7)},
    )
    rule_sets = tuple((ReductionRule(target, {master:sp.cancel(p[z]/2-2)}),) for p in pts)
    result = batch_reconstruct_targets((target,), (master,), rule_sets, pts, (D,z), 3, 1, 1)
    assert len(result.reconstructed) == 1
    rec = result.reconstructed[0].coefficients[master]
    assert sp.simplify(rec.expression - (z/2-2)) == 0
    assert rec.holdout_count == 1


def test_residue_scheduler_ranks_new_high_impact_sector_first():
    from qedcalc.operations.ibp import (
        IntegralIndex, ReductionRule, residue_impact_profile,
        residue_sector_profile, schedule_residue_sectors,
    )
    m = IntegralIndex((1,0,0))
    r_hi = IntegralIndex((0,1,2))
    r_old = IntegralIndex((1,0,2))
    t1 = IntegralIndex((2,0,0)); t2 = IntegralIndex((3,0,0)); t3 = IntegralIndex((4,0,0))
    rules = (
        ReductionRule(t1, {m:1, r_hi:1}),
        ReductionRule(t2, {m:1, r_hi:1}),
        ReductionRule(t3, {m:1, r_old:1}),
    )
    impacts = residue_impact_profile((t1,t2,t3), rules, (m,), existing_seeds=(r_old,))
    sectors = residue_sector_profile(impacts)
    assert sectors[0].impact == 2
    assert sectors[0].new_seed_cost == 1
    batch = schedule_residue_sectors(sectors, max_new_seeds=1)
    assert batch.new_seeds == (r_hi,)
    assert batch.predicted_impact == 2


def test_residue_scheduler_skips_existing_only_sector():
    from qedcalc.operations.ibp import (
        IntegralIndex, ReductionRule, residue_impact_profile,
        residue_sector_profile, schedule_residue_sectors,
    )
    m = IntegralIndex((1,0))
    r = IntegralIndex((0,2))
    t = IntegralIndex((2,0))
    rules = (ReductionRule(t, {m:1, r:1}),)
    impacts = residue_impact_profile((t,), rules, (m,), existing_seeds=(r,))
    sectors = residue_sector_profile(impacts)
    assert sectors[0].new_seed_cost == 0
    assert sectors[0].score == 0
    batch = schedule_residue_sectors(sectors, max_new_seeds=1)
    assert batch.new_seeds == ()

def test_directional_depth2_seed_generation_is_bounded():
    from qedcalc.operations.ibp import directional_depth2_seeds
    base = IntegralIndex((1,1,0,1,1,1,1))
    seeds = directional_depth2_seeds(base)
    assert IntegralIndex((3,1,0,1,1,1,1)) in seeds
    assert IntegralIndex((1,1,-2,1,1,1,1)) in seeds
    assert len(seeds) <= 7


def test_directional_depth2_diagnostic_runs_on_tadpole():
    from qedcalc.operations.ibp import (
        diagnose_directional_depth2_irreducibility,
        specialize_ibp_system, laporta_forward_eliminate,
    )
    D, m2 = sp.symbols('D m2')
    fam = tadpole_family()
    base_eq = generate_ibp_equation(fam, (1,), 'k', 'k')
    probe = {D: sp.Rational(7,2), m2: 1}
    base_rules = laporta_forward_eliminate(
        specialize_ibp_system((base_eq,), probe),
        protected=(IntegralIndex((1,)),),
    )
    diag = diagnose_directional_depth2_irreducibility(
        fam, IntegralIndex((1,)), base_rules, probe,
        existing_seeds=(IntegralIndex((1,)),),
        protected=(IntegralIndex((1,)),), vectors=('k',),
    )
    assert diag.residue == IntegralIndex((1,))
    assert isinstance(diag.pivoting_seeds, tuple)


def test_build_specialized_laporta_rules_matches_tadpole_reduction():
    from qedcalc.operations.ibp import build_specialized_laporta_rules
    D, m2 = sp.symbols('D m2')
    fam = tadpole_family()
    rules = build_specialized_laporta_rules(
        fam, (IntegralIndex((1,)),),
        {D: sp.Rational(7,2), m2: 1},
        protected=(IntegralIndex((1,)),), vectors=('k',),
    )
    red = reduce_integral((2,), rules)
    assert red[IntegralIndex((1,))] == sp.Rational(3,4)


def test_persistent_integral_reducer_matches_reduce_integral():
    from qedcalc.operations.ibp import IntegralIndex, ReductionRule, build_integral_reducer, reduce_integral
    import sympy as sp
    a=IntegralIndex((2,)); b=IntegralIndex((1,)); c=IntegralIndex((0,))
    rules=(ReductionRule(a,{b:sp.Rational(2)}), ReductionRule(b,{c:sp.Rational(3)}))
    reducer=build_integral_reducer(rules)
    assert reducer(a)==reduce_integral(a,rules)=={c:sp.Integer(6)}
    before=reducer.cache_info().hits
    assert reducer(a)=={c:sp.Integer(6)}
    assert reducer.cache_info().hits>before
