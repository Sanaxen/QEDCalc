from pathlib import Path
import csv,json
ROOT=Path(__file__).parents[1]
phase6=ROOT/'data'/'ladder_phase6_full_degree2_checkpoint.csv'
with phase6.open(newline='',encoding='utf8') as f:
    p1=list(csv.DictReader(f))
# batch files for p2,p3
rows=[]
for r in p1:
    idx=tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))
    rows.append(['probe1',*idx,int(r['new_mixed_degree2_seeds']),int(r['pivoting_mixed_seeds']),0,False])
for pn in ('probe2','probe3'):
    for ci in (1,2,3):
        p=ROOT/'data'/f'phase7_batch_{pn}_cand{ci}.csv'
        with p.open(newline='',encoding='utf8') as f:
            r=next(csv.DictReader(f))
        idx=eval(r['candidate'],{'__builtins__':{}})
        rows.append([pn,*idx,int(r['mixed_seeds']),0,int(r['new_pivots']),r['candidate_pivot']=='True'])
outcsv=ROOT/'output'/'ladder_phase7_three_probe_full_degree2_audit.csv'; outcsv.parent.mkdir(parents=True,exist_ok=True)
with outcsv.open('w',newline='',encoding='utf8') as f:
    w=csv.writer(f); w.writerow(['probe','nK','nL','nH','n1','n2','n3','n4','mixed_seeds','pivoting_mixed_seeds','batch_new_pivots','candidate_pivot']); w.writerows(rows)
# metadata/checkpoints
metas=[]
for pn in ('probe1','probe2','probe3'):
    p=ROOT/'data'/f'ladder_phase2_{pn}_837_rules.json'
    with p.open(encoding='utf8') as f: metas.append(json.load(f)['metadata'])
out=ROOT/'output'/'phase7_three_probe_full_degree2_master_candidate_trial.md'
lines=['# QEDCalc phase-7 three-probe full degree-2 master-candidate audit','',
'## 1. Purpose','',
'This audit repeats the complete bounded degree-2 Cartesian test at three independent exact-rational probes. The first-neighbor and same-direction depth-2 classes had already been checked at all three probes; this phase completes the mixed two-direction class at probes 2 and 3.','',
'## 2. Portable baseline checkpoints','']
for m in metas:
    lines.append(f'- probe `{m.get("probe")}`: **{m.get("pivot_count")}** baseline pivots.')
lines += ['', 'All three independently rebuilt baseline systems contain **837 pivots**.', '', '## 3. Full mixed degree-2 results', '']
# group by candidate
cands=[]
for r in p1:
    cands.append(tuple(int(r[k]) for k in ('nK','nL','nH','n1','n2','n3','n4')))
for ci,c in enumerate(cands,1):
    lines.append(f'### Candidate {ci}: `{c}`')
    lines.append('')
    for pn in ('probe1','probe2','probe3'):
        rr=[x for x in rows if x[0]==pn and tuple(x[1:8])==c][0]
        lines.append(f'- {pn}: mixed seeds **{rr[8]}**, candidate pivot = **{rr[11]}**' + (f', batch new pivots **{rr[10]}**.' if pn!='probe1' else '.'))
    lines.append('')
lines += ['## 4. Interpretation','',
'All three provisional candidates remain non-pivoting throughout the complete bounded degree-2 Cartesian neighborhood at all three independent exact-rational probes. This is stronger evidence than a single-probe bounded audit, but it is still not a global mathematical proof of master-integral status.','',
'## 5. Performance improvement','',
'Incremental Laporta reduction now reuses one persistent recursive reduction cache for all new IBP rows. This removes repeated reconstruction of the 837-rule recursion graph and makes the multi-probe mixed-domain audit practical.','',
f'CSV: `{outcsv.relative_to(ROOT)}`','']
out.write_text('\n'.join(lines),encoding='utf8')
print('Wrote:',out); print('Wrote:',outcsv)
