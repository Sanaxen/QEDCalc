"""Bounded POSIX process-group termination smoke test; NEVER starts Kira.

This tests host process-group signaling on WSL/Linux, NOT the Kira monitor
itself or its swap/time decision logic. Timeout controls cleanup.
"""
from __future__ import annotations
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path

def alive(pid):
 try:
  os.kill(pid,0)
  return True
 except ProcessLookupError:return False

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_process_group_stop_smoke.json"))
 a=ap.parse_args()
 if os.name!="posix":ap.error("Run in WSL/Linux; never run from native Windows Python")
 script="import time; time.sleep(60)"
 proc=None;report={"status":"FAIL","kira_executed":False,"actual_monitor_tested":False,
   "smoke_test_only":True}
 try:
  proc=subprocess.Popen([sys.executable,"-c",script],start_new_session=True,
                         stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  report["dummy_pid"]=proc.pid
  time.sleep(0.2)
  report["dummy_started"]=proc.poll() is None
  if not report["dummy_started"]:raise RuntimeError("Dummy process exited early")
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:
   os.killpg(proc.pid,signal.SIGKILL)
   proc.wait(timeout=3)
   report["required_SIGKILL"]=True
  report["dummy_reaped"]=proc.poll() is not None
  report["status"]="PASS_DUMMY_PROCESS_GROUP_STOP" if report["dummy_reaped"] else "FAIL"
 except (OSError,RuntimeError,subprocess.TimeoutExpired) as e:
  report["error"]=str(e)
 finally:
  if proc is not None and proc.poll() is None:
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:pass
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_PROCESS_GROUP_STOP_SMOKE "+json.dumps(report),flush=True)
 if report["status"]!="PASS_DUMMY_PROCESS_GROUP_STOP":raise SystemExit(2)
if __name__=="__main__":main()
