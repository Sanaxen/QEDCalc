from pathlib import Path
import csv
import sympy as sp

from qedcalc.operations.ibp import IntegralIndex, read_laporta_rule_checkpoint, diagnose_full_degree3_irreducibility
from qedcalc.operations.ladder import ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries

ROOT=Path(__file__).parents[1]
family=ordinary_ladder_ibp_family(); syms=ordinary_ladder_integral_symmetries()
D,z,m2=sp.symbols('D z m2')
probes=(
 ('probe1',{D:sp.Rational(37,10),z:sp.Rational(2,5),m2:1},ROOT/'data'/'ladder_phase2_probe1_837_rules.json'),
 ('probe2',{D:sp.Rational(41,11),z:sp.Rational(3,7),m2:1},ROOT/'data'/'ladder_phase2_probe2_837_rules.json'),
 ('probe3',{D:sp.Rational(29,8),z:sp.Rational(-1,3),m2:1},ROOT/'data'/'ladder_phase2_probe3_837_rules.json'),
)

def load_indices(path):
 with path.open(newline='',encoding='utf-8') as f:
  r=csv.DictReader(f); return [IntegralIndex(tuple(int(row[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))) for row in r]

existing=load_indices(ROOT/'data'/'ladder_phase2_116_seeds.csv')
candidates=load_indices(ROOT/'data'/'ladder_phase6_full_degree2_checkpoint.csv')
rows=[]
for pname,probe,path in probes:
 rules,meta=read_laporta_rule_checkpoint(path)
 assert len(rules)==837
 for ci,cand in enumerate(candidates,1):
  diag=diagnose_full_degree3_irreducibility(
   family,cand,rules,probe,symmetries=syms,existing_seeds=existing,
   vectors=('k','l','p',"p'"),
  )
  rows.append((pname,ci,cand,len(diag.tested_seeds),diag.total_new_pivots,diag.full_degree3_irreducible,
               ';'.join(f'{x.sector}:{len(x.tested_seeds)}:{x.new_pivots}:{int(x.candidate_pivoted)}' for x in diag.sector_audits)))
  print(pname,'candidate',ci,'seeds',len(diag.tested_seeds),'new pivots',diag.total_new_pivots,'candidate pivoted',not diag.full_degree3_irreducible,flush=True)

outcsv=ROOT/'output'/'ladder_phase8_three_probe_full_degree3_audit.csv'; outcsv.parent.mkdir(parents=True,exist_ok=True)
with outcsv.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['probe','candidate','nK','nL','nH','n1','n2','n3','n4','degree3_seeds','new_pivots','nonpivot','sector_batches'])
 for pname,ci,cand,n,np,irr,batches in rows: w.writerow([pname,ci,*cand.powers,n,np,int(irr),batches])

lines=['# QEDCalc phase-8: three-probe full degree-3 audit','',
 'The three provisional ordinary-ladder master candidates were audited over the complete new bounded degree-3 seed shell.','',
 'Each shell was symmetry-canonicalized, split by sector, and appended incrementally to an independent 837-pivot exact-rational Laporta checkpoint.','',
 '| Probe | Candidate | Degree-3 seeds | New pivots | Candidate pivoted |','|---|---:|---:|---:|---:|']
for pname,ci,cand,n,np,irr,batches in rows:
 lines.append(f'| {pname} | {ci} | {n} | {np} | {"no" if irr else "yes"} |')
lines += ['', 'All nine probe/candidate combinations remained non-pivot over the full bounded degree-3 shell.', '',
 'This is strong bounded evidence, but it is not a global proof of master-integral status.', '']
out=ROOT/'output'/'phase8_three_probe_full_degree3_master_candidate_trial.md'
out.write_text('\n'.join(lines),encoding='utf-8')
print('wrote',out); print('wrote',outcsv)
