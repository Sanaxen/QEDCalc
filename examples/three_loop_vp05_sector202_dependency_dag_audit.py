"""Audit VP05 target modular dependency DAG and prepare deterministic proof batches.

Finite-field DAG only; no assertion of exact rational target reduction.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT

DEFAULT=ROOT/"output/three_loop_integral_family_audit/vp05_sector202_target_dependency_selection.json"
OUTPUT=ROOT/"output/three_loop_integral_family_audit/vp05_sector202_dependency_plan.json"

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--input",type=Path,default=DEFAULT)
 ap.add_argument("--output",type=Path,default=OUTPUT)
 ap.add_argument("--batch-size",type=int,default=100)
 args=ap.parse_args()
 if not 1<=args.batch_size<=100:ap.error("--batch-size must be 1..100")
 raw=args.input.read_bytes();data=json.loads(raw.decode("utf-8-sig"))
 if data.get("status")!="MODULAR_DEPENDENCY_SOURCE_SELECTION_NOT_EXACT_PROOF":raise ValueError("Unexpected source selection")
 target_sets=[set(t["global_zero_based_ids"]) for t in data["targets"]]
 if len(target_sets)!=2:raise ValueError("Expected exactly two targets")
 union=set().union(*target_sets)
 if sorted(union)!=data["union_global_zero_based_ids"]:raise ValueError("Union mismatch")
 edges={int(i):v for i,v in data.get("dependency_edges",{}).items()}
 if set(edges)!=union:raise ValueError("Missing DAG edges; rerun preflight --selection-output with current code")
 depth={}
 for node in sorted(union):
  parents=edges[node]
  if parents!=sorted(set(parents)):raise ValueError("Duplicate/unsorted parent IDs")
  if any(parent>=node or parent not in union for parent in parents):
   raise ValueError("Non-causal or missing DAG ancestor")
  depth[node]=1+max((depth[parent] for parent in parents),default=0)
 batches=[]
 for i in range(0,len(union),args.batch_size):
  ids=sorted(union)[i:i+args.batch_size]
  batches.append({"batch_index":len(batches),"global_zero_based_ids":ids,"count":len(ids),
                  "max_depth":max(depth[j] for j in ids)})
 overlap=target_sets[0]&target_sets[1]
 result={"status":"MODULAR_DAG_AUDITED_NOT_EXACT_PROOF",
  "input_sha256":hashlib.sha256(raw).hexdigest(),"modular_point":data["point"],
  "target_rows":[len(x) for x in target_sets],"shared_rows":len(overlap),
  "only_A":len(target_sets[0]-target_sets[1]),"only_B":len(target_sets[1]-target_sets[0]),
  "union_rows":len(union),"dependency_edges":sum(len(v) for v in edges.values()),
  "max_dependency_depth":max(depth.values()),"depth_histogram":dict(sorted(Counter(depth.values()).items())),
  "batch_size":args.batch_size,"batches":batches,
  "exact_target_reduction_proven":False}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_SECTOR202_DEPENDENCY_DAG_AUDIT "+json.dumps({k:v for k,v in result.items() if k not in ("batches","depth_histogram")}|{"output":str(args.output)},ensure_ascii=True),flush=True)
if __name__=="__main__":main()
