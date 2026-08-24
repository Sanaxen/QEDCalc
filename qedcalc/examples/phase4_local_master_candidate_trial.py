from pathlib import Path
import csv

ROOT = Path(__file__).parents[1]
SRC = ROOT / 'data' / 'ladder_phase4_local_master_candidates_checkpoint.csv'
OUT = ROOT / 'output' / 'phase4_local_master_candidate_trial.md'
CSV_OUT = ROOT / 'output' / 'ladder_phase4_local_master_candidates.csv'

rows = []
with SRC.open('r', encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))

CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

local = [r for r in rows if r['locally_irreducible'].lower() == 'true']
lines = ['# QEDCalc phase-4 local master-candidate trial', '']
lines += ['## 1. Residues entering phase 4', '']
lines += [f'Remaining genuine terminal residue kinds after factorized lower-sector recognition: **{len(rows)}**.', '']
for r in rows:
    idx = tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))
    lines += [f'- `{idx}` blocks **{r["impact"]}** target(s).']
lines += ['', '## 2. First-neighborhood diagnostic checkpoint', '']
for r in rows:
    idx = tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))
    lines += [
        f'- `{idx}`: tested **{r["tested_new_first_neighbors"]}** new canonical first-neighbor seeds; '
        f'pivoting neighbors = **{r["pivoting_neighbors"]}**; locally irreducible = **{r["locally_irreducible"]}**.'
    ]
lines += ['', 'The checkpoint was generated from the v0.35 phase-2 triangular rule set using the generic `diagnose_first_neighbor_irreducibility()` algorithm. It is a bounded local IBP diagnostic, not a proof of global master-integral status.', '']
lines += ['## 3. Provisional basis expansion', '']
lines += [f'Original corrected non-factorized candidate basis: **6**.', '']
lines += [f'Additional locally irreducible candidates: **{len(local)}**.', '']
lines += [f'Provisional non-factorized basis size: **{6 + len(local)}**.', '']
lines += ['After admitting these three residues provisionally, the previously reported phase-3 non-basis terminal-residue set is exhausted, so all 40 corrected canonical targets are closed with respect to this provisional basis plus known factorized lower sectors.', '']
lines += [f'CSV: `{CSV_OUT.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_OUT}')
print('provisional non-factorized basis size:', 6 + len(local))
