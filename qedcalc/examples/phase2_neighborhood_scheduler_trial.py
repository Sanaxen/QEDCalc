from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex, target_aware_closure, canonicalize_seed_set,
    generate_ibp_system, canonicalize_ibp_system, prune_zero_sectors,
    specialize_ibp_system, laporta_forward_eliminate, residue_impact_profile,
    residue_sector_profile, schedule_residue_sectors, bounded_seed_domain,
    canonicalize_integral, evaluate_neighborhood_seed_candidates,
    schedule_neighborhood_seeds,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'phase2_neighborhood_scheduler_trial.md'
CSV_OUT = ROOT / 'output' / 'ladder_phase2_neighborhood_seed_ranking.csv'

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
phase1_seeds, phase1_rules = build_rules(set(base_seeds) | set(phase1_direct.new_seeds))
phase1_impacts = residue_impact_profile(
    closure.targets, phase1_rules, masters,
    symmetries=symmetries, existing_seeds=phase1_seeds,
)
phase1_sectors = residue_sector_profile(phase1_impacts)

# Phase 2: only the two highest-impact sectors whose degree-1 neighborhoods
# remain modest.  The candidates are evaluated incrementally, one seed at a time.
candidates = set()
for sid in (96, 80):
    sector = next(item for item in phase1_sectors if item.sector == sid)
    for residue in sector.residues:
        candidates.update(bounded_seed_domain(residue, 1))
candidates = {
    canonicalize_integral(seed, symmetries) for seed in candidates
} - set(phase1_seeds)

ranking = evaluate_neighborhood_seed_candidates(
    family, candidates, phase1_rules, phase1_impacts, probe,
    symmetries=symmetries, protected=masters,
    vectors=('k','l','p',"p'"),
)
batch = schedule_neighborhood_seeds(ranking, max_new_seeds=3)

CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['nK','nL','nH','n1','n2','n3','n4','direct_impact','new_pivots','hit_residues'])
    for item in ranking:
        w.writerow([
            *item.seed.powers, item.direct_impact, item.new_pivot_count,
            ';'.join(str(r.powers) for r in item.hit_residues),
        ])

lines = ['# QEDCalc phase-2 neighborhood scheduler trial', '']
lines += ['## 1. Phase-1 baseline', '']
lines += [f'Phase-1 seeds: **{len(phase1_seeds)}**.', '']
lines += [f'Phase-1 pivots: **{len(phase1_rules)}**.', '']
lines += [f'Terminal residue kinds: **{len(phase1_impacts)}**.', '']
lines += ['## 2. Incremental extension', '']
lines += ['New candidate seeds are not evaluated by rebuilding the full 906-row system. Each candidate contributes only its own IBP rows, which are reduced through the existing 823 phase-1 pivots before new pivots are selected.', '']
lines += ['## 3. Candidate pool', '']
lines += [f'Candidate neighborhood seeds from sectors 96 and 80: **{len(candidates)}**.', '']
positive = [x for x in ranking if x.direct_impact > 0]
lines += [f'Candidates that directly pivot at least one known terminal residue: **{len(positive)}**.', '']
for item in ranking[:10]:
    lines += [f'- `{item.seed.powers}`: direct blocked-target impact = **{item.direct_impact}**, new pivots = **{item.new_pivot_count}**, terminal residues hit = **{len(item.hit_residues)}**']
lines += ['']
lines += ['## 4. Greedy phase-2 batch', '']
lines += [f'Selected seeds: **{len(batch.selected)}**.', '']
lines += [f'Union of targets blocked by directly hit residues: **{len(batch.covered_targets)}**.', '']
for item in batch.selected:
    lines += [f'- `{item.seed.powers}`: direct impact = **{item.direct_impact}**, hit residues = `{[r.powers for r in item.hit_residues]}`']
lines += ['']
lines += ['The covered-target count is a scheduling metric, not a claim that those targets are already fully reduced. Full recursive target reduction is deferred until the small batch has been accepted.', '']
lines += [f'Ranking CSV: `{CSV_OUT.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_OUT}')
print('phase-1 seeds / pivots:', len(phase1_seeds), len(phase1_rules))
print('candidate seeds:', len(candidates))
print('positive direct-impact seeds:', len(positive))
print('selected seeds:', [x.seed.powers for x in batch.selected])
print('directly covered blocked-target union:', len(batch.covered_targets))
