"""Bounded RAM+swap monitor for a disposable subprocess in WSL/Linux.

Default mode is dry-run, NO subprocess. --smoke-test starts ONLY an
independent sleeping Python dummy; never invokes Kira or touches Kira files.
"""
from __future__ import annotations
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path

def mem():
 d={}
 for line in Path("/proc/meminfo").read_text().splitlines():
  if ":" in line:
   k,v=line.split(":",1);part=v.split()
   if part and part[0].isdigit():d[k]=int(part[0])*1024
 return d
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--smoke-test",action="store_true")
 p.add_argument("--min-mem-available-gib",type=float,default=4)
 p.add_argument("--max-swap-used-gib",type=float,default=12)
 p.add_argument("--max-seconds",type=int,default=10)
 p.add_argument("--interval",type=float,default=0.2)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_ram_swap_guard_smoke.json"))
 a=p.parse_args()
 if os.name!="posix":p.error("Requires WSL/Linux")
 if a.min_mem_available_gib<=0 or a.max_swap_used_gib<=0 or not 2<=a.max_seconds<=60 or not .1<=a.interval<=5:
  p.error("unsafe limits")
 g=1024**3;initial=mem()
 checks={"available_ram_above_floor":initial.get("MemAvailable",0)/g>a.min_mem_available_gib,
  "swap_used_below_stop":(initial.get("SwapTotal",0)-initial.get("SwapFree",0))/g<a.max_swap_used_gib}
 report={"status":"DRY_RUN_ONLY" if not a.smoke_test else "FAIL","checks":checks,"kira_executed":False,
  "actual_kira_monitor_tested":False,"ram_and_swap_policy_tested":False}
 if a.smoke_test and all(checks.values()):
  proc=None
  try:
   proc=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],start_new_session=True)
   start=time.monotonic();reason=None
   while proc.poll() is None:
    m=mem()
    if m.get("MemAvailable",0)/g<=a.min_mem_available_gib:reason="ram_floor";break
    if (m.get("SwapTotal",0)-m.get("SwapFree",0))/g>=a.max_swap_used_gib:reason="swap_ceiling";break
    if time.monotonic()-start>=a.max_seconds:reason="time_ceiling";break
    time.sleep(a.interval)
   if reason:
    os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
     os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=2)
   report.update({"status":"PASS_DUMMY_RAM_SWAP_GUARD" if reason=="time_ceiling" and proc.poll() is not None else "FAIL",
       "stop_reason":reason,"dummy_reaped":proc.poll() is not None,"ram_and_swap_policy_tested":True})
  finally:
   if proc is not None and proc.poll() is None:
    try:os.killpg(proc.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    proc.wait(timeout=3)
 elif a.smoke_test:report["status"]="BLOCKED_UNSAFE_INITIAL_RESOURCES"
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_RAM_SWAP_GUARD_SMOKE "+json.dumps(report),flush=True)
 if a.smoke_test and report["status"]!="PASS_DUMMY_RAM_SWAP_GUARD":raise SystemExit(2)
if __name__=="__main__":main()
