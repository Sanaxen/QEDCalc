"""Select a bounded pilot from the verified modular nonzero original-row support.

Uses global_zero_based ORIGINAL SYSTEM IDs, not exported-list offsets.
An exact smoke pass on a chunk is not an exact A/B target certificate.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT

BASE=ROOT/"output/three_loop_integral_family_audit"
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--certificate",type=Path,default=BASE/"vp05_sector202_modular_provenance_certificate.json")
 ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_support_pilot_ids.json")
 ap.add_argument("--target",choices=["A","B","union"],default="union")
 ap.add_argument("--start",type=int,default=0)
 ap.add_argument("--rows",type=int,default=30)
 args=ap.parse_args()
 if args.start<0 or not 1<=args.rows<=100:ap.error("Require --start >= 0 and 1 <= --rows <= 100")
 raw=args.certificate.read_bytes(); obj=json.loads(raw.decode("utf-8-sig"))
 if obj.get("status")!="MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF":
  raise RuntimeError("Unsupported modular certificate format")
 if obj.get("exact_target_reduction_proven") is not False or obj.get("point")!=[1000003,17,7]:
  raise RuntimeError("Certificate proof status or modular evaluation point mismatch")
 targets=obj.get("target_results",[])
 if len(targets)!=2 or any(t.get("target_index")!=i or t.get("modular_original_replay_verified") is not True for i,t in enumerate(targets)):
  raise RuntimeError("Both independently replayed target entries are required")
 sets=[]
 for t in targets:
  ids=t["support_original_ids"]
  multipliers=t["source_multipliers"]
  if ids!=sorted(set(ids)) or len(ids)!=t["nonzero_original_support"]:
   raise RuntimeError("Invalid ordered modular support IDs")
  if [x[0] for x in multipliers]!=ids or any(type(x[1]) is not int or not 0<x[1]<obj["point"][0] for x in multipliers):
   raise RuntimeError("Nonzero multiplier list inconsistent with support")
  sets.append(set(ids))
 if len(sets[0]&sets[1])!=obj["shared_nonzero_support"] or len(sets[0]|sets[1])!=obj["union_nonzero_support"]:
  raise RuntimeError("Union/shared support mismatch")
 ids=sorted(sets[0] if args.target=="A" else sets[1] if args.target=="B" else sets[0]|sets[1])
 selected=ids[args.start:args.start+args.rows]
 if not selected:raise RuntimeError("Requested pilot slice is empty")
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(selected,indent=2)+"\n",encoding="utf-8")
 print("VP05_SECTOR202_SUPPORT_PILOT "+json.dumps({
  "status":"MODULAR_SUPPORT_SELECTED_NOT_EXACT_PROOF","target":args.target,
  "certificate_sha256":hashlib.sha256(raw).hexdigest(),
  "total_support":len(ids),"start":args.start,"selected_rows":len(selected),
  "first_original_id":selected[0],"last_original_id":selected[-1],
  "output":str(args.output),"exact_target_reduction_proven":False},ensure_ascii=True),flush=True)
if __name__=="__main__":main()
