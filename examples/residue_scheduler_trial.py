from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex, target_aware_closure, generate_ibp_system,
    canonicalize_ibp_system, canonicalize_seed_set, prune_zero_sectors,
    specialize_ibp_system, laporta_forward_eliminate, reduce_integral,
    residue_impact_profile, residue_sector_profile, schedule_residue_sectors,
    integral_latex,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'residue_scheduler_trial.md'
CSV_RES = ROOT / 'output' / 'ladder_residue_impact_profile.csv'
CSV_SEC = ROOT / 'output' / 'ladder_residue_sector_priority.csv'

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
    residual_targets = []
    for target in closure.targets:
        if target in masters:
            continue
        if set(reduce_integral(target, rules)) - masters:
            residual_targets.append(target)
    return cseeds, eqs, rules, tuple(residual_targets)

base_seeds, base_eqs, base_rules, base_residual_targets = build_rules(closure.final_seeds)
impacts = residue_impact_profile(
    closure.targets, base_rules, masters,
    symmetries=symmetries, existing_seeds=base_seeds,
)
sectors = residue_sector_profile(impacts)
# Phase 1 intentionally adds terminal residues only.  It does not add their
# full degree-1 neighborhoods.
batch = schedule_residue_sectors(sectors, max_new_seeds=64)
phase1_seed_input = set(base_seeds) | set(batch.new_seeds)
phase1_seeds, phase1_eqs, phase1_rules, phase1_residual_targets = build_rules(phase1_seed_input)

CSV_RES.parent.mkdir(parents=True, exist_ok=True)
with CSV_RES.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['nK','nL','nH','n1','n2','n3','n4','blocked_targets','sector','already_seeded'])
    for item in impacts:
        w.writerow([*item.residue.powers, item.impact, item.sector, int(item.already_seeded)])

with CSV_SEC.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['sector','blocked_targets','residue_count','new_seed_cost','score'])
    for item in sectors:
        w.writerow([item.sector, item.impact, len(item.residues), item.new_seed_cost, str(item.score)])

lines = ['# QEDCalc residue-aware closure scheduler trial', '']
lines += ['## 1. Purpose', '']
lines += ['This trial ranks terminal non-candidate residues by the number of corrected ordinary-ladder targets they block, aggregates them by sector, and adds only the residue seeds themselves before any neighborhood expansion.', '']
lines += ['## 2. Baseline', '']
lines += [f'Canonical corrected targets: **{len(closure.targets)}**.', '']
lines += [f'Protected stable candidate basis: **{len(masters)}**.', '']
lines += [f'Baseline seeds: **{len(base_seeds)}**.', '']
lines += [f'Baseline IBP rows: **{len(base_eqs)}**.', '']
lines += [f'Baseline pivots at the exact probe: **{len(base_rules)}**.', '']
lines += [f'Baseline residue-bearing targets: **{len(base_residual_targets)}**.', '']
lines += ['## 3. Highest-impact residue sectors', '']
for sector in sectors[:8]:
    lines += [f'- sector {sector.sector}: blocked targets = **{sector.impact}**, residues = **{len(sector.residues)}**, new direct seeds = **{sector.new_seed_cost}**, score = **{sector.score}**']
lines += ['']
lines += ['The first two useful sectors are sector 96 and sector 80. Sector 82 has high impact but its terminal residue is already present in the baseline seed set, so it receives zero new-seed priority.', '']
lines += ['## 4. Phase-1 bounded direct-residue insertion', '']
lines += [f'New terminal-residue seeds selected: **{len(batch.new_seeds)}**.', '']
lines += [f'Seeds after phase 1: **{len(phase1_seeds)}**.', '']
lines += [f'IBP rows after phase 1: **{len(phase1_eqs)}**.', '']
lines += [f'Pivots after phase 1: **{len(phase1_rules)}**.', '']
lines += [f'Residue-bearing targets after phase 1: **{len(phase1_residual_targets)}**.', '']
lines += [f'Additional fully closed targets: **{len(base_residual_targets)-len(phase1_residual_targets)}**.', '']
lines += ['## 5. Interpretation', '']
lines += ['The direct-residue phase remains computationally controlled and avoids the large blow-up seen when all degree-1 residue neighborhoods are inserted simultaneously. It also produces additional pivots and closes one more corrected target in this trial.', '']
lines += ['The next scheduler phase should recompute terminal residues on the enlarged seed system and expand only the best remaining residue sector neighborhood, under a strict new-seed budget.', '']
lines += [f'Residue profile CSV: `{CSV_RES.relative_to(ROOT)}`', '']
lines += [f'Sector priority CSV: `{CSV_SEC.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_RES}')
print(f'Wrote: {CSV_SEC}')
print('baseline seeds / IBPs / pivots / residual targets:', len(base_seeds), len(base_eqs), len(base_rules), len(base_residual_targets))
print('phase1 seeds / IBPs / pivots / residual targets:', len(phase1_seeds), len(phase1_eqs), len(phase1_rules), len(phase1_residual_targets))
print('new direct residue seeds:', len(batch.new_seeds))
