"""Preview a guarded VP05 physical nonmaster reduction job without modifying Kira.

Reads the already prepared project; proposes a full-stage jobs.yaml in a
separate audit folder. Does NOT enable, execute, or overwrite a Kira job.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

DEFAULT=Path("output/vp05_single_nonmaster_reduction_prepared")
OUT=Path("output/three_loop_integral_family_audit")
FLAGS={"run_initiate":"true","run_triangular":"false",
       "run_back_substitution":"false","run_firefly":"false"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--output",type=Path,default=OUT/"vp05_single_nonmaster_full_stage_plan.json")
 p.add_argument("--job-preview",type=Path,default=OUT/"vp05_single_nonmaster_full_stage_jobs.preview.yaml")
 a=p.parse_args()
 root=a.project.resolve()
 job=root/"jobs.yaml";target=root/"mandatory_single_nonmaster.txt"
 errors=[]
 if not root.is_dir() or not job.is_file():errors.append("prepared project/jobs.yaml missing")
 if not target.is_file() or parse_file_integrals(target)!=[TARGET]:errors.append("single mandatory target mismatch")
 raw=job.read_text(encoding="utf-8-sig") if job.is_file() else ""
 if "[VP05_full,mandatory_single_nonmaster.txt]" not in raw:errors.append("mandatory selection missing")
 if not re.search(r"sectors:\s*\[203\],\s*r:\s*6,\s*s:\s*6,\s*d:\s*1",raw):
  errors.append("seed differs from expected r6s6d1")
 if not re.search(r"truncate_sp:\s*\n\s*-\s*\{topologies:\s*\[VP05_full\],\s*l:\s*2\}",raw):
  errors.append("truncate_sp l=2 missing")
 for key,value in FLAGS.items():
  if len(re.findall(r"^\s*"+key+r":\s*"+value+r"\s*$",raw,re.M))!=1:
   errors.append(key+" must occur exactly once with "+value)
 for rel in ("config/integralfamilies.yaml","config/kinematics.yaml",
             "preferred_provisional64_sector203.txt"):
  if not (root/rel).is_file():errors.append(rel+" missing")
 if (root/"results/kira.db").exists() or list(root.rglob("SYSTEM_VP05_full_*.gz")):
  errors.append("prepared project already contains Kira runtime outputs; refuse to plan")
 # Preserve original source verbatim except for the two explicit stage switches.
 proposal=raw
 if not errors:
  for key in ("run_triangular","run_back_substitution"):
   proposal=re.sub(r"(^\s*"+key+r":\s*)false(\s*$)",r"\g<1>true\g<2>",proposal,count=1,flags=re.M)
  if proposal==raw:errors.append("proposed job unchanged")
  for key in ("run_triangular","run_back_substitution"):
   if not re.search(r"^\s*"+key+r":\s*true\s*$",proposal,re.M):errors.append("stage switch failed: "+key)
 report={"status":"BLOCKED" if errors else "FULL_STAGE_PLAN_ONLY",
  "prepared_project":str(root),
  "target":"VP05_full["+",".join(map(str,TARGET))+"]",
  "original_jobs_sha256":sha(job) if job.is_file() else None,
  "proposed_job_preview":str(a.job_preview),"errors":errors,
  "run_triangular_proposed":True,"run_back_substitution_proposed":True,
  "runtime_limits_enforced":False,"schema_validated_by_kira":False,
  "kira_executed":False,"original_project_modified":False,
  "ready_to_execute":False,
  "next_requirement":"Validate Kira version/schema and monitored process resource guard, then create a separate execution-only project and obtain explicit execution approval. Never run the preview directly."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 if not errors:
  a.job_preview.parent.mkdir(parents=True,exist_ok=True)
  a.job_preview.write_text("# REVIEW-ONLY: DO NOT RUN KIRA FROM THIS FILE\n"+proposal,encoding="utf-8")
 print("VP05_SINGLE_NONMASTER_FULL_STAGE_PLAN "+json.dumps(report,ensure_ascii=False),flush=True)
 if errors:raise SystemExit(2)
if __name__=="__main__":main()
