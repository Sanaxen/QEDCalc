from pathlib import Path
import csv
import sympy as sp
from qedcalc.operations.ibp import IntegralIndex, read_laporta_rule_checkpoint, diagnose_mixed_degree2_irreducibility
from qedcalc.operations.ladder import ordinary_ladder_ibp_family, ordinary_ladder_integral_symmetries

ROOT=Path(__file__).parents[1]
family=ordinary_ladder_ibp_family(); syms=ordinary_ladder_integral_symmetries()
D,z,m2=sp.symbols('D z m2')
probes=(
 ('probe1',{D:sp.Rational(37,10),z:sp.Rational(2,5),m2:1},ROOT/'data'/'ladder_phase2_probe1_837_rules.json'),
 ('probe2',{D:sp.Rational(41,11),z:sp.Rational(3,7),m2:1},ROOT/'data'/'ladder_phase2_probe2_837_rules.json'),
 ('probe3',{D:sp.Rational(29,8),z:sp.Rational(-1,3),m2:1},ROOT/'data'/'ladder_phase2_probe3_837_rules.json'),
)
# 116-seed baseline.
with (ROOT/'data'/'ladder_phase2_116_seeds.csv').open(newline='',encoding='utf-8') as f:
    r=csv.DictReader(f); existing=[IntegralIndex(tuple(int(row[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))) for row in r]
# Three phase-4/5/6 candidates.
with (ROOT/'data'/'ladder_phase6_full_degree2_checkpoint.csv').open(newline='',encoding='utf-8') as f:
    r=csv.DictReader(f); candidates=[IntegralIndex(tuple(int(row[k]) for k in ('nK','nL','nH','n1','n2','n3','n4'))) for row in r]

rows=[]
for pname,probe,path in probes:
    rules,meta=read_laporta_rule_checkpoint(path)
    assert len(rules)==837
    for cand in candidates:
        d=diagnose_mixed_degree2_irreducibility(family,cand,rules,probe,symmetries=syms,existing_seeds=existing,vectors=('k','l','p',"p'"))
        rows.append((pname,cand,len(d.tested_seeds),len(d.pivoting_seeds),d.max_new_pivots))
        print(pname,cand.powers,'mixed',len(d.tested_seeds),'pivoting',len(d.pivoting_seeds),'maxnew',d.max_new_pivots,flush=True)

out=ROOT/'data'/'ladder_phase7_multprobe_full_degree2_checkpoint.csv'
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['probe','nK','nL','nH','n1','n2','n3','n4','mixed_seeds','pivoting_mixed_seeds','max_new_pivots'])
    for pname,cand,n,p,m in rows: w.writerow([pname,*cand.powers,n,p,m])
print('wrote',out)
