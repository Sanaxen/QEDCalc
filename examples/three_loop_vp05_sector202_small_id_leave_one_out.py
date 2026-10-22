"""Read-only leave-one-out opaque Kira ID sensitivity on saved VP05 L2 IBPs.

Each probe begins from independent shallow copies of modular rowspace pivots.
Formal opaque free columns are not identified with physical master integrals.
"""
from __future__ import annotations
import json,argparse
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_sector203_weight_audit import ROOT,load_codec

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-fill",type=int,default=20000)
 args=ap.parse_args()
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=m.from_kiradb(str(P/"results/kira.db"))
 if ordering!=5:raise RuntimeError("L2 project requires ordering=5")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 keys=[(codec.encode(t),139) for t in TARGETS]
 if any(tuple(codec.decode(w))!=t for t,(w,s) in zip(TARGETS,keys)):raise RuntimeError("codec roundtrip failed")
 rows=[];cols=set()
 for f in sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  for row in equations(f,1000003,17,7):rows.append(row);cols.update(row)
 if len(rows)!=2678:raise RuntimeError("wrong source equation count")
 small=sorted(k for k in cols if k[0]<1024)
 pivots={}
 for row in rows:insert(row,pivots,1000003,args.max_fill)
 cases=[]
 for excluded in [None]+small:
  span=pivots.copy()
  for key in dict.fromkeys([keys[2]]+[k for k in small if k!=excluded]):
   insert({key:1},span,1000003,args.max_fill)
  status=[]
  for t,key in zip(TARGETS[:2],keys[:2]):
   probe=span.copy()
   increase=insert({key:1},probe,1000003,args.max_fill)
   status.append({"exponents":list(t),"in_relaxed_span":not increase})
  cases.append({"excluded_opaque_id":list(excluded) if excluded is not None else None,
   "augmented_rank":len(span),"target_results":status})
 print("VP05_SECTOR202_SMALL_ID_LEAVE_ONE_OUT "+json.dumps({
  "status":"VP05_SECTOR202_SMALL_ID_LEAVE_ONE_OUT","rows":len(rows),
  "raw_rank":len(pivots),"small_ids":[list(k) for k in small],
  "prime":1000003,"z":17,"d":7,"cases":cases,
  "interpretation":"Single-point leave-one-out tests identify necessary formal opaque columns only relative to this chosen full set. They do not establish physical master identities, sufficiency across other points, or exact symbolic reduction.",
  "exact_reduction_proven":False,"kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
