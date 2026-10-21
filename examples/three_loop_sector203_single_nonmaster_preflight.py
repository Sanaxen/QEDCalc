"""Fail-closed preflight of isolated VP05 one-target Kira project.

No Kira launch. Verify copied configs, target-only mandatory list, stage
settings, no inherited SYSTEM/DB, and original source fingerprints.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import parse_file_integrals
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET

COPY=("config/integralfamilies.yaml","config/kinematics.yaml",
      "preferred_provisional64_sector203.txt")
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-project",type=Path,default=DEFAULT_PROJECT)
 ap.add_argument("--project",type=Path,default=Path("output/vp05_single_nonmaster_reduction_prepared"))
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_single_nonmaster_preflight.json"))
 a=ap.parse_args();src=a.source_project.resolve();dst=a.project.resolve()
 checks={}
 def check(name,result):checks[name]=bool(result)
 check("distinct_directory",src!=dst and src not in dst.parents and dst not in src.parents)
 check("destination_exists",dst.is_dir())
 if not dst.is_dir():
  report={"status":"NOT_PREPARED","checks":checks,"kira_executed":False}
 else:
  for rel in COPY:check("copied_"+rel,(src/rel).is_file() and (dst/rel).is_file() and digest(src/rel)==digest(dst/rel))
  m=dst/"mandatory_single_nonmaster.txt"
  check("single_exact_mandatory_integral",m.is_file() and parse_file_integrals(m)==[TARGET])
  job=dst/"jobs.yaml"
  s=job.read_text(encoding="utf-8-sig") if job.is_file() else ""
  check("single_target_list_referenced",'[VP05_full,mandatory_single_nonmaster.txt]' in s)
  check("sector203_r6s6d1",bool(re.search(r"sectors:\s*\[203\],\s*r:\s*6,\s*s:\s*6,\s*d:\s*1",s)))
  check("truncate_sp_l2",bool(re.search(r"truncate_sp:\s*\n\s*-\s*\{topologies:\s*\[VP05_full\],\s*l:\s*2\}",s)))
  for key,expected in (("run_initiate","true"),("run_triangular","false"),
                       ("run_back_substitution","false"),("run_firefly","false")):
   check(key,bool(re.search(r"^\s*"+key+r":\s*"+expected+r"\s*$",s,re.M)))
  check("original_kira_db_not_copied",not (dst/"results/kira.db").exists())
  check("no_kira_SYSTEM_copied",not list(dst.rglob("SYSTEM_VP05_full_*.gz")))
  check("original_project_not_nested",src not in dst.parents)
  check("prepared_manifest_present",(dst/"qedcalc_preparation.json").is_file())
  if (dst/"qedcalc_preparation.json").is_file():
   obj=json.loads((dst/"qedcalc_preparation.json").read_text(encoding="utf-8-sig"))
   check("prepared_not_executed_manifest",obj.get("status")=="PREPARED_NOT_EXECUTED" and obj.get("kira_executed") is False)
  report={"status":"PASS_PREPARE_ONLY" if all(checks.values()) else "FAIL_PREPARE_AUDIT",
   "source_project":str(src),"project":str(dst),"checks":checks,
   "ready_for_physical_reduction":False,"ready_to_execute_kira":False,
   "kira_executed":False,
   "next_requirement":"Explicitly review Kira job schema and set guarded triangular/back-substitution stages in a separate plan; initiate-only cannot establish physical reduction."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_SINGLE_NONMASTER_PREFLIGHT "+json.dumps(report,ensure_ascii=False),flush=True)
 if report["status"]!="PASS_PREPARE_ONLY":raise SystemExit(2)
if __name__=="__main__":main()
