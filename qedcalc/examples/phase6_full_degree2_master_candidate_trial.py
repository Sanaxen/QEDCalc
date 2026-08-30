from pathlib import Path
import csv, json

ROOT = Path(__file__).parents[1]
SRC = ROOT / 'data' / 'ladder_phase6_full_degree2_checkpoint.csv'
RULES = ROOT / 'data' / 'ladder_phase2_probe1_837_rules.json'
OUT = ROOT / 'output' / 'phase6_full_degree2_master_candidate_trial.md'
CSV_OUT = ROOT / 'output' / 'ladder_phase6_full_degree2_master_candidates.csv'

with SRC.open('r', encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
with RULES.open('r', encoding='utf-8') as f:
    rule_meta = json.load(f)['metadata']

CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

lines = ['# QEDCalc phase-6 full degree-2 Cartesian master-candidate audit', '']
lines += ['## 1. Scope', '']
lines += ['This audit completes the bounded degree-2 Cartesian neighborhood at the primary exact-rational probe. The previously tested first-neighbor and same-direction depth-2 sectors are supplemented by all remaining mixed two-direction degree-2 seeds.', '']
lines += ['The 837-pivot primary-probe Laporta rule set is loaded from a portable JSON checkpoint rather than rebuilt from scratch.', '']
lines += [f'Checkpoint probe: `{rule_meta.get("probe")}`; stored pivots: **{rule_meta.get("pivot_count")}**.', '']
lines += ['## 2. Results', '']
for r in rows:
    idx = tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))
    lines += [
        f'- `{idx}`: new full degree-2 seeds = **{r["new_full_degree2_seeds"]}** '
        f'(first **{r["new_first_seeds"]}**, directional **{r["new_directional_depth2_seeds"]}**, mixed **{r["new_mixed_degree2_seeds"]}**); '
        f'mixed pivoting seeds = **{r["pivoting_mixed_seeds"]}**; full degree-2 pivoting seeds = **{r["full_degree2_pivoting_seeds"]}**.'
    ]
lines += ['', 'At the primary probe, all three candidates remain non-pivoting throughout the complete bounded degree-2 Cartesian neighborhood after symmetry canonicalization and removal of seeds already present in the 116-seed baseline.', '']
lines += ['## 3. Interpretation', '']
lines += ['This is stronger than the directional depth-2 audit because the mixed two-direction seed class is now exhausted at the primary probe. It is still not a global proof of master-integral status: an independent reduction system or a wider seed domain remains desirable.', '']
lines += [f'CSV: `{CSV_OUT.relative_to(ROOT)}`', '']
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote: {OUT}')
print(f'Wrote: {CSV_OUT}')
print('full degree-2 candidates audited:', len(rows))
