"""Read-only reconciliation between VP05 L2 custom run and Stage-2 controller.

Never create generic seed PASS, checkpoint, promotion-ready, or modify registry.
Do not infer global basis stability from single-target exact equation.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from three_loop.master_basis_api import build_family_spec
from three_loop.master_basis_batch import AUDIT_DIR,discover_seed_results,family_steps,load_checkpoint,execution_families
from examples.three_loop_sector203_weight_audit import parse_file_integrals
FAMILY="VP05_full"
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,default=DEFAULT);a=p.parse_args()
 spec=build_family_spec(FAMILY);steps=family_steps(FAMILY)
 audits=discover_seed_results();checkpoint=load_checkpoint().get("steps",{})
 source=a.project.resolve()
 saved=source/"results/VP05_full/masters"
 masters=parse_file_integrals(saved) if saved.is_file() else []
 records=[]
 for step in steps:
  cache=audits.get((step.family,step.seed.tag,step.solver))
  prior=checkpoint.get(step.key,{})
  records.append({"phase":step.phase,"seed":step.seed.tag,"solver":step.solver,
                  "cache_hit":bool(cache),"audit":cache.get("path") if cache else None,
                  "checkpoint_status":prior.get("status")})
 promotion=AUDIT_DIR/"three_loop_vp05_full_promotion_ready.json"
 verified=AUDIT_DIR/"vp05_verified_reduction_artifact_v1.json"
 proof=None
 if verified.is_file():
  try:proof=json.loads(verified.read_text(encoding="utf-8-sig"))
  except (ValueError,OSError):pass
 ready=None
 if promotion.is_file():
  try:ready=json.loads(promotion.read_text(encoding="utf-8-sig"))
  except (ValueError,OSError):pass
 report={"status":"VP05_STAGE2_RECONCILIATION_ONLY",
   "canonical_family":FAMILY,
   "in_pending_schedule":FAMILY in execution_families(),
   "canonical_baseline_seed":spec.baseline_seed.tag,
   "canonical_top_sector":spec.top_sector,
   "standard_stage2_steps":records,
   "saved_l2_project":str(source),
   "saved_l2_selected_masters":len(masters),
   "saved_single_target_exact_artifact_present":bool(proof and proof.get("status")=="EXACT_SAVED_KIRA_PROJECT_REDUCTION"),
   "standard_promotion_ready_present":bool(ready),
   "standard_promotion_audit_pass":bool(ready and ready.get("audit_pass") is True),
   "standard_step_complete":all(x["cache_hit"] or x["checkpoint_status"]=="pass" for x in records),
   "l2_seed_is_standard_step":any(x["seed"]=="r6s6d1" for x in records),
   "eligible_for_automatic_reuse":False,
   "one_axis_boundary_verified_from_l2":False,
   "global_candidate_closure_verified_from_l2":False,
   "registration_approved":False,
   "recommended_action":"Do not run Stage-2 VP05 unattended. Review canonical seed, source provenance and resource-safe equivalent boundary/closure plan first.",
   "kira_executed":False,"project_modified":False}
 print("VP05_STAGE2_RECONCILIATION "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
