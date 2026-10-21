"""Validate VP05 full-stage preview without running Kira or modifying projects.

Reads prepared project, exact target, audit plan, and the review-only preview.
Copies nothing and never launches a process.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

ROOT=Path("output/vp05_single_nonmaster_reduction_prepared")
AUDIT=Path("output/three_loop_integral_family_audit")
OUTPUT=AUDIT/"vp05_kira_full_stage_specific_validation.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    job=ROOT/"jobs.yaml"
    target=ROOT/"mandatory_single_nonmaster.txt"
    preferred=ROOT/"preferred_provisional64_sector203.txt"
    plan=AUDIT/"vp05_single_nonmaster_full_stage_plan.json"
    preview=AUDIT/"vp05_single_nonmaster_full_stage_jobs.preview.yaml"
    checks={}
    checks["prepared_job_exists"]=job.is_file()
    checks["single_target_exact"]=target.is_file() and parse_file_integrals(target)==[TARGET]
    checks["preferred_masters_exists"]=preferred.is_file()
    checks["preview_exists"]=preview.is_file()
    checks["plan_exists"]=plan.is_file()
    if checks["preview_exists"] and checks["prepared_job_exists"]:
        original=job.read_text(encoding="utf-8-sig")
        raw=preview.read_text(encoding="utf-8-sig")
        header="# REVIEW-ONLY: DO NOT RUN KIRA FROM THIS FILE\n"
        checks["review_only_header"]=raw.startswith(header)
        proposal=raw[len(header):] if raw.startswith(header) else ""
        expected=original
        for flag in ("run_triangular","run_back_substitution"):
            expected=re.sub(r"(^\s*"+flag+r":\s*)false(\s*$)",
                            r"\g<1>true\g<2>",expected,count=1,flags=re.M)
        checks["only_two_stage_flags_differ"]=bool(proposal) and proposal==expected and expected!=original
        checks["sector203_seed"]=bool(re.search(r"sectors:\s*\[203\],\s*r:\s*6,\s*s:\s*6,\s*d:\s*1",proposal))
        checks["truncate_sp_l2"]=bool(re.search(r"truncate_sp:\s*\n\s*-\s*\{topologies:\s*\[VP05_full\],\s*l:\s*2\}",proposal))
        checks["mandatory_list_reference"]=proposal.count("[VP05_full,mandatory_single_nonmaster.txt]")==1
        checks["preferred_masters_reference"]=proposal.count('preferred_provisional64_sector203.txt')==1
        for flag,value in (("run_initiate","true"),("run_triangular","true"),
                           ("run_back_substitution","true"),("run_firefly","false")):
            checks[flag]=len(re.findall(r"^\s*"+flag+r":\s*"+value+r"\s*$",proposal,re.M))==1
    if checks["plan_exists"] and checks["prepared_job_exists"]:
        data=json.loads(plan.read_text(encoding="utf-8-sig"))
        checks["plan_status"]=data.get("status")=="FULL_STAGE_PLAN_ONLY"
        checks["source_hash_unchanged"]=data.get("original_jobs_sha256")==digest(job)
    checks["family_config_exists"]=(ROOT/"config/integralfamilies.yaml").is_file()
    checks["kinematics_exists"]=(ROOT/"config/kinematics.yaml").is_file()
    checks["no_existing_runtime_db"]=not (ROOT/"results/kira.db").exists()
    checks["no_existing_system_files"]=not list(ROOT.rglob("SYSTEM_VP05_full_*.gz"))
    failures=[k for k,v in checks.items() if not v]
    report={"status":"VP05_SPECIFIC_STATIC_PASS" if not failures else "VP05_SPECIFIC_STATIC_BLOCKED",
            "checks":checks,"failed":failures,
            "kira_executed":False,"schema_validated_on_vp05_by_kira":False,
            "actual_kira_monitor_tested":False,"ready_to_execute":False,
            "note":"Checks the prepared preview only. Does not validate actual Kira schema or authorize physical VP05 execution."}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_KIRA_FULL_STAGE_SPECIFIC_VALIDATION "+json.dumps(report,ensure_ascii=False),flush=True)
    if failures:raise SystemExit(2)

if __name__=="__main__":
    main()
