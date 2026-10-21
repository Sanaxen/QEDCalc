"""Real-Kira monitor smoke: isolated toy job, normal exit and forced stop only."""
from __future__ import annotations
import argparse,json,os,resource,shutil,signal,subprocess,tempfile,time
from pathlib import Path
from examples.three_loop_sector203_kira_schema_isolated_probe import FAMILY,JOB,KIN,GIB,find_fermat,memory
from examples.three_loop_sector203_full_stage_guarded_run import cleanup_group

def resource_alarm(floor,ceil):
 d=memory()
 if d.get("MemAvailable",0)<=floor*GIB:return "ram_floor"
 if (d.get("SwapTotal",0)-d.get("SwapFree",0))>=ceil*GIB:return "swap_ceiling"
 return None

def exercise(kira,fermat,root,name,force,seconds,floor,ceil):
 work=root/name
 (work/"config").mkdir(parents=True)
 for rel,body in (("config/kinematics.yaml",KIN),("config/integralfamilies.yaml",FAMILY),("jobs.yaml",JOB)):
  (work/rel).write_text(body,encoding="utf-8")
 env=os.environ.copy();env["FERMATPATH"]=fermat
 def limits():
  resource.setrlimit(resource.RLIMIT_AS,(2*GIB,2*GIB))
  resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 logpath=work/"kira.log"
 with logpath.open("wb") as stream:
  proc=subprocess.Popen([kira,"--parallel=1","jobs.yaml"],cwd=work,env=env,
   stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,
   start_new_session=True,preexec_fn=limits)
 reason=None;start=time.monotonic();samples=0
 try:
  if force:
   try:os.kill(proc.pid,signal.SIGSTOP)
   except ProcessLookupError:reason="early_exit"
  while reason is None:
   samples+=1
   reason=resource_alarm(floor,ceil)
   if reason:break
   if not force and proc.poll() is not None:reason="completed";break
   if time.monotonic()-start>=seconds:reason="time_ceiling";break
   time.sleep(.1)
  if reason=="completed":proc.wait(timeout=3)
 finally:cleanup=cleanup_group(proc)
 output=logpath.read_bytes()[-3500:].decode("utf-8","replace")
 return {"case":name,"reason":reason,"returncode":proc.returncode,"samples":samples,
  **cleanup,
  "toy_reduction_finished":reason=="completed" and proc.returncode==0 and "Back substitution" in output,
  "stdout_tail":output[-1600:]}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
 p.add_argument("--normal-max-seconds",type=float,default=15)
 p.add_argument("--forced-stop-seconds",type=float,default=1)
 p.add_argument("--min-mem-available-gib",type=float,default=4)
 p.add_argument("--max-swap-used-gib",type=float,default=12)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kira_monitor_smoke.json"))
 a=p.parse_args()
 if os.name!="posix" or not 5<=a.normal_max_seconds<=30 or not .5<=a.forced_stop_seconds<=5 or a.min_mem_available_gib<2 or a.max_swap_used_gib<=0:p.error("unsafe limits")
 kira=shutil.which("kira");fermat=find_fermat(a.fermat)
 report={"status":"BLOCKED","kira_executable":kira,"fermat_executable":fermat,
  "original_project_opened":False,"vp05_equations_used":False,
  "physical_vp05_reduction_executed":False,"ready_to_execute_vp05":False,"cases":[]}
 try:
  if not kira or not fermat:report["reason"]="EXECUTABLE_MISSING"
  elif resource_alarm(a.min_mem_available_gib,a.max_swap_used_gib):report["reason"]="RESOURCE_PREFLIGHT_FAILED"
  else:
   with tempfile.TemporaryDirectory(prefix="qedcalc_real_kira_guard_",dir="/tmp") as td:
    root=Path(td)
    normal=exercise(str(Path(kira).resolve()),fermat,root,"normal",False,a.normal_max_seconds,a.min_mem_available_gib,a.max_swap_used_gib)
    report["cases"].append(normal)
    if normal["toy_reduction_finished"] and normal["process_group_gone"] and normal["process_reaped"] and not normal["members_after_cleanup"]:
     forced=exercise(str(Path(kira).resolve()),fermat,root,"forced",True,a.forced_stop_seconds,a.min_mem_available_gib,a.max_swap_used_gib)
     report["cases"].append(forced)
     report["status"]="PASS_REAL_KIRA_MONITOR_SMOKE" if forced["reason"]=="time_ceiling" and forced["process_reaped"] and forced["process_group_gone"] and not forced["members_after_cleanup"] else "FORCED_STOP_NOT_VERIFIED"
    else:report["status"]="NORMAL_KIRA_CASE_FAILED"
 except Exception as exc:report["status"]="MONITOR_SMOKE_ERROR";report["error"]=repr(exc)
 finally:
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  print("VP05_KIRA_MONITOR_SMOKE "+json.dumps(report,ensure_ascii=False),flush=True)
 if report["status"]!="PASS_REAL_KIRA_MONITOR_SMOKE":raise SystemExit(2)
if __name__=="__main__":main()
