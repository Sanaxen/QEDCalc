from pathlib import Path
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralFamily, IntegralIndex, sp_atom,
    generate_ibp_equation, generate_ibp_system, laporta_eliminate, reduce_integral,
    ibp_equation_latex, reduction_rule_latex, first_neighbor_seeds, bounded_seed_domain,
    zero_sector_ids, prune_zero_sectors, laporta_forward_eliminate, master_candidates,
    canonicalize_seed_set, canonicalize_ibp_system, specialize_ibp_system,
)
from qedcalc.operations.ladder import ladder_ibp_seed_equations, ordinary_ladder_integral_symmetries

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'ibp_laporta_trial.md'


def math(tex):
    return f"\n$$\n{tex}\n$$\n"

D, m2 = sp.symbols('D m2')
T = sp.Symbol('T')
kk = sp_atom('k','k')
tadpole = IntegralFamily(
    name='tadpole',
    denominator_names=('T',),
    denominator_exprs=(kk-m2,),
    loop_momenta=('k',),
    external_momenta=(),
    scalar_product_rules={kk:T+m2},
    dimension_symbol=D,
)

eq_tad = generate_ibp_equation(tadpole, (1,), 'k', 'k')
rules_tad = laporta_eliminate((eq_tad,), protected=(IntegralIndex((1,)),))
red_tad = reduce_integral((2,), rules_tad)

family, ladder_eqs = ladder_ibp_seed_equations(mass_squared=1)
ladder_rules = laporta_eliminate(ladder_eqs)
all_integrals = set()
for eq in ladder_eqs:
    all_integrals.update(eq.terms)
unsolved = all_integrals - {r.lhs for r in ladder_rules}
base = IntegralIndex((1,1,0,1,1,1,1))
base_reduced = reduce_integral(base, ladder_rules)

neighbor_seeds = first_neighbor_seeds(base)
neighbor_eqs = generate_ibp_system(family, neighbor_seeds, vectors=('k','l','p',"p'"))
neighbor_integrals = set()
for eq in neighbor_eqs:
    neighbor_integrals.update(eq.terms)

zero_ids = zero_sector_ids(family)
neighbor_pruned = prune_zero_sectors(family, neighbor_eqs)
forward_rules = laporta_forward_eliminate(neighbor_pruned, family=None, prune_scaleless=False)
forward_masters = master_candidates(neighbor_pruned, forward_rules, family=None, prune_scaleless=False)

degree2_seeds = bounded_seed_domain(base, max_extra_degree=2)
degree2_eqs = generate_ibp_system(family, degree2_seeds, vectors=('k','l','p',"p'"))
degree2_integrals = set()
for eq in degree2_eqs:
    degree2_integrals.update(eq.terms)

ladder_symmetries = ordinary_ladder_integral_symmetries()
degree2_canonical_seeds = canonicalize_seed_set(degree2_seeds, ladder_symmetries)
degree2_canonical_eqs = canonicalize_ibp_system(degree2_eqs, ladder_symmetries)
degree2_canonical_eqs = prune_zero_sectors(family, degree2_canonical_eqs)
degree2_canonical_integrals = {i for eq in degree2_canonical_eqs for i in eq.terms}
probe_subs = {sp.Symbol('D'): sp.Rational(37,10), sp.Symbol('z'): sp.Rational(2,5), sp.Symbol('m2'): sp.Integer(1)}
degree2_probe_eqs = specialize_ibp_system(degree2_canonical_eqs, probe_subs)
degree2_probe_rules = laporta_forward_eliminate(degree2_probe_eqs, family=None, prune_scaleless=False)
degree2_probe_masters = master_candidates(degree2_probe_eqs, degree2_probe_rules, family=None, prune_scaleless=False)

lines = ['# QEDCalc IBP / finite Laporta trial', '']
lines += ['## 1. One-loop sanity check', '']
lines += ['For the tadpole family $T=k^2-m^2$, QEDCalc generates', '']
lines += ['$$', ibp_equation_latex(eq_tad), '$$', '']
lines += ['Solving the finite system with $J(1)$ protected gives', '']
lines += ['$$', reduction_rule_latex(rules_tad[0]), '$$', '']

lines += ['## 2. Ordinary-ladder seven-denominator family', '']
lines += ['The family is', '']
lines += ['$$', r'J(n_K,n_L,n_H,n_1,n_2,n_3,n_4)', '$$', '']
lines += ['with denominator basis $(K,L,H,E_1,E_2,E_3,E_4)$. For the bare seed', '']
lines += ['$$', r'J(1,1,0,1,1,1,1)', '$$', '']
lines += [r"QEDCalc generates the eight canonical identities from $(\partial_k,\partial_l)$ contracted with $(k,l,p,p\prime)$.", '']
for eq in ladder_eqs:
    lines += [f'### {eq.label}', '']
    lines += ['$$', ibp_equation_latex(eq), '$$', '']

lines += ['## 3. Finite Laporta elimination on the base-seed system', '']
lines += [f'Distinct integrals appearing in the eight equations: **{len(all_integrals)}**.', '']
lines += [f'Pivots solved by the finite sparse eliminator: **{len(ladder_rules)}**.', '']
lines += [f'Integrals left unsolved in this deliberately small system: **{len(unsolved)}**.', '']
lines += ['The bare seed itself can already be solved in this finite system as', '']
# locate base rule/reduction, use recursive reduction result so no solved pivots remain
rhs = []
for idx, coeff in sorted(base_reduced.items(), key=lambda kv: kv[0].powers):
    term = r'J\left(' + ','.join(map(str,idx.powers)) + r'\right)'
    if coeff == 1:
        body = term
    elif coeff == -1:
        body = '-' + term
    else:
        body = sp.latex(sp.factor(coeff)) + r'\,' + term
    rhs.append(body)
rhs_tex = rhs[0] if rhs else '0'
for body in rhs[1:]:
    rhs_tex += body if body.startswith('-') else '+' + body
lines += ['$$', r'J(1,1,0,1,1,1,1)=' + rhs_tex, '$$', '']

lines += ['## 4. Sector ordering and zero-sector detection', '']
lines += [f'Structurally scaleless sector IDs detected in the ordinary-ladder family: **{list(zero_ids)}**.', '']
lines += ['These are the sectors built only from the massless loop-only denominators $K,L,H$; sectors containing any $E_i$ are not discarded by this conservative test.', '']

lines += ['## 5. First-neighbor forward sparse Laporta', '']
lines += [f'Generated seeds: **{len(neighbor_seeds)}**.', '']
lines += [f'Generated IBP equations: **{len(neighbor_eqs)}**.', '']
lines += [f'Distinct integrals in the first neighborhood: **{len(neighbor_integrals)}**.', '']
lines += [f'Forward sparse pivots solved: **{len(forward_rules)}**.', '']
lines += [f'Unsolved integrals in this finite domain: **{len(forward_masters)}**.', '']
lines += ['The unsolved count is not a physical master-integral count; the seed domain is not closed yet.', '']

lines += ['## 6. Bounded seed closure', '']
lines += [f'Degree-2 bounded seeds: **{len(degree2_seeds)}**.', '']
lines += [f'Degree-2 IBP equations: **{len(degree2_eqs)}**.', '']
lines += [f'Distinct integrals appearing at degree 2: **{len(degree2_integrals)}**.', '']
lines += ['Degree 2 is generated symbolically; the next subsection applies graph symmetries and a generic rational-point probe before elimination.', '']

lines += ['## 7. Ordinary-ladder family symmetry', '']
lines += [f'Symmetry-group order: **{len(ladder_symmetries)}**.', '']
lines += [f'Degree-2 seeds before/after canonicalization: **{len(degree2_seeds)} -> {len(degree2_canonical_seeds)}**.', '']
lines += [f'Distinct degree-2 integrals before/after canonicalization: **{len(degree2_integrals)} -> {len(degree2_canonical_integrals)}**.', '']
lines += [r'The generators are external exchange $p\leftrightarrow p\prime$ and the unit-Jacobian loop reparametrization $k\to k+l$, $l\to-l$.', '']

lines += ['## 8. Generic rational-point rank probe', '']
lines += ['For a fast rank diagnostic only, coefficients are specialized to', '']
lines += ['$$', r'D=\frac{37}{10},\qquad z=\frac25,\qquad m^2=1', '$$', '']
lines += [f'Forward sparse pivots at this generic exact-rational point: **{len(degree2_probe_rules)}**.', '']
lines += [f'Unsolved integrals in the finite degree-2 probe domain: **{len(degree2_probe_masters)}**.', '']
lines += ['This probe does not replace the symbolic reduction; it is a fast rank/closure diagnostic.', '']

lines += ['## 9. Automation boundary', '']
lines += ['This version contains conservative zero-sector detection, sector-aware ranking, bounded seed domains, and a forward sparse Laporta eliminator that can process the full 64-equation first neighborhood. Graph symmetries are now included. Complete iterative closure to a stable symbolic master basis, coefficient reconstruction from generic probes, and master-integral boundary data remain future work.', '']

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print('Tadpole reduction:', red_tad)
print('Ladder IBPs:', len(ladder_eqs))
print('Ladder distinct integrals:', len(all_integrals))
print('Finite Laporta rules:', len(ladder_rules))
print('Finite-system unsolved integrals:', len(unsolved))
print('First-neighbor seeds:', len(neighbor_seeds))
print('First-neighbor IBPs:', len(neighbor_eqs))
print('First-neighbor distinct integrals:', len(neighbor_integrals))
print('Scaleless sector IDs:', zero_ids)
print('Forward sparse rules:', len(forward_rules))
print('Finite-domain unsolved integrals:', len(forward_masters))
print('Degree-2 seeds:', len(degree2_seeds))
print('Degree-2 IBPs:', len(degree2_eqs))
print('Degree-2 distinct integrals:', len(degree2_integrals))

print('Ladder symmetry group order:', len(ladder_symmetries))
print('Degree-2 canonical seeds:', len(degree2_canonical_seeds))
print('Degree-2 canonical integrals:', len(degree2_canonical_integrals))
print('Degree-2 generic-point pivots:', len(degree2_probe_rules))
