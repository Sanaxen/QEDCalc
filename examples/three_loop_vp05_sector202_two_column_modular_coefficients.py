"""Extract VP05 sector202 two-free-column modular reduction coefficients.

Read-only selected 2678 L2 Kira SYSTEM equations. All coefficients here are
finite-field evaluations and are NOT exact rational functions. Preserve small
Kira ID4 as a formal column; its mapping to a physical master is documented
independently and remains conditioned on the Kira build semantics.
"""
from __future__ import annotations
import argparse,json
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS

def residual(vec,pivots,p):
 cur={k:v%p for k,v in vec.items() if v%p}
 out={}
 while cur:
  lead=min(cur)
  if lead not in pivots:
   out[lead]=cur.pop(lead)
   continue
  q=cur[lead];base=pivots[lead]
  for k,v in base.items():
   t=(cur.get(k,0)-q*v)%p
   if t:cur[k]=t
   else:cur.pop(k,None)
 return out

def mod_coeff(target,c,m,pivots,p):
 rt=residual({target:1},pivots,p)
 rc=residual({c:1},pivots,p)
 rm=residual({m:1},pivots,p)
 col=sorted(set(rt)|set(rc)|set(rm))
 for i,ki in enumerate(col):
  for kj in col[i+1:]:
   a,b=rc.get(ki,0),rm.get(ki,0)
   d,e=rc.get(kj,0),rm.get(kj,0)
   det=(a*e-b*d)%p
   if not det:continue
   u=(rt.get(ki,0)*e-b*rt.get(kj,0))*pow(det,-1,p)%p
   v=(a*rt.get(kj,0)-rt.get(ki,0)*d)*pow(det,-1,p)%p
   check=residual({target:1,c:-u,m:-v},pivots,p)
   if check:return {"status":"RESIDUAL_NONZERO","residual_terms":len(check)}
   return {"status":"MODULAR_RELATION_VERIFIED","coefficient_C_mod_p":u,
     "coefficient_small4_mod_p":v,"independent_remainder_pivots":[list(ki),list(kj)],
     "remainder_terms":{"target":len(rt),"C":len(rc),"small4":len(rm)}}
 return {"status":"TWO_FREE_REMAINDERS_RANK_LT_2",
   "remainder_terms":{"target":len(rt),"C":len(rc),"small4":len(rm)}}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-fill",type=int,default=20000)
 ap.add_argument("--points",type=int,choices=(1,2,3),default=3)
 args=ap.parse_args()
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=m.from_kiradb(str(P/"results/kira.db"))
 if ordering!=5:raise RuntimeError("expected Kira ordering 5")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 keys=[(codec.encode(x),139) for x in TARGETS]
 if any(tuple(codec.decode(k[0]))!=x for k,x in zip(keys,TARGETS)):
  raise RuntimeError("target physical ID roundtrip failed")
 small4=(4,73)
 files=sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 points=[(1000003,17,7),(1000033,19,11),(1000037,23,13)][:args.points]
 outputs=[]
 for prime,z,d in points:
  pivots={};cols=set();n=0;error=None
  try:
   for file in files:
    for row in equations(file,prime,z,d):
     cols.update(row);insert(row,pivots,prime,args.max_fill);n+=1
   if n!=2678:raise RuntimeError("source equation count changed")
   if any(k not in cols for k in keys+[small4]):raise RuntimeError("target/small4 not present in source")
   relation=[mod_coeff(t,keys[2],small4,pivots,prime) for t in keys[:2]]
   outputs.append({"prime":prime,"z":z,"d":d,"equations":n,"rank":len(pivots),
     "relations":relation,"all_verified_at_point":all(r["status"]=="MODULAR_RELATION_VERIFIED" for r in relation)})
  except Exception as ex:
   outputs.append({"prime":prime,"z":z,"d":d,"equations":n,
     "error":type(ex).__name__+": "+str(ex)[:250],"all_verified_at_point":False})
 print("VP05_SECTOR202_TWO_COLUMN_MODULAR_COEFFICIENTS "+json.dumps({
  "status":"VP05_SECTOR202_TWO_COLUMN_MODULAR_COEFFICIENTS",
  "source_project":str(P),"target_exponents":[list(x) for x in TARGETS],
  "formal_free_columns":[list(keys[2]),list(small4)],
  "points":outputs,"all_points_verified":all(x["all_verified_at_point"] for x in outputs),
  "exact_rational_function_coefficients_proven":False,
  "scope":"Modular coefficients only, obtained by exact finite-field rowspace reduction. No symbolic interpolation/proof, no 63-master closure proof.",
  "kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
