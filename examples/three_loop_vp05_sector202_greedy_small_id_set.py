"""Read-only greedy formal-free-column reduction for saved VP05 sector202 IBPs.

Use a fixed prime/evaluation point. Greedy deletion re-tests both physical
sector202 target memberships each time; resulting set is locally irredundant
only for this ordering/point, not globally minimal or a physical master proof.
"""
from __future__ import annotations
import argparse,json
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-fill",type=int,default=20000)
 a=ap.parse_args()
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,order=m.from_kiradb(str(P/"results/kira.db"))
 if order!=5:raise RuntimeError("wrong Kira weight ordering")
 codec=m.WeightCodec(np=12,bits=bits,iord=order,topsectors=[203])
 target=[(codec.encode(v),139) for v in TARGETS]
 if any(tuple(codec.decode(w))!=v for v,(w,s) in zip(TARGETS,target)):raise RuntimeError("roundtrip mismatch")
 rows=[];cols=set()
 for f in sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  for row in equations(f,1000003,17,7):rows.append(row);cols.update(row)
 if len(rows)!=2678:raise RuntimeError("unexpected source count")
 opaque=sorted(x for x in cols if x[0]<1024)
 pivots={}
 for row in rows:insert(row,pivots,1000003,a.max_fill)
 def trial(free):
  span=pivots.copy()
  for key in [target[2]]+list(free):insert({key:1},span,1000003,a.max_fill)
  membership=[]
  for k in target[:2]:
   test=span.copy()
   membership.append(not insert({k:1},test,1000003,a.max_fill))
  return membership,len(span)
 before,full_rank=trial(opaque)
 if before!=[True,True]:raise RuntimeError("unexpected full-set status")
 kept=list(opaque);steps=[]
 # Deterministic descending order helps test multiple deletions beyond leave-one-out.
 for key in reversed(opaque):
  proposal=[x for x in kept if x!=key]
  membership,rank=trial(proposal)
  drop=all(membership)
  steps.append({"candidate_removed":list(key),"removal_accepted":drop,
    "both_targets_still_in_relaxed_span":membership,"augmented_rank":rank})
  if drop:kept=proposal
 final,rank=trial(kept)
 report={"status":"VP05_SECTOR202_GREEDY_OPAQUE_FREE_SET",
  "equations":len(rows),"raw_rank":len(pivots),"columns":len(cols),
  "prime":1000003,"z":17,"d":7,"initial_opaque_count":len(opaque),
  "initial_augmented_rank":full_rank,"greedy_deletion_steps":steps,
  "remaining_formal_small_ids":[list(x) for x in kept],
  "remaining_count":len(kept),"final_augmented_rank":rank,
  "final_target_membership":final,
  "proves_exact_coefficients":False,
  "scope":"Greedy subset only at one modular point and using opaque formal columns. No validated physical master mapping/complete 63-master quotient, no exact symbolic reduction, no globally minimality.",
  "kira_executed":False,"files_modified":False}
 print("VP05_SECTOR202_GREEDY_SMALL_ID_SET "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
