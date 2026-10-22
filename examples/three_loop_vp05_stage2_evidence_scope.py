"""Read-only scope matrix: VP05 exceptional proofs vs canonical 63-master closure.

Do not interpret a local sector identity as a proof of global basis closure.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR
from three_loop.vp05_verified_reduction import TARGET,MASTER_6,MASTER_5
from examples.three_loop_sector203_weight_audit import ROOT

PREFIX="three_loop_vp05_full_masters_r8s3d0"
SEEDS=("r9s5d2","r8s6d2","r8s5d3")
def read(path):
 try:return json.loads(path.read_text(encoding="utf-8-sig"))
 except (OSError,ValueError):return {}
def parse(s):
 m=re.fullmatch(r"VP05_full\[(-?\d+(?:,-?\d+){11})\]",str(s))
 return tuple(map(int,m.group(1).split(","))) if m else None
def sector(v):return sum(1<<i for i,x in enumerate(v) if x>0)
def main():
 manifest_path=AUDIT_DIR/f"{PREFIX}_candidate_r8s5d2_closure_manifest.json"
 closure_path=AUDIT_DIR/f"{PREFIX}_candidate_r8s5d2_closure_audit.json"
 manifest=read(manifest_path);closure=read(closure_path)
 assert manifest.get("family")=="VP05_full" and manifest.get("candidate_master_count")==63, "Expected saved standard 63-candidate manifest missing"
 candidates=[parse(x) for x in manifest["candidate_masters"]]
 if len(candidates)!=63 or any(x is None for x in candidates) or len(set(candidates))!=63:raise RuntimeError("63 candidate list invalid")
 sections={}
 for v in candidates:sections[sector(v)]=sections.get(sector(v),0)+1
 boundary={r.get("seed"):r for r in closure.get("boundary_rows",[]) if isinstance(r,dict)}
 local_files=sorted(AUDIT_DIR.glob("three_loop_vp05_full_masters_r8s3d0_candidate_sector_closure_*_audit.json"))
 local=[]
 for p in local_files:
  d=read(p);local.append({"file":p.name,"seed":d.get("test_seed"),"audit_pass":d.get("audit_pass"),
   "stable_under_sector_local_closure":d.get("stable_under_sector_local_closure"),"sector_count":d.get("sector_count"),
   "missing_candidate_masters":len(d.get("missing_candidate_masters",[]))})
 artifact=AUDIT_DIR/"vp05_verified_reduction_artifact_v1.json"
 proof=read(artifact)
 target_scope={"target_in_63_candidates":TARGET in candidates,
   "master_6_in_63_candidates":MASTER_6 in candidates,
   "master_5_in_63_candidates":MASTER_5 in candidates,
   "target_sector":sector(TARGET),"master_6_sector":sector(MASTER_6),"master_5_sector":sector(MASTER_5)}
 status=[]
 for seed in SEEDS:
  b=boundary.get(seed,{})
  status.append({"seed":seed,"standard_stable":b.get("stable") is True,
    "standard_error":b.get("error"),"standard_master_count":b.get("master_count"),
    "sector_local_audit_matches":[x for x in local if x["seed"]==seed],
    "whole_family_closure_proven":b.get("stable") is True and not b.get("error")})
 report={"status":"VP05_STAGE2_EVIDENCE_SCOPE_MATRIX","canonical_candidate_count":63,
  "canonical_candidate_sectors":sections,"union_target_count":manifest.get("union_target_count"),
  "closure_target_count":manifest.get("closure_target_count"),
  "standard_boundaries":status,
  "saved_local_sector_audits":local,
  "local_single_target_certificate":{"present":artifact.is_file(),
    "status":proof.get("status"),"scope":target_scope,
    "establishes_one_identity_only":True,"establishes_global_63_closure":False},
  "standard_promotion_ready":(AUDIT_DIR/"three_loop_vp05_full_promotion_ready.json").is_file(),
  "unresolved_obligations":[x["seed"] for x in status if not x["whole_family_closure_proven"]],
  "safety":{"automatic_promotion":False,"falsified_checkpoint":False,"kira_executed":False,"files_modified":False}}
 print("VP05_STAGE2_EVIDENCE_SCOPE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
