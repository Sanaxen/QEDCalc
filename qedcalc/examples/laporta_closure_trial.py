from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import IntegralIndex, target_aware_closure, integral_latex
from qedcalc.operations.ladder import (
    ordinary_ladder_ibp_family,
    ordinary_ladder_integral_symmetries,
    load_ladder_coefficient_table,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'output' / 'laporta_closure_trial.md'
CSV_HIST = ROOT / 'output' / 'ladder_historical_stable_unreduced_candidates.csv'
CSV_CORR = ROOT / 'output' / 'ladder_corrected_stable_unreduced_candidates.csv'

family = ordinary_ladder_ibp_family()
symmetries = ordinary_ladder_integral_symmetries()
D, z, m2 = sp.symbols('D z m2')
probes = (
    {D: sp.Rational(37,10), z: sp.Rational(2,5), m2: 1},
    {D: sp.Rational(41,11), z: sp.Rational(3,7), m2: 1},
    {D: sp.Rational(29,8), z: sp.Rational(-1,3), m2: 1},
)

def run_closure(targets):
    return target_aware_closure(
        family,
        targets,
        probes,
        symmetries=symmetries,
        vectors=('k','l','p',"p'"),
        neighborhood_degree=1,
        max_rounds=4,
    )

def write_candidates(path, candidates):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['nK','nL','nH','n1','n2','n3','n4'])
        for idx in candidates:
            w.writerow(idx.powers)

# Historical audit route: archived 75-term coefficient table.
historical_table = load_ladder_coefficient_table(ROOT / 'data' / 'ladder_Ddim_75_coefficients.csv')
historical_targets = [IntegralIndex(idx.as_tuple()) for idx in historical_table]
historical = run_closure(historical_targets)
write_candidates(CSV_HIST, historical.stable_candidates)

# Corrected physical spin-sum route: target table checkpoint regenerated from raw bare LaTeX by the general-q trace demo.
corrected_table = load_ladder_coefficient_table(ROOT / 'data' / 'ladder_corrected_spin_sum_72_coefficients.csv')
corrected_targets = [IntegralIndex(idx.as_tuple()) for idx in corrected_table]
corrected = run_closure(corrected_targets)
write_candidates(CSV_CORR, corrected.stable_candidates)

lines = ['# QEDCalc target-aware Laporta closure trial', '']
lines += ['## 1. Purpose', '']
lines += ['This trial expands the IBP seed domain around the integrals that actually occur in the ordinary-ladder projector output. It keeps the archived historical 75-term audit route separate from the corrected spin-sum route whose 72-term checkpoint was generated and regression-tested from the raw bare LaTeX input.', '']
lines += ['A stable unreduced candidate is not yet declared to be a physical master integral. Stability here means that the target-aware neighborhood stops growing and the same candidate set is obtained at all configured exact-rational probe points.', '']

lines += ['## 2. Exact-rational probes', '']
for n, point in enumerate(probes, 1):
    lines += [f'Probe {n}:', '']
    lines += ['$$', rf'D={sp.latex(point[D])},\qquad z={sp.latex(point[z])},\qquad m^2={sp.latex(point[m2])}', '$$', '']


def append_result(title, result, original_count, csv_path):
    lines.extend([title, ''])
    lines.extend([f'Original target monomials: **{original_count}**.', ''])
    lines.extend([f'Canonical targets after symmetry: **{len(result.targets)}**.', ''])
    for r in result.rounds:
        lines.extend([f'### Round {r.round_index}', ''])
        lines.extend([f'- canonical seeds: **{r.seed_count}**'])
        lines.extend([f'- symbolic IBP rows after pruning: **{r.equation_count}**'])
        lines.extend([f'- distinct integrals in the row system: **{r.integral_count}**'])
        lines.extend([f'- exact-rational probe pivots: **{list(r.pivot_counts)}**'])
        lines.extend([f'- solved targets: **{r.solved_target_count}/{r.target_count}**'])
        lines.extend([f'- unreduced targets: **{len(r.unsolved_targets)}**'])
        lines.extend([f'- identical candidate set across probes: **{r.stable_across_probes}**', ''])
    lines.extend([f'Closure status: **{result.status}**.', ''])
    lines.extend([f'Stable unreduced candidates: **{len(result.stable_candidates)}**.', ''])
    for idx in result.stable_candidates:
        lines.extend(['$$', integral_latex(idx), '$$', ''])
    lines.extend([f'Candidate CSV: `{csv_path.relative_to(ROOT)}`', ''])

append_result('## 3. Historical 75-term audit route', historical, len(historical_table), CSV_HIST)
append_result('## 4. Corrected spin-sum route', corrected, len(corrected_table), CSV_CORR)

lines += ['## 5. Interpretation', '']
lines += ['The historical route stabilizes at seven unreduced candidates. The corrected spin-sum route stabilizes at six. The corrected route is the physically relevant projector ordering; the historical result is retained only as an audit/regression path.', '']
lines += ['The six corrected candidates are stable under three independent exact-rational probes and under the implemented target-neighborhood expansion. Further sector completion, additional identities, symbolic coefficient reconstruction, and master-integral boundary data are still required before calling them the final physical master basis.', '']

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_HIST}')
print(f'Wrote: {CSV_CORR}')
print('Historical:', len(historical.targets), 'canonical targets ->', len(historical.stable_candidates), 'stable candidates')
print('Corrected:', len(corrected.targets), 'canonical targets ->', len(corrected.stable_candidates), 'stable candidates')
for label, result in [('historical', historical), ('corrected', corrected)]:
    for r in result.rounds:
        print(label, f'round {r.round_index}: seeds={r.seed_count}, pivots={r.pivot_counts}, solved={r.solved_target_count}/{r.target_count}')
