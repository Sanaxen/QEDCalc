"""Read-only recovery of VP05 Stage-2 boundary/union/closure history."""
from __future__ import annotations
import json
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR
def load(path):
 try:return json.loads(path.read_text(encoding="utf-8-sig"))
 except (OSError,ValueError):return {}
def main():
 prefix="three_loop_vp05_full"
 patterns={
  "boundary_aggregate":f"{prefix}_masters_r8s3d0_boundary_aggregate_audit.json",
  "promotion_ready":f"{prefix}_promotion_ready.json",
 }
 results={}
 for k,n in patterns.items():
  p=AUDIT_DIR/n;v=load(p)
  results[k]={"present":p.is_file(),"path":str(p),
   "audit_pass":v.get("audit_pass"),"stage":v.get("stage"),
   "stable_under_one_axis_extensions":v.get("stable_under_one_axis_extensions"),
   "union_reduction_needed":v.get("union_reduction_needed"),
   "baseline_master_count":v.get("baseline_master_count"),
   "errors":v.get("errors")}
 related=[]
 for p in sorted(AUDIT_DIR.glob("*vp05_full*")):
  name=p.name.lower()
  if p.suffix!=".json" or not any(s in name for s in
    ("union","closure","refinement","boundary","promotion")):continue
  v=load(p)
  related.append({"name":p.name,"stage":v.get("stage"),
   "audit_pass":v.get("audit_pass"),"stable":v.get("stable_under_one_axis_extensions"),
   "union_needed":v.get("union_reduction_needed"),
   "master_count":v.get("master_count"),
   "candidate_master_count":v.get("candidate_master_count"),
   "errors":str(v.get("errors",[]))[:250]})
 report={"status":"VP05_STAGE2_HISTORY_READ_ONLY",
  "canonical_boundary":results["boundary_aggregate"],
  "promotion_ready":results["promotion_ready"],
  "related_audit_count":len(related),"related_audits":related[:100],
  "related_truncated":len(related)>100,
  "conclusion":"Inventory only; no Stage-2 promotion is inferred.",
  "kira_executed":False,"sources_modified":False}
 print("VP05_STAGE2_HISTORY "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
