"""Read-only WSL resource preflight for a future guarded VP05 Kira run.

Never starts Kira, changes settings, or claims full reduction readiness.
WSL /proc/meminfo values are system-wide and not a reliable process limit.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path

def meminfo():
 data={}
 with open("/proc/meminfo",encoding="ascii") as f:
  for line in f:
   if ":" not in line:continue
   k,v=line.split(":",1)
   fields=v.split()
   if fields and fields[0].isdigit():
    data[k]=int(fields[0])*1024 if len(fields)>1 and fields[1]=="kB" else int(fields[0])
 return data

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--warn-gib",type=float,default=8)
 ap.add_argument("--stop-gib",type=float,default=12)
 ap.add_argument("--max-seconds",type=int,default=1800)
 ap.add_argument("--interval",type=int,default=5)
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_wsl_resource_preflight.json"))
 a=ap.parse_args()
 if os.name!="posix":ap.error("Run via WSL/Linux Python")
 m=meminfo();G=1024**3
 total=m.get("MemTotal",0)/G;available=m.get("MemAvailable",0)/G
 swap_total=m.get("SwapTotal",0)/G;swap_free=m.get("SwapFree",0)/G
 used=max(0,swap_total-swap_free)
 errors=[]
 if not (0<a.warn_gib<a.stop_gib<=240):errors.append("Invalid monitor swap thresholds")
 if not (10<=a.max_seconds<=86400):errors.append("A finite time limit from 10s to 24h is required")
 if not (1<=a.interval<=60):errors.append("Invalid sampling interval")
 if swap_total<=0:errors.append("No swap configured: swap threshold cannot protect RAM")
 if a.stop_gib>swap_total:errors.append("Swap stop threshold exceeds total available swap")
 if used>=a.stop_gib:errors.append("Swap already above stop threshold")
 report={"status":"RESOURCE_PREFLIGHT_PASS" if not errors else "RESOURCE_PREFLIGHT_BLOCKED",
  "mem_total_gib":round(total,3),"mem_available_gib":round(available,3),
  "swap_total_gib":round(swap_total,3),"swap_used_gib":round(used,3),
  "proposed_guard":{"warn_gib":a.warn_gib,"stop_gib":a.stop_gib,
   "max_seconds":a.max_seconds,"interval":a.interval},
  "errors":errors,"kira_executed":False,"monitor_process_tested":False,
  "physical_reduction_ready":False,
  "warning":"Swap control does not bound Kira resident RAM or cgroup memory; full execution requires dedicated RAM/cgroup review and Kira schema validation."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_WSL_RESOURCE_PREFLIGHT "+json.dumps(report),flush=True)
 if errors:raise SystemExit(2)
if __name__=="__main__":main()
