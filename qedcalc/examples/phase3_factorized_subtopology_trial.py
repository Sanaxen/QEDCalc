from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex, target_aware_closure, canonicalize_seed_set,
    generate_ibp_system, canonicalize_ibp_system, prune_zero_sectors,
    specialize_ibp_system, laporta_forward_eliminate, residue_impact_profile,
    residue_sector_profile, schedule_residue_sectors,
    extend_laporta_rules_incrementally, factorized_one_denominator_per_loop,
    factorized_euclidean_scalar_value, is_scaleless_zero_sector_extended,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'phase3_factorized_subtopology_trial.md'
CSV_OUT = ROOT / 'output' / 'ladder_phase3_factorized_lower_sectors.csv'

family = ordinary_ladder_ibp_family()
symmetries = ordinary_ladder_integral_symmetries()
D, z, m2 = sp.symbols('D z m2')
probes = (
    {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1},
    {D: sp.Rational(41,11), z: sp.Rational(3,7), m2: 1},
    {D: sp.Rational(29,8), z: sp.Rational(-1,3), m2: 1},
)
probe = probes[0]

table = load_ladder_coefficient_table(ROOT / 'data' / 'ladder_corrected_spin_sum_72_coefficients.csv')
raw_targets = [IntegralIndex(idx.as_tuple()) for idx in table]
closure = target_aware_closure(
    family, raw_targets, probes,
    symmetries=symmetries, vectors=('k','l','p',"p'"), max_rounds=4,
)
masters = set(closure.stable_candidates)


def build_rules(seeds):
    cseeds = canonicalize_seed_set(seeds, symmetries)
    eqs = generate_ibp_system(family, cseeds, vectors=('k','l','p',"p'"))
    eqs = canonicalize_ibp_system(eqs, symmetries)
    eqs = prune_zero_sectors(family, eqs)
    peqs = specialize_ibp_system(eqs, probe)
    rules = laporta_forward_eliminate(
        peqs, family=None, prune_scaleless=False, protected=masters,
    )
    return cseeds, rules


base_seeds, base_rules = build_rules(closure.final_seeds)
base_impacts = residue_impact_profile(
    closure.targets, base_rules, masters,
    symmetries=symmetries, existing_seeds=base_seeds,
)
phase1_direct = schedule_residue_sectors(
    residue_sector_profile(base_impacts), max_new_seeds=64,
)
phase1_seeds, phase1_rules = build_rules(
    set(base_seeds) | set(phase1_direct.new_seeds)
)

# v0.34 greedy phase-2 pair.  Here we perform the actual recursive check.
selected = (
    IntegralIndex((-1,0,0,0,0,1,2)),
    IntegralIndex((-1,0,0,0,1,0,2)),
)
new_eqs = []
for seed in selected:
    eqs = generate_ibp_system(family, (seed,), vectors=('k','l','p',"p'"))
    eqs = canonicalize_ibp_system(eqs, symmetries)
    eqs = prune_zero_sectors(family, eqs)
    new_eqs.extend(specialize_ibp_system(eqs, probe))
phase2_rules = extend_laporta_rules_incrementally(
    phase1_rules, new_eqs, protected=masters,
)
phase2_seeds = canonicalize_seed_set(set(phase1_seeds) | set(selected), symmetries)
phase2_impacts = residue_impact_profile(
    closure.targets, phase2_rules, masters,
    symmetries=symmetries, existing_seeds=phase2_seeds,
)
phase2_blocked = set()
for item in phase2_impacts:
    phase2_blocked.update(item.blocked_targets)

factorized = {}
for item in phase2_impacts:
    fac = factorized_one_denominator_per_loop(family, item.residue)
    if fac is not None:
        factorized[item.residue] = fac

known_lower = masters | set(factorized)
phase3_impacts = residue_impact_profile(
    closure.targets, phase2_rules, known_lower,
    symmetries=symmetries, existing_seeds=phase2_seeds,
)
phase3_blocked = set()
for item in phase3_impacts:
    phase3_blocked.update(item.blocked_targets)

CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['nK','nL','nH','n1','n2','n3','n4','denominators','powers','det','unimodular'])
    for idx, fac in sorted(factorized.items(), key=lambda x: x[0].powers):
        w.writerow([
            *idx.powers,
            ';'.join(fac.denominator_names),
            ';'.join(map(str, fac.powers)),
            str(fac.direction_determinant),
            fac.unimodular,
        ])

lines = ['# QEDCalc phase-3 factorized lower-subtopology trial', '']
lines += ['## 1. Recursive check of the v0.34 phase-2 pair', '']
lines += [f'Phase-1 pivots: **{len(phase1_rules)}**.', '']
lines += [f'After inserting the two selected phase-2 seeds: **{len(phase2_rules)}** pivots.', '']
lines += [f'Residue-bearing corrected targets after actual recursive reduction: **{len(phase2_blocked)}**.', '']
lines += ['The direct-pivot scheduling metric did not by itself close these targets; the high-power residues descended to simpler lower-sector integrals.', '']
lines += ['## 2. Factorized lower sectors', '']
lines += [f'Factorized terminal residues recognized: **{len(factorized)}**.', '']
for idx, fac in sorted(factorized.items(), key=lambda x: x[0].powers):
    val = factorized_euclidean_scalar_value(fac, dimension=D, delta=m2)
    lines += [f'- `{idx.powers}` -> denominators `{fac.denominator_names}`, powers `{fac.powers}`, loop-direction determinant `{fac.direction_determinant}`, unimodular = **{fac.unimodular}**.']
    lines += [f'  Convention-free Euclidean product: `${sp.latex(val)}$`.']
lines += ['']
lines += ['These are not promoted to new genuine two-loop masters. They are known lower-subtopology products of one-loop massive tadpoles after an invertible loop-momentum change of variables.', '']
lines += ['## 3. Closure after recognizing the lower sectors', '']
lines += [f'Residue-bearing corrected targets: **{len(phase2_blocked)} -> {len(phase3_blocked)}**.', '']
lines += [f'Remaining terminal residue kinds: **{len(phase3_impacts)}**.', '']
for item in phase3_impacts:
    lines += [f'- `{item.residue.powers}` blocks **{item.impact}** target(s).']
lines += ['']
lines += ['## 4. Extended zero-sector diagnostic', '']
free_example = IntegralIndex((0,0,0,0,0,0,2))
lines += [f'`{free_example.powers}` is classified as zero by the extended diagnostic because one of the two loop directions is completely unconstrained by positive denominators: **{is_scaleless_zero_sector_extended(family, free_example)}**.', '']
lines += [f'CSV: `{CSV_OUT.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_OUT}')
print('phase-2 blocked targets:', len(phase2_blocked))
print('factorized lower residues:', [x.powers for x in factorized])
print('phase-3 blocked targets:', len(phase3_blocked))
print('remaining residue kinds:', [(x.residue.powers, x.impact) for x in phase3_impacts])
