"""Prepare VP05 full-stage execution capsule; never invoke Kira.

Fails closed on stale validation, missing inputs, or existing destination.
Only five small allowlisted text files are copied. Review-only by design.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil
from pathlib import Path
from examples.three_loop_sector203_kira_full_stage_specific_validation import ROOT,AUDIT
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

HEADER="# REVIEW-ONLY: DO NOT RUN KIRA FROM THIS FILE\n"
FILES=("config/integralfamilies.yaml","config/kinematics.yaml",
       "mandatory_single_nonmaster.txt","preferred_provisional64_sector203.txt")

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--create",action="store_true",help="Create a new capsule; NEVER start Kira")
 p.add_argument("--destination",type=Path,default=Path("output/vp05_full_stage_execution_capsule"))
 a=p.parse_args()
 dest=a.destination.resolve()
 source=ROOT.resolve();audit=AUDIT.resolve()
 validation=audit/"vp05_kira_full_stage_specific_validation.json"
 plan=audit/"vp05_single_nonmaster_full_stage_plan.json"
 preview=audit/"vp05_single_nonmaster_full_stage_jobs.preview.yaml"
 errors=[]
 if dest==source or source in dest.parents or dest==audit or audit in dest.parents:
  errors.append("destination under source/audit")
 if dest.exists():errors.append("destination already exists (never overwrite)")
 for f in FILES:
  if not (source/f).is_file():errors.append("missing "+f)
 if not validation.is_file() or json.loads(validation.read_text(encoding="utf-8-sig")).get("status")!="VP05_SPECIFIC_STATIC_PASS":
  errors.append("specific static PASS report missing")
 if not plan.is_file() or not preview.is_file():errors.append("missing plan or preview")
 if not errors:
  v=json.loads(validation.read_text(encoding="utf-8-sig"))
  if not v.get("checks") or not all(v["checks"].values()):
   errors.append("static checks incomplete")
  plan_data=json.loads(plan.read_text(encoding="utf-8-sig"))
  if plan_data.get("status")!="FULL_STAGE_PLAN_ONLY" or plan_data.get("original_jobs_sha256")!=sha(source/"jobs.yaml"):
   errors.append("source hash or plan mismatch")
  data=preview.read_text(encoding="utf-8-sig")
  if not data.startswith(HEADER):errors.append("review header missing")
  if parse_file_integrals(source/"mandatory_single_nonmaster.txt")!=[TARGET]:
   errors.append("target changed")
  if any((source/x).is_symlink() for x in (*FILES,"jobs.yaml")):errors.append("source symlink prohibited")
  if not errors:
   # Derive the exact permitted two-flag change, independently of old report.
   old=(source/"jobs.yaml").read_text(encoding="utf-8-sig")
   expected=old.replace("      run_triangular: false\n","      run_triangular: true\n",1).replace(
      "      run_back_substitution: false\n","      run_back_substitution: true\n",1)
   if expected==old or data[len(HEADER):]!=expected:errors.append("preview no longer matches source")
 report={"status":"BLOCKED" if errors else ("CAPSULE_CREATED_NOT_EXECUTED" if a.create else "CAPSULE_PLAN_ONLY"),
  "destination":str(dest),"errors":errors,"kira_executed":False,
  "original_project_opened":False,"ready_to_execute":False}
 if a.create and not errors:
  dest.mkdir(parents=True,exist_ok=False)
  digests={}
  for f in FILES:
   target=dest/f;target.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(source/f,target);digests[f]=sha(target)
  job_file=dest/"jobs.yaml"
  job_file.write_text(data[len(HEADER):],encoding="utf-8",newline="\n")
  digests["jobs.yaml"]=sha(job_file)
  report["files_sha256"]=digests
  (dest/"CAPSULE_REVIEW_ONLY.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_FULL_STAGE_CAPSULE_PREPARE "+json.dumps(report,ensure_ascii=False),flush=True)
 if errors:raise SystemExit(2)

if __name__=="__main__":
 main()
