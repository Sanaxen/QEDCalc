"""Read-only inventory of the first bounded VP05 Kira experiment.

Never launches Kira, deletes files, or calls the guarded runner.
Do not interpret a progress line as proof that its sector completed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, stat
from collections import defaultdict
from pathlib import Path

DEFAULT_RUN=Path("output/vp05_full_stage_kira_experiment")
DEFAULT_REPORT=Path("output/three_loop_integral_family_audit/vp05_full_stage_experiment_inventory.json")
CAPSULE=Path("output/vp05_full_stage_execution_capsule")
GUARD=Path("output/three_loop_integral_family_audit/vp05_full_stage_guarded_run.json")
INPUTS=("jobs.yaml","config/integralfamilies.yaml","config/kinematics.yaml",
        "mandatory_single_nonmaster.txt","preferred_provisional64_sector203.txt")

def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as fh:
  for chunk in iter(lambda:fh.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()

def equivalent_local_paths(recorded, actual):
 """Compare a Windows path and its WSL /mnt/<drive> representation without filesystem mutation."""
 def normalize(value):
  if not isinstance(value,str) or not value.strip():return None
  v=value.strip().replace(chr(92),"/").rstrip("/")
  windows=re.fullmatch(r"([A-Za-z]):/(.*)",v)
  if windows:v="/mnt/"+windows.group(1).lower()+"/"+windows.group(2)
  return v.casefold()
 return normalize(recorded)==normalize(actual) and normalize(actual) is not None

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--run-dir",type=Path,default=DEFAULT_RUN)
 p.add_argument("--output",type=Path,default=DEFAULT_REPORT)
 a=p.parse_args()
 run=a.run_dir.resolve()
 checks={}
 def ck(key,yes):checks[key]=bool(yes)
 ck("run_directory_exists",run.is_dir() and not run.is_symlink())
 ck("run_directory_isolated",run!=CAPSULE.resolve()
    and CAPSULE.resolve() not in run.parents
    and run!=Path("output/vp05_single_nonmaster_reduction_prepared").resolve())
 files=[];by_top=defaultdict(lambda:{"files":0,"bytes":0})
 links=[];errors=[]
 if checks["run_directory_exists"]:
  for base,dirs,names in os.walk(run,followlinks=False):
   for name in dirs+names:
    path=Path(base)/name
    relative=path.relative_to(run).as_posix()
    try:
     info=path.lstat()
     if stat.S_ISLNK(info.st_mode):
      links.append(relative);continue
     if stat.S_ISREG(info.st_mode):
      size=info.st_size
      files.append({"path":relative,"bytes":size})
      top=relative.split("/")[0]
      by_top[top]["files"]+=1;by_top[top]["bytes"]+=size
    except OSError as exc:errors.append(relative+": "+str(exc))
 ck("no_symlinks",not links)
 ck("input_files_present",all((run/f).is_file() and not (run/f).is_symlink() for f in INPUTS))
 manifest=CAPSULE/"CAPSULE_REVIEW_ONLY.json"
 hashes={}
 if manifest.is_file():
  try:hashes=json.loads(manifest.read_text(encoding="utf-8-sig")).get("files_sha256",{})
  except (OSError,ValueError):pass
 ck("all_input_hashes_match_capsule",isinstance(hashes,dict) and
    all((run/f).is_file() and not (run/f).is_symlink() and sha(run/f)==hashes.get(f) for f in INPUTS))
 guard={}
 if GUARD.is_file():
  try:guard=json.loads(GUARD.read_text(encoding="utf-8-sig"))
  except (OSError,ValueError):pass
 ck("guard_path_matches",equivalent_local_paths(guard.get("destination"),str(run)))
 ck("guard_was_executed",guard.get("kira_executed") is True)
 ck("guard_process_reaped",guard.get("process_reaped") is True)
 ck("guard_group_gone",guard.get("process_group_gone") is True)
 ck("guard_record_for_this_run",checks["guard_path_matches"]
    and checks["guard_was_executed"] and checks["guard_process_reaped"] and checks["guard_group_gone"])
 log=run/"kira_run.log"
 ck("kira_log_present",log.is_file() and not log.is_symlink())
 progress={"last_generation_sector":None,"last_generation_ordinal":None,
           "generation_total":None,"triangular_started":False,
           "back_substitution_started":False,"reduction_reported":False,
           "log_evidence_only":True}
 if checks["kira_log_present"]:
  text=log.read_text(encoding="utf-8",errors="replace")
  matches=list(re.finditer(r"Generate equations for topology VP05_full, sector (\d+) \((\d+) of (\d+)\)",text))
  if matches:
   m=matches[-1]
   progress.update(last_generation_sector=int(m[1]),last_generation_ordinal=int(m[2]),generation_total=int(m[3]))
  progress["triangular_started"]="Bring system in triangular form" in text
  progress["back_substitution_started"]="Run the back substitution" in text
  progress["reduction_reported"]=bool(re.search(r"\d+ equations were reduced",text))
 failed=[key for key,val in checks.items() if not val]
 report={"status":"EXPERIMENT_INVENTORY_PASS" if not failed and not errors else "EXPERIMENT_INVENTORY_REVIEW_REQUIRED",
         "checks":checks,"failed":failed,"walk_errors":errors,
         "run_directory":str(run),"guard_recorded_destination":guard.get("destination"),
         "guard_recorded_status":guard.get("status"),"guard_stop_reason":guard.get("stop_reason"),
         "guard_returncode":guard.get("returncode"),"file_count":len(files),
         "bytes_total":sum(x["bytes"] for x in files),
         "top_level_usage":dict(sorted(by_top.items())),
         "largest_files":sorted(files,key=lambda x:x["bytes"],reverse=True)[:20],
         "symlinks":links,"progress":progress,"kira_executed_by_inventory":False,
         "resume_validated":False,"safe_to_resume":False,
         "next_step":"Review runtime artifacts before designing a separately isolated follow-up; do not reuse existing run directory."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_EXPERIMENT_INVENTORY "+json.dumps(report,ensure_ascii=False),flush=True)
 if failed or errors:raise SystemExit(2)

if __name__=="__main__":main()
