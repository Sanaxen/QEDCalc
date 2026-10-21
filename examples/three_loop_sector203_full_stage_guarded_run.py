"""VP05 guarded experiment wrapper. Default dry-run; no Kira execution.

Execution requires --execute-vp05 and an exact acknowledgement. A new output
directory is created exclusively; the verified capsule remains untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,os,resource,shutil,signal,subprocess,time
from pathlib import Path
from examples.three_loop_sector203_kira_schema_isolated_probe import find_fermat,memory,GIB
CAPSULE=Path("output/vp05_full_stage_execution_capsule")
FILES=("config/integralfamilies.yaml","config/kinematics.yaml","mandatory_single_nonmaster.txt","preferred_provisional64_sector203.txt","jobs.yaml")
TARGET=(1,1,0,1,0,0,1,1,0,0,0,0)

def parse_one_target(path):
 import re
 lines=[line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip() and not line.lstrip().startswith("#")]
 if len(lines)!=1:return False
 m=re.fullmatch(r"VP05_full\[([+-]?\d+(?:\s*,\s*[+-]?\d+){11})\]",lines[0])
 return bool(m and tuple(int(x.strip()) for x in m.group(1).split(","))==TARGET)

ACK="EXECUTE_ISOLATED_VP05_SINGLE_TARGET"
AUDIT=Path("output/three_loop_integral_family_audit")
DEST=Path("output/vp05_full_stage_kira_experiment")

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def resources(floor,swap_limit):
 m=memory()
 if m.get("MemAvailable",0)<=floor*GIB:return "ram_floor"
 if (m.get("SwapTotal",0)-m.get("SwapFree",0))>=swap_limit*GIB:return "swap_ceiling"
 return None
def group_members(pgid):
 """Live /proc members, excluding zombies; conservative on read errors."""
 members=[]
 for entry in Path("/proc").iterdir():
  if not entry.name.isdigit():continue
  try:
   content=(entry/"stat").read_text()
   tail=content[content.rfind(")")+2:].split()
   if len(tail)>=3 and int(tail[2])==pgid and tail[0] not in ("Z","X"):
    members.append(int(entry.name))
  except (FileNotFoundError,ProcessLookupError):continue
  except (OSError,ValueError,IndexError):
   members.append(-1)
 return sorted(set(members))

def cleanup_group(proc):
 """Reap leader, terminate all surviving group members even if leader exited."""
 pgid=proc.pid
 before=group_members(pgid)
 sent=[]
 def sig(kind):
  try:
   os.killpg(pgid,kind)
   sent.append(signal.Signals(kind).name)
  except ProcessLookupError:pass
 if before:
  sig(signal.SIGTERM)
  until=time.monotonic()+2.0
  while group_members(pgid) and time.monotonic()<until:time.sleep(.1)
  if group_members(pgid):
   sig(signal.SIGKILL)
 try:proc.wait(timeout=3)
 except subprocess.TimeoutExpired:
  sig(signal.SIGKILL)
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:pass
 remaining=group_members(pgid)
 return {"group_id":pgid,"members_before_cleanup":before,
         "signals_sent":sent,"members_after_cleanup":remaining,
         "process_reaped":proc.poll() is not None,
         "process_group_gone":not remaining}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--execute-vp05",action="store_true")
 p.add_argument("--acknowledge",default="")
 p.add_argument("--max-seconds",type=int,default=30)
 p.add_argument("--min-mem-available-gib",type=float,default=4)
 p.add_argument("--max-swap-used-gib",type=float,default=12)
 p.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
 p.add_argument("--output",type=Path,default=AUDIT/"vp05_full_stage_guarded_run.json")
 a=p.parse_args()
 if not 10<=a.max_seconds<=120 or a.min_mem_available_gib<2 or a.max_swap_used_gib<=0:p.error("unsafe limits")
 report={"status":"DRY_RUN_NOT_EXECUTED","kira_executed":False,"physical_vp05_reduction_executed":False,
         "ready_to_execute":False,"destination":str(DEST.resolve()),"checks":{},
         "limits":{"max_seconds":a.max_seconds,"min_mem_available_gib":a.min_mem_available_gib,
                   "max_swap_used_gib":a.max_swap_used_gib,"address_space_gib":2,"parallel":1}}
 check=report["checks"]
 pre=AUDIT/"vp05_full_stage_execution_guard_preflight.json"
 check["preflight_pass"]=pre.is_file() and json.loads(pre.read_text(encoding="utf-8-sig")).get("status")=="EXECUTION_GUARD_PREFLIGHT_PASS_NO_KIRA"
 check["capsule_exists"]=CAPSULE.is_dir()
 check["destination_absent"]=not DEST.exists() and not DEST.is_symlink()
 manifest=CAPSULE/"CAPSULE_REVIEW_ONLY.json"
 data=json.loads(manifest.read_text(encoding="utf-8-sig")) if manifest.is_file() else {}
 check["manifest_status"]=data.get("status")=="CAPSULE_CREATED_NOT_EXECUTED"
 hashes=data.get("files_sha256",{})
 check["hashes_match"]=isinstance(hashes,dict) and set(hashes)==set(FILES) and all(
  (CAPSULE/f).is_file() and not (CAPSULE/f).is_symlink() and digest(CAPSULE/f)==hashes[f] for f in FILES)
 check["target_exact"]=(CAPSULE/"mandatory_single_nonmaster.txt").is_file() and parse_one_target(CAPSULE/"mandatory_single_nonmaster.txt")
 check["disk_free_20_gib"]=shutil.disk_usage(Path("output")).free>=20*GIB
 check["memory_safe"]=resources(a.min_mem_available_gib,a.max_swap_used_gib) is None
 kira=shutil.which("kira");fermat=find_fermat(a.fermat)
 check["executables_present"]=bool(kira and fermat)
 check["acknowledged"]=a.acknowledge==ACK
 report["kira_executable"]=kira;report["fermat_executable"]=fermat
 if not a.execute_vp05:
  report["status"]="GUARDED_VP05_DRY_RUN_PASS" if all(v for k,v in check.items() if k!="acknowledged") else "GUARDED_VP05_DRY_RUN_BLOCKED"
 elif not all(check.values()):
  report["status"]="GUARDED_VP05_EXECUTION_BLOCKED"
 else:
  proc=None
  try:
   DEST.mkdir(parents=True,exist_ok=False)
   for f in FILES:
    out=DEST/f;out.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(CAPSULE/f,out)
    if digest(out)!=hashes[f]:raise RuntimeError("copy hash mismatch: "+f)
   def limits():
    resource.setrlimit(resource.RLIMIT_AS,(2*GIB,2*GIB))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
   env=os.environ.copy();env["FERMATPATH"]=fermat
   log=DEST/"kira_run.log"
   with log.open("wb") as stream:
    proc=subprocess.Popen([str(Path(kira).resolve()),"--parallel=1","jobs.yaml"],cwd=DEST,env=env,
     stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
   report["kira_executed"]=True;report["physical_vp05_reduction_executed"]=True
   deadline=time.monotonic()+a.max_seconds
   reason=None
   while proc.poll() is None:
    reason=resources(a.min_mem_available_gib,a.max_swap_used_gib)
    if reason:break
    if time.monotonic()>=deadline:reason="time_ceiling";break
    time.sleep(.2)
   report["stop_reason"]=reason
   report["returncode"]=proc.poll()
   report["log_tail"]=log.read_bytes()[-4000:].decode("utf-8","replace")
   report["status"]="KIRA_FINISHED_PENDING_CLEANUP"
  except BaseException as exc:
   report["status"]="GUARDED_VP05_EXCEPTION";report["error"]=repr(exc)
  finally:
   if proc is not None:
    final_cleanup=cleanup_group(proc)
    report.update(final_cleanup)
    report["returncode"]=proc.poll()
    if not final_cleanup["process_group_gone"] or not final_cleanup["process_reaped"]:
     report["status"]="KIRA_PROCESS_CLEANUP_FAILED"
    elif report["status"]=="KIRA_FINISHED_PENDING_CLEANUP":
     report["status"]="KIRA_COMPLETED_REQUIRES_RESULT_AUDIT" if proc.returncode==0 and report["stop_reason"] is None else "KIRA_STOPPED_OR_FAILED"
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_FULL_STAGE_GUARDED_RUN "+json.dumps(report,ensure_ascii=False),flush=True)
 if report["status"] not in ("GUARDED_VP05_DRY_RUN_PASS","KIRA_COMPLETED_REQUIRES_RESULT_AUDIT"):raise SystemExit(2)
if __name__=="__main__":main()
