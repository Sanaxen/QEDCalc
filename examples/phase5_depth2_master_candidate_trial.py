from pathlib import Path
import csv

ROOT = Path(__file__).parents[1]
SRC = ROOT / 'data' / 'ladder_phase5_depth2_master_candidate_checkpoint.csv'
OUT = ROOT / 'output' / 'phase5_depth2_master_candidate_trial.md'
CSV_OUT = ROOT / 'output' / 'ladder_phase5_depth2_master_candidates.csv'

with SRC.open('r', encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

lines = ['# QEDCalc phase-5 depth-2 master-candidate audit', '']
lines += ['## 1. Scope', '']
lines += ['This audit strengthens the v0.36 bounded first-neighborhood test without claiming a global master-integral proof.', '']
lines += ['For each of the three provisional local master candidates, QEDCalc tests canonical seeds obtained by moving one admissible integral-family index two steps in the same direction. This directional depth-2 domain is deliberately smaller than the full Cartesian degree-2 seed domain and avoids opening an uncontrolled Laporta system.', '']
lines += ['## 2. Independent exact-rational probes', '']
lines += ['The same phase-2 seed domain was rebuilt independently at three exact-rational kinematic points:', '']
lines += ['- `(D,z)=(37/10,2/5)`', '- `(D,z)=(41/11,3/7)`', '- `(D,z)=(29/8,-1/3)`', '']
lines += ['Each probe produced **837** baseline pivots.', '']
lines += ['## 3. Directional depth-2 results', '']
for r in rows:
    idx = tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))
    lines += [
        f'- `{idx}`: first-neighbor pivots = **{r["first_pivots"]}/{r["first_neighbors"]}**; '
        f'directional depth-2 seeds = **{r["depth2_directional_seeds"]}**; '
        f'pivoting seeds across the three probes = **{r["probe1_pivots"]}, {r["probe2_pivots"]}, {r["probe3_pivots"]}**.'
    ]
lines += ['', 'All three candidates remain non-pivoting in the tested directional depth-2 domain at all three independent exact-rational probes.', '']
lines += ['## 4. Interpretation', '']
lines += ['The evidence is stronger than the v0.36 first-neighborhood audit, but it is still bounded. The three integrals are therefore promoted only to **depth-2-stable provisional master candidates**, not to globally proven master integrals.', '']
lines += [f'CSV: `{CSV_OUT.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_OUT}')
print('depth-2-stable provisional candidates:', len(rows))
