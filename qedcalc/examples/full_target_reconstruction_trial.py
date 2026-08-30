from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex, target_aware_closure, generate_ibp_system,
    canonicalize_ibp_system, prune_zero_sectors, specialize_ibp_system,
    laporta_forward_eliminate, batch_reconstruct_targets, integral_latex,
)
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'full_target_reconstruction_trial.md'
CSV_STATUS = ROOT / 'output' / 'ladder_corrected_target_reconstruction_status.csv'
CSV_COEFF = ROOT / 'output' / 'ladder_corrected_reconstructed_coefficients.csv'

family = ordinary_ladder_ibp_family()
symmetries = ordinary_ladder_integral_symmetries()
D, z, m2 = sp.symbols('D z m2')
table = load_ladder_coefficient_table(ROOT / 'data' / 'ladder_corrected_spin_sum_72_coefficients.csv')
raw_targets = [IntegralIndex(idx.as_tuple()) for idx in table]

closure_probes = (
    {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1},
    {D: sp.Rational(41,11), z: sp.Rational(3,7), m2: 1},
    {D: sp.Rational(29,8), z: sp.Rational(-1,3), m2: 1},
)
closure = target_aware_closure(
    family, raw_targets, closure_probes,
    symmetries=symmetries, vectors=('k','l','p',"p'"), max_rounds=4,
)
masters = closure.stable_candidates
master_set = set(masters)

eqs = generate_ibp_system(family, closure.final_seeds, vectors=('k','l','p',"p'"))
eqs = canonicalize_ibp_system(eqs, symmetries)
eqs = prune_zero_sectors(family, eqs)

pairs = (
    ((7,2),(1,5)), ((18,5),(-1,4)), ((19,5),(1,3)), ((21,5),(3,7)),
    ((23,6),(-2,5)), ((17,5),(2,3)), ((39,10),(1,7)), ((31,8),(-1,2)),
    ((43,11),(4,9)), ((27,7),(3,8)), ((16,5),(-2,7)), ((22,5),(2,5)),
    ((33,8),(5,11)), ((25,7),(-3,8)), ((47,12),(1,4)), ((37,9),(2,7)),
)
points = tuple({D: sp.Rational(*dp), z: sp.Rational(*zp), m2: 1} for dp, zp in pairs)
rule_sets = []
valid_points = []
for point in points:
    try:
        peqs = specialize_ibp_system(eqs, point)
        rules = laporta_forward_eliminate(
            peqs, family=None, prune_scaleless=False, protected=master_set,
        )
    except Exception:
        continue
    rule_sets.append(rules)
    valid_points.append(point)

if len(valid_points) < 8:
    raise RuntimeError('Too few valid exact-rational probe points for batch reconstruction.')
training_count = min(12, len(valid_points) - 3)
result = batch_reconstruct_targets(
    closure.targets, masters, rule_sets, valid_points, (D,z), training_count,
    max_numerator_degree=3, max_denominator_degree=3,
)

CSV_STATUS.parent.mkdir(parents=True, exist_ok=True)
with CSV_STATUS.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['nK','nL','nH','n1','n2','n3','n4','status','residual_count','message'])
    for entry in result.entries:
        w.writerow([*entry.target.powers, entry.status, len(entry.residuals), entry.message])

with CSV_COEFF.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['target','master','coefficient','numerator_degree','denominator_degree','training_count','holdout_count'])
    for entry in result.reconstructed:
        for master, rec in entry.coefficients.items():
            w.writerow([
                entry.target.powers, master.powers, sp.sstr(sp.factor(rec.expression)),
                rec.numerator_degree, rec.denominator_degree,
                rec.training_count, rec.holdout_count,
            ])

lines = ['# QEDCalc full corrected-target reconstruction trial', '']
lines += ['## 1. Purpose', '']
lines += ['This trial applies exact-rational symbolic coefficient reconstruction to every symmetry-canonical target of the corrected ordinary-ladder projector route.', '']
lines += ['A target is reconstructed only if recursive Laporta reduction closes entirely on the six stable candidate integrals at every probe point. Targets leaving any non-candidate residue are explicitly skipped rather than interpolated.', '']
lines += ['## 2. Domain', '']
lines += [f'Corrected raw monomials: **{len(table)}**.', '']
lines += [f'Symmetry-canonical targets: **{len(closure.targets)}**.', '']
lines += [f'Stable candidate basis elements: **{len(masters)}**.', '']
lines += [f'Final closure seeds: **{len(closure.final_seeds)}**.', '']
lines += [f'Symbolic IBP rows: **{len(eqs)}**.', '']
lines += [f'Valid exact-rational sample points: **{len(valid_points)}** = {training_count} training + {len(valid_points)-training_count} holdout.', '']

lines += ['## 3. Candidate basis', '']
for n, master in enumerate(masters, 1):
    lines += [f'$M_{n}$:', '', '$$', integral_latex(master), '$$', '']

lines += ['## 4. Batch result', '']
lines += [f'Candidate-basis targets: **{len(result.master_entries)}**.', '']
lines += [f'Non-master targets reconstructed and holdout-validated: **{len(result.reconstructed)}**.', '']
lines += [f'Targets still containing non-candidate IBP residues: **{len(result.residual)}**.', '']
failed = [e for e in result.entries if e.status == 'failed_reconstruction']
lines += [f'Closed targets whose rational ansatz still failed: **{len(failed)}**.', '']

lines += ['## 5. Reconstructed targets', '']
for entry in result.reconstructed:
    lines += ['Target:', '', '$$', integral_latex(entry.target), '$$', '']
    if not entry.coefficients:
        lines += ['The target reduces identically to zero in the current IBP system.', '']
        continue
    rhs = []
    for master, rec in entry.coefficients.items():
        midx = masters.index(master) + 1
        rhs.append(rf'\left({sp.latex(sp.factor(rec.expression))}\right)M_{{{midx}}}')
    lines += ['$$', integral_latex(entry.target) + '=' + '+'.join(rhs), '$$', '']

lines += ['## 6. Residue diagnostic', '']
lines += ['The residual targets demonstrate that pivot membership is weaker than full basis closure. Their recursive reductions terminate on additional non-candidate integrals, so coefficient reconstruction is intentionally not attempted for them.', '']
for entry in result.residual[:10]:
    lines += ['Target:', '', '$$', integral_latex(entry.target), '$$', '']
    lines += [f'Non-candidate residues in sampled reductions: **{len(entry.residuals)}**.', '']
lines += ['(Only the first ten residue-bearing targets are printed here; the CSV contains the complete status table.)', '']

lines += ['## 7. Interpretation', '']
lines += ['The corrected 40-target set is therefore not yet symbolically closed on the six candidate integrals, even though many targets appear as Laporta pivots. The next required step is residue-aware seed closure: collect the actual terminal non-candidate integrals from recursive target reductions, add only their canonical neighborhoods, and repeat until the target reductions themselves close or the residual set stabilizes.', '']
lines += [f'Status CSV: `{CSV_STATUS.relative_to(ROOT)}`', '']
lines += [f'Reconstructed coefficient CSV: `{CSV_COEFF.relative_to(ROOT)}`', '']

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_STATUS}')
print(f'Wrote: {CSV_COEFF}')
print('masters:', len(result.master_entries))
print('reconstructed:', len(result.reconstructed))
print('residual:', len(result.residual))
print('failed reconstruction:', len(failed))
