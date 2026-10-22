"""Finite-field target provenance certificate and actual nonzero support audit.

Reconstruct exact *modular* original-row multipliers by reversing the sparse
pivot elimination DAG, then independently replay original SYSTEM rows.
This does NOT establish a rational-function identity over Q(z,d).
"""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_symbolic_source_preflight import load_rows
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS
from examples.three_loop_vp05_sector202_bivariate_candidate_verify import functions

DEFAULT=ROOT/"output/three_loop_integral_family_audit/vp05_sector202_modular_provenance_certificate.json"

def add(target,key,value,p):
 value=(target.get(key,0)+value)%p
 if value:target[key]=value
 else:target.pop(key,None)

def reduce(row,pivots,p,cap):
 operations=[]
 while row:
  lead=min(row)
  if lead not in pivots:break
  basis,owner,inv=pivots[lead]
  factor=row[lead]
  operations.append((owner,factor))
  for k,v in basis.items():
   add(row,k,-factor*v,p)
  if len(row)>cap:raise RuntimeError("Modular row fill cap exceeded")
 return operations

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--prime",type=int,default=1000003)
 ap.add_argument("--z",type=int,default=17)
 ap.add_argument("--d",type=int,default=7)
 ap.add_argument("--max-fill",type=int,default=20000)
 ap.add_argument("--output",type=Path,default=DEFAULT)
 args=ap.parse_args()
 p,z,d=args.prime,args.z,args.d
 if p<=2:ap.error("Prime must be >2")
 codec_mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=codec_mod.from_kiradb(str(P/"results/kira.db"))
 if ordering!=5:raise RuntimeError("Unexpected Kira ordering")
 codec=codec_mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 keys=[(codec.encode(v),139) for v in TARGETS]
 if any(tuple(codec.decode(x[0]))!=v for x,v in zip(keys,TARGETS)):
  raise RuntimeError("Target codec roundtrip mismatch")
 from examples.three_loop_vp05_sector202_symbolic_source_preflight import coefficient
 original=load_rows(p,z,d)
 if len(original)!=2678:raise RuntimeError("Unexpected original SYSTEM equation count")
 pivots={};operations={};inverse={};rank=0
 for index,(original_row,meta) in enumerate(original):
  row=original_row.copy()
  ops=reduce(row,pivots,p,args.max_fill)
  if not row:continue
  lead=min(row);inv=pow(row[lead],-1,p)
  normalized={k:v*inv%p for k,v in row.items()}
  pivots[lead]=(normalized,index,inv)
  operations[index]=ops
  inverse[index]=inv
  rank+=1
 values=functions(z,d)
 target_results=[]
 for i,target_key in enumerate(keys[:2]):
  a,b=values[2*i:2*i+2]
  if a.denominator%p==0 or b.denominator%p==0:raise RuntimeError("Singular candidate")
  av=a.numerator%p*pow(a.denominator%p,-1,p)%p
  bv=b.numerator%p*pow(b.denominator%p,-1,p)%p
  target={target_key:1}
  add(target,keys[2],-av,p)
  add(target,(4,73),-bv,p)
  target_original=target.copy()
  target_operations=reduce(target,pivots,p,args.max_fill)
  if target:raise RuntimeError("Target modular elimination has nonzero remainder")
  required=defaultdict(int)
  for owner,factor in target_operations:
   required[owner]=(required[owner]+factor)%p
  multipliers={}
  for owner in sorted(operations,reverse=True):
   coeff=required.get(owner,0)%p
   if not coeff:continue
   scale=coeff*inverse[owner]%p
   if scale:multipliers[owner]=scale
   for parent,factor in operations[owner]:
    required[parent]=(required[parent]-scale*factor)%p
  replay={}
  for owner,factor in multipliers.items():
   for key,value in original[owner][0].items():
    add(replay,key,factor*value,p)
  if replay!=target_original:
   raise AssertionError("Original SYSTEM coefficient replay differs from modular target")
  target_results.append({"target_index":i,"target":list(TARGETS[i]),"modular_coeff_C":av,
   "modular_coeff_small4":bv,"direct_pivot_steps":len(target_operations),
   "nonzero_original_support":len(multipliers),
   "support_original_ids":sorted(multipliers),
   "source_multipliers":[[owner,multipliers[owner]] for owner in sorted(multipliers)],
   "modular_original_replay_verified":True})
 result={"status":"MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF",
  "point":[p,z,d],"total_original_rows":len(original),"rank":rank,
  "target_results":target_results,
  "shared_nonzero_support":len(set(target_results[0]["support_original_ids"])&set(target_results[1]["support_original_ids"])),
  "union_nonzero_support":len(set(target_results[0]["support_original_ids"])|set(target_results[1]["support_original_ids"])),
  "exact_target_reduction_proven":False,"kira_executed":False,"original_files_modified":False}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_SECTOR202_MODULAR_SUPPORT "+json.dumps({
  "status":result["status"],"point":result["point"],"rank":rank,
  "target_nonzero_support":[x["nonzero_original_support"] for x in target_results],
  "direct_pivot_steps":[x["direct_pivot_steps"] for x in target_results],
  "shared_nonzero_support":result["shared_nonzero_support"],
  "union_nonzero_support":result["union_nonzero_support"],
  "modular_original_replay_verified":True,
  "exact_target_reduction_proven":False,"output":str(args.output)},ensure_ascii=True),flush=True)
if __name__=="__main__":main()
