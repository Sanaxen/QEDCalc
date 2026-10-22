"""Read-only matrix of missing VP05 Stage-2 closure by seed and sector.

One passing sector audit at r9s5d2 cannot be reused as proof for r8s6d2
or r8s5d3. Inspect saved exact-sector evidence; never infer PASS from
an unrelated seed, a partial Kira run, or the L2 one-target certificate.
"""
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR
from three_loop.vp05_verified_reduction import TARGET,MASTER_5,MASTER_6

STEM="three_loop_vp05_full_masters_r8s3d0"
SEEDS=("r9s5d2","r8s6d2","r8s5d3")
def read(path):
 try:return json.loads(path.read_text(encoding="utf-8-sig"))
 except (OSError,ValueError):return {}
def index(text):
 m=re.fullmatch(r"VP05_full\[(-?\d+(?:,-?\d+){11})\]",str(text))
 if not m:raise ValueError("bad canonical candidate: "+str(text))
 return tuple(map(int,m.group(1).split(",")))
def sector(v):return sum(1<<i for i,n in enumerate(v) if n>0)
def main():
 manifest=read(AUDIT_DIR/f"{STEM}_candidate_r8s5d2_closure_manifest.json")
 closure=read(AUDIT_DIR/f"{STEM}_candidate_r8s5d2_closure_audit.json")
 assert manifest.get("family")=="VP05_full" and manifest.get("candidate_master_count")==63
 candidates=[index(v) for v in manifest["candidate_masters"]]
 assert len(candidates)==63 and len(set(candidates))==63
 groups=defaultdict(list)
 for v in candidates:groups[sector(v)].append(v)
 boundary={v.get("seed"):v for v in closure.get("boundary_rows",[]) if isinstance(v,dict)}
 result=[]
 for seed in SEEDS:
  b=boundary.get(seed,{})
  sector_file=AUDIT_DIR/f"{STEM}_candidate_sector_closure_{seed}_audit.json"
  sector_audit=read(sector_file)
  rows={int(v["sector"]):v for v in sector_audit.get("sector_rows",[]) if isinstance(v,dict) and "sector" in v}
  matrix=[]
  for sid in sorted(groups):
   row=rows.get(sid)
   proven=bool(row and row.get("stable") is True and row.get("error") is None and
               row.get("target_count")==len(groups[sid]) and row.get("missing_candidate_masters")==[])
   matrix.append({"sector":sid,"candidate_count":len(groups[sid]),
       "sector_audit_present":row is not None,"sector_audit_stable":row.get("stable") if row else None,
       "sector_audit_error":row.get("error") if row else None,
       "same_seed_sector_coverage":proven})
  result.append({"seed":seed,"whole_family_boundary_stable":b.get("stable") is True and not b.get("error"),
      "whole_family_error":b.get("error"),"sector_local_audit_file":str(sector_file),
      "sector_local_aggregate_pass":sector_audit.get("audit_pass") is True,
      "same_seed_sector_proven_count":sum(r["same_seed_sector_coverage"] for r in matrix),
      "sector_count":len(matrix),"uncovered_sector_count":sum(not r["same_seed_sector_coverage"] for r in matrix),
      "sectors":matrix})
 report={"status":"VP05_STAGE2_CLOSURE_SECTOR_GAP_MATRIX",
   "candidate_count":len(candidates),"sector_count":len(groups),
   "union_target_count":manifest.get("union_target_count"),
   "seed_rows":result,
   "outstanding_seeds":[row["seed"] for row in result if not row["whole_family_boundary_stable"]],
   "note":"Same-seed sector coverage is an evidence inventory, not automatically equivalent to whole-family closure.",
   "single_target_proof_sector_203_only":True,
   "promotion_allowed":False,"kira_executed":False,"sources_modified":False}
 print("VP05_STAGE2_CLOSURE_SECTOR_GAP "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
