"""Bounded overnight controller for the existing VP05 sector202 step51 scratch.

Runs only on the user's Windows/WSL2 machine; never executes Kira/FireFly.
Before every coefficient, fail-closed monitor Windows/WSL available RAM,
WSL swap usage, and local disk space. Every coefficient is persisted by
the existing scratch runner, never by this controller.
"""
from __future__ import annotations
import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from examples.three_loop_vp05_sector202_target_exact_reduction import BASE
from examples.three_loop_vp05_sector202_step51_scratch import SCRATCH, STATE
GIB=1024**3

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_=[
        ("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
        ("ullTotalPhys",ctypes.c_ulonglong),
        ("ullAvailPhys",ctypes.c_ulonglong),
        ("ullTotalPageFile",ctypes.c_ulonglong),
        ("ullAvailPageFile",ctypes.c_ulonglong),
        ("ullTotalVirtual",ctypes.c_ulonglong),
        ("ullAvailVirtual",ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual",ctypes.c_ulonglong),
    ]

def windows_available_bytes():
    if sys.platform!="win32":
        raise RuntimeError("This guarded overnight controller requires Windows")
    value=MEMORYSTATUSEX()
    value.dwLength=ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):
        raise OSError("Windows GlobalMemoryStatusEx failed")
    return int(value.ullAvailPhys)

def parse_free(output):
    rows={}
    for line in output.splitlines():
        pieces=line.split()
        if pieces and pieces[0].rstrip(":") in ("Mem","Swap"):
            if len(pieces)<4:
                raise ValueError("Unexpected WSL free output row")
            rows[pieces[0].rstrip(":")]=pieces
    if "Mem" not in rows or "Swap" not in rows or len(rows["Mem"])<7:
        raise ValueError("Missing WSL memory/swap readings")
    return {"wsl_mem_available_bytes":int(rows["Mem"][6]),
            "wsl_swap_total_bytes":int(rows["Swap"][1]),
            "wsl_swap_used_bytes":int(rows["Swap"][2]),
            "wsl_swap_free_bytes":int(rows["Swap"][3])}

def wsl_memory():
    result=subprocess.run(["wsl.exe","-e","free","-b"],
                          capture_output=True,text=True,timeout=20,check=True)
    return parse_free(result.stdout)

def resource_snapshot(args):
    memory=wsl_memory()
    memory["windows_mem_available_bytes"]=windows_available_bytes()
    memory["disk_free_bytes"]=shutil.disk_usage(args.scratch.resolve().parent).free
    return memory

def unsafe(snapshot,args):
    constraints=(
        ("windows_low_ram",snapshot["windows_mem_available_bytes"]<args.min_windows_ram_gib*GIB),
        ("wsl_low_ram",snapshot["wsl_mem_available_bytes"]<args.min_wsl_ram_gib*GIB),
        ("swap_used_high",snapshot["wsl_swap_used_bytes"]>args.max_swap_used_gib*GIB),
        ("swap_free_low",snapshot["wsl_swap_free_bytes"]<args.min_swap_free_gib*GIB),
        ("disk_free_low",snapshot["disk_free_bytes"]<args.min_disk_free_gib*GIB),
    )
    return [key for key,triggered in constraints if triggered]

def progress_from_output(output):
    matches=[]
    for line in output.splitlines():
        if line.startswith("VP05_SECTOR202_STEP51_SCRATCH_RESULT "):
            matches.append(json.loads(line.split(" ",1)[1]))
    if len(matches)!=1:
        raise RuntimeError("Expected one scratch result line, got "+str(len(matches)))
    return matches[0]

def write_event(handle,event,data):
    msg={"event":event,"timestamp_utc":__import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat(),**data}
    handle.write(json.dumps(msg,ensure_ascii=True)+"\n")
    handle.flush()
    os.fsync(handle.fileno())
    print("VP05_STEP51_OVERNIGHT "+json.dumps(msg,ensure_ascii=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scratch",type=Path,default=SCRATCH)
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--hours",type=float,default=12.0)
    ap.add_argument("--timeout-seconds",type=int,default=90,
                    help="Per coefficient computation time cap (1..120s)")
    ap.add_argument("--min-windows-ram-gib",type=float,default=2.0)
    ap.add_argument("--min-wsl-ram-gib",type=float,default=1.5)
    ap.add_argument("--max-swap-used-gib",type=float,default=190.0)
    ap.add_argument("--min-swap-free-gib",type=float,default=20.0)
    ap.add_argument("--min-disk-free-gib",type=float,default=15.0)
    ap.add_argument("--max-coefficients",type=int,default=288)
    ap.add_argument("--log",type=Path,default=BASE/"vp05_sector202_step51_overnight.jsonl")
    args=ap.parse_args()
    if not 0<args.hours<=12 or not 1<=args.timeout_seconds<=120:
        ap.error("Hours must be 0..12 and coefficient timeout 1..120")
    if not 1<=args.max_coefficients<=288 or min(
        args.min_windows_ram_gib,args.min_wsl_ram_gib,
        args.max_swap_used_gib,args.min_swap_free_gib,args.min_disk_free_gib)<=0:
        ap.error("Invalid resource safety bounds")
    if not args.scratch.exists() or not args.state.exists():
        ap.error("Target state and existing scratch are required")
    if args.log.resolve() in {args.scratch.resolve(),args.state.resolve()}:
        ap.error("Log cannot overwrite target/scratch")
    args.log.parent.mkdir(parents=True,exist_ok=True)
    deadline=time.monotonic()+args.hours*3600
    completed=0
    stop_reason="HOURS_CEILING"
    with args.log.open("x",encoding="utf-8") as handle:
        write_event(handle,"START",{"hours_ceiling":args.hours,
                    "coefficient_timeout_seconds":args.timeout_seconds,
                    "max_coefficients":args.max_coefficients,
                    "formal_target_state_modified":False})
        try:
            for _ in range(args.max_coefficients):
                remaining=deadline-time.monotonic()
                if remaining<180:
                    stop_reason="TIME_BUDGET_LOW"
                    break
                try:
                    snapshot=resource_snapshot(args)
                except Exception as ex:
                    stop_reason="RESOURCE_MONITOR_UNAVAILABLE"
                    write_event(handle,"RESOURCE_CHECK_FAILED",{"error":str(ex)[:300]})
                    break
                violations=unsafe(snapshot,args)
                write_event(handle,"RESOURCE_CHECK",
                            {**snapshot,"violations":violations})
                if violations:
                    stop_reason="RESOURCE_LIMIT"
                    break
                cmd=[sys.executable,"-m","examples.three_loop_vp05_sector202_step51_scratch",
                     "--resume","--scratch",str(args.scratch),
                     "--state",str(args.state),"--coefficients","1",
                     "--timeout-seconds",str(args.timeout_seconds)]
                try:
                    result=subprocess.run(cmd,capture_output=True,text=True,
                                          timeout=min(remaining,180),check=False)
                except subprocess.TimeoutExpired:
                    stop_reason="SCRATCH_RUN_TIMEOUT"
                    break
                write_event(handle,"COEFFICIENT_RUN",
                            {"returncode":result.returncode,
                             "stdout_tail":result.stdout[-1800:],
                             "stderr_tail":result.stderr[-350:]})
                if result.returncode:
                    stop_reason="SCRATCH_RUN_ERROR"
                    break
                try:
                    progress=progress_from_output(result.stdout)
                except (RuntimeError,ValueError,KeyError) as ex:
                    stop_reason="INVALID_SCRATCH_REPORT"
                    write_event(handle,"INVALID_REPORT",{"error":str(ex)})
                    break
                if progress["status"]!="INTRA_STEP51_SCRATCH_NOT_PROOF":
                    stop_reason="SCRATCH_STOP_"+str(progress["status"])
                    break
                if progress["coefficients_this_run"]!=1:
                    if progress["saved_coefficient_count"]==progress["total_coefficients"]:
                        stop_reason="ALL_SCRATCH_COEFFICIENTS_COMPLETE_NOT_PROOF"
                    else:
                        stop_reason="NO_PROGRESS"
                    break
                completed+=1
                if progress["saved_coefficient_count"]==progress["total_coefficients"]:
                    stop_reason="ALL_SCRATCH_COEFFICIENTS_COMPLETE_NOT_PROOF"
                    break
        except KeyboardInterrupt:
            stop_reason="USER_INTERRUPTED"
        write_event(handle,"STOP",{"reason":stop_reason,
                    "coefficients_completed_this_session":completed,
                    "formal_target_state_modified":False,
                    "exact_target_proven":False})
    if stop_reason in ("SCRATCH_RUN_ERROR","SCRATCH_RUN_TIMEOUT","INVALID_SCRATCH_REPORT",
                       "RESOURCE_MONITOR_UNAVAILABLE","RESOURCE_LIMIT","NO_PROGRESS"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
