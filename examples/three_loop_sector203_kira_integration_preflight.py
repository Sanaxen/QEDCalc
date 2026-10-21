"""Non-executing integration preflight for VP05 single-nonmaster full-stage Kira.

Checks source fingerprints, prepared job, proposal and guard prerequisites.
Does not launch Kira, copy job files into a runnable project, or imply
that static safety tests amount to runtime validation.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

AUDIT=Path("output/three_loop_integral_family_audit")
PREP=Path("output/vp05_single_nonmaster_reduction_prepared")

def load(path):
 return json.loads(path.read_text(encoding="utf-8-sig"))
def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--prepared",type=Path,default=PREP)
 p.add_argument("--audit-folder",type=Path,default=AUDIT)
 p.add_argument("--output",type=Path,default=AUDIT/"vp05_kira_execution_integration_preflight.json")
 a=p.parse_args()
 checks={};notes=[]
 job=a.prepared/"jobs.yaml"
 proposed=a.audit_folder/"vp05_single_nonmaster_full_stage_jobs.preview.yaml"
 plan=a.audit_folder/"vp05_single_nonmaster_full_stage_plan.json"
 group=a.audit_folder/"vp05_process_group_stop_smoke.json"
 resource=a.audit_folder/"vp05_wsl_resource_preflight.json"
 ram=a.audit_folder/"vp05_ram_swap_guard_smoke.json"
 target=a.prepared/"mandatory_single_nonmaster.txt"
 def ck(key,condition):checks[key]=bool(condition)
 ck("original_prepared_job_exists",job.is_file())
 ck("single_target_present",target.is_file() and parse_file_integrals(target)==[TARGET])
 ck("full_stage_plan_exists",plan.is_file())
 ck("preview_yaml_exists",proposed.is_file())
 if plan.is_file() and job.is_file():
  v=load(plan)
  ck("plan_status",v.get("status")=="FULL_STAGE_PLAN_ONLY")
  ck("original_job_hash_unchanged",v.get("original_jobs_sha256")==digest(job))
 else:
  ck("plan_status",False);ck("original_job_hash_unchanged",False)
 if proposed.is_file():
  text=proposed.read_text(encoding="utf-8-sig")
  ck("preview_both_stages_on",all(re.search(r"^\s*"+x+r":\s*true\s*$",text,re.M)
      for x in ("run_triangular","run_back_substitution")))
  ck("preview_only_header",text.startswith("# REVIEW-ONLY: DO NOT RUN KIRA FROM THIS FILE"))
 else:
  ck("preview_both_stages_on",False);ck("preview_only_header",False)
 ck("dummy_process_stop_pass",group.is_file() and load(group).get("status")=="PASS_DUMMY_PROCESS_GROUP_STOP")
 ck("wsl_resource_pass",resource.is_file() and load(resource).get("status")=="RESOURCE_PREFLIGHT_PASS")
 ck("ram_swap_dummy_test_pass",ram.is_file() and load(ram).get("status")=="PASS_DUMMY_RAM_SWAP_GUARD"
    and load(ram).get("ram_and_swap_policy_tested") is True)
 ck("no_db_copied",not (a.prepared/"results/kira.db").exists())
 ck("no_system_copied",not list(a.prepared.rglob("SYSTEM_VP05_full_*.gz")))
 incomplete=[name for name,ok in checks.items() if not ok]
 report={"status":"INTEGRATION_PREREQUISITES_PRESENT" if not incomplete else "INTEGRATION_BLOCKED",
  "checks":checks,"incomplete":incomplete,"prepared_project":str(a.prepared),
  "schema_validated_by_kira":False,"monitor_with_real_kira_tested":False,
  "kira_executed":False,"ready_to_execute":False,
  "note":"Passing these prerequisite checks does not create or authorize a runnable Kira job. A separately reviewed resource-bounded execution wrapper and Kira schema confirmation are still required."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_KIRA_INTEGRATION_PREFLIGHT "+json.dumps(report),flush=True)
 if incomplete:raise SystemExit(2)
if __name__=="__main__":main()
