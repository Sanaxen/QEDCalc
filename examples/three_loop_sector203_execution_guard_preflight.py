"""Fail-closed, read-only preflight for VP05 isolated Kira execution.

NO Kira invocation and NO execution directory creation.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,stat
from pathlib import Path
from examples.three_loop_sector203_kira_full_stage_specific_validation import ROOT,AUDIT
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

CAPSULE=Path("output/vp05_full_stage_execution_capsule")
FILES=("config/integralfamilies.yaml","config/kinematics.yaml",
       "mandatory_single_nonmaster.txt","preferred_provisional64_sector203.txt","jobs.yaml")

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--destination",type=Path,default=Path("output/vp05_full_stage_kira_experiment"))
 p.add_argument("--output",type=Path,default=AUDIT/"vp05_full_stage_execution_guard_preflight.json")
 a=p.parse_args()
 checks={}
 def ck(n,value):checks[n]=bool(value)
 capsule=CAPSULE.resolve();dest=a.destination.resolve()
 source=ROOT.resolve();audit=AUDIT.resolve()
 ck("capsule_exists",CAPSULE.is_dir() and not CAPSULE.is_symlink())
 ck("destination_not_present",not a.destination.exists() and not a.destination.is_symlink())
 ck("destination_isolated", all(dest != x and x not in dest.parents and dest not in x.parents
                                    for x in (capsule,source,audit)))
 ck("destination_under_output",Path("output").resolve() in dest.parents)
 manifest=CAPSULE/"CAPSULE_REVIEW_ONLY.json"
 ck("manifest_exists",manifest.is_file() and not manifest.is_symlink())
 data={}
 if checks["manifest_exists"]:
  try:data=json.loads(manifest.read_text(encoding="utf-8-sig"))
  except (OSError,ValueError):pass
 ck("manifest_created_not_executed",data.get("status")=="CAPSULE_CREATED_NOT_EXECUTED"
    and data.get("kira_executed") is False)
 expected=data.get("files_sha256")
 ck("manifest_file_set",isinstance(expected,dict) and set(expected)==set(FILES))
 for f in FILES:
  file=CAPSULE/f
  ck("safe_file_"+f.replace("/","_"),file.is_file() and not file.is_symlink())
  ck("hash_"+f.replace("/","_"),checks["safe_file_"+f.replace("/","_")]
     and isinstance(expected,dict) and sha(file)==expected.get(f))
 for f in FILES[:-1]:
  ck("unchanged_source_"+f.replace("/","_"),(ROOT/f).is_file()
     and (CAPSULE/f).is_file() and sha(ROOT/f)==sha(CAPSULE/f))
 ck("single_target", (CAPSULE/FILES[2]).is_file()
    and parse_file_integrals(CAPSULE/FILES[2])==[TARGET])
 audit_file=AUDIT/"vp05_full_stage_capsule_audit.json"
 ck("capsule_audit_pass",audit_file.is_file()
    and json.loads(audit_file.read_text(encoding="utf-8-sig")).get("status")=="CAPSULE_AUDIT_PASS_NOT_EXECUTED")
 contents=set()
 if CAPSULE.is_dir():
  for f in CAPSULE.rglob("*"):
   if f.is_symlink():contents.add("SYMLINK:"+str(f.relative_to(CAPSULE)))
   elif f.is_file():contents.add(f.relative_to(CAPSULE).as_posix())
 ck("no_extra_files",contents==set(FILES)|{"CAPSULE_REVIEW_ONLY.json"})
 disk=shutil.disk_usage(Path("output").resolve())
 ck("disk_free_at_least_20_gib",disk.free>=20*1024**3)
 fail=[k for k,v in checks.items() if not v]
 report={"status":"EXECUTION_GUARD_PREFLIGHT_PASS_NO_KIRA" if not fail else "EXECUTION_GUARD_PREFLIGHT_BLOCKED",
  "checks":checks,"failed":fail,"destination":str(dest),"disk_free_gib":round(disk.free/1024**3,2),
  "kira_executed":False,"experiment_created":False,"ready_to_execute":False,
  "note":"No physical VP05 test is authorized; separate monitored execution implementation and review remain required."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_EXECUTION_GUARD_PREFLIGHT "+json.dumps(report,ensure_ascii=False),flush=True)
 if fail:raise SystemExit(2)

if __name__=="__main__":main()
