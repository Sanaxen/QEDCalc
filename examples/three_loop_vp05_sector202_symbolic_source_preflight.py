"""Identify saved original IBP rows sufficient for sector202 candidate proof.

At a modular point, replay A-a*C-b*small4 against an explicitly tracked
sparse elimination DAG. The extracted rows are an exact-source *candidate*
only: independently verify with exact symbolic arithmetic before proof.
No Kira run and no writes to original saved system.
"""
from __future__ import annotations
import argparse,gzip,json
from pathlib import Path
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS
from examples.three_loop_vp05_sector202_bivariate_candidate_verify import functions

def load_rows(p,z,d):
 rows=[]
 for f in sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(f,"rt",encoding="utf-8") as source:
   ordinal=0
   while marker:=source.readline():
    if marker.strip()!="Eq":raise RuntimeError("malformed SYSTEM source")
    equation_id=source.readline().strip();n=int(source.readline());ordinal+=1
    row={}
    for _ in range(n):
     fields=source.readline().split()
     key=(int(fields[2]),int(fields[3]))
     val=coefficient(fields[1],z,d,p)
     row[key]=(row.get(key,0)+val)%p
     if not row[key]:del row[key]
    rows.append((row,{"file":f.name,"ordinal":ordinal,"equation_id":equation_id}))
 return rows

def eliminate(cur,pivots,p,cap):
 deps=[]
 while cur:
  lead=min(cur)
  if lead not in pivots:break
  base,owner=pivots[lead];fac=cur[lead]
  deps.append(owner)
  for k,v in base.items():
   updated=(cur.get(k,0)-fac*v)%p
   if updated:cur[k]=updated
   else:cur.pop(k,None)
  if len(cur)>cap:raise RuntimeError("fill cap exceeded")
 return deps

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--prime",type=int,default=1000003)
 ap.add_argument("--z",type=int,default=17)
 ap.add_argument("--d",type=int,default=7)
 ap.add_argument("--max-fill",type=int,default=20000)
 ap.add_argument("--selection-output",type=Path,help="Optional JSON file recording exact original-row IDs per target (modular candidate, not proof)")
 args=ap.parse_args()
 p,z,d=args.prime,args.z,args.d
 codec_mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=codec_mod.from_kiradb(str(P/"results/kira.db"))
 if ordering!=5:raise RuntimeError("unexpected codec ordering")
 codec=codec_mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 keys=[(codec.encode(v),139) for v in TARGETS]
 if any(tuple(codec.decode(x[0]))!=v for x,v in zip(keys,TARGETS)):
  raise RuntimeError("target codec roundtrip failure")
 original=load_rows(p,z,d)
 if len(original)!=2678:raise RuntimeError("unexpected equation count")
 pivots={};dependency={};normalized_rows={};accepted=0
 for index,(row,meta) in enumerate(original):
  cur=row.copy()
  deps=eliminate(cur,pivots,p,args.max_fill)
  if not cur:continue
  lead=min(cur);inv=pow(cur[lead],-1,p)
  normalized={k:v*inv%p for k,v in cur.items()}
  pivots[lead]=(normalized,index)
  dependency[index]=deps
  normalized_rows[index]=lead
  accepted+=1
 selected=set();tests=[];values=functions(z,d);target_sources=[]
 for i,target in enumerate(keys[:2]):
  a,b=values[i*2:i*2+2]
  if a.denominator%p==0 or b.denominator%p==0:raise ValueError("singular candidate")
  av=a.numerator%p*pow(a.denominator%p,-1,p)%p
  bv=b.numerator%p*pow(b.denominator%p,-1,p)%p
  cur={target:1,keys[2]:(-av)%p,(4,73):(-bv)%p}
  owners=eliminate(cur,pivots,p,args.max_fill)
  queue=list(owners);needed=set()
  while queue:
   node=queue.pop()
   if node in needed:continue
   needed.add(node);queue.extend(dependency[node])
  selected.update(needed)
  target_sources.append({"target_index":i,"target":list(TARGETS[i]),"global_zero_based_ids":sorted(needed),"count":len(needed)})
  tests.append({"target":list(TARGETS[i]),"modular_coeff_C":av,
    "modular_coeff_small4":bv,"remainder_terms":len(cur),
    "direct_pivot_dependencies":len(owners),
    "transitive_original_rows":len(needed),"verified":not cur})
 out={"status":"VP05_SECTOR202_SYMBOLIC_SOURCE_PROOF_PREFLIGHT",
  "point":[p,z,d],"saved_equations":len(original),"rank":accepted,
  "target_tests":tests,"union_source_rows":len(selected),
  "selected_rows":[{"global_zero_based":j,**original[j][1]} for j in sorted(selected)],
  "symbolic_exact_replay_proven":False,
  "description":"Modular elimination dependency DAG. Selected original rows are a candidate sufficient source for exact symbolic certificate. No exact symbolic replay performed.",
  "kira_executed":False,"files_modified":False}
 if args.selection_output:
  if not all(t["verified"] for t in tests):raise RuntimeError("Target modular replay failed; selection not written")
  selection={"status":"MODULAR_DEPENDENCY_SOURCE_SELECTION_NOT_EXACT_PROOF",
   "point":[p,z,d],"source_equation_count":len(original),
   "targets":target_sources,"union_global_zero_based_ids":sorted(selected),
   "provenance":"Modular elimination DAG from original Kira SYSTEM files; indices are original global_zero_based IDs",
   "exact_target_reduction_proven":False}
  args.selection_output.parent.mkdir(parents=True,exist_ok=True)
  args.selection_output.write_text(json.dumps(selection,indent=2,ensure_ascii=True)+"\n",encoding="utf-8")
  out["selection_output"]=str(args.selection_output)
 print("VP05_SECTOR202_SOURCE_PROOF_PREFLIGHT "+json.dumps(out,ensure_ascii=True),flush=True)
 if not all(t["verified"] for t in tests):raise SystemExit(2)
if __name__=="__main__":main()
