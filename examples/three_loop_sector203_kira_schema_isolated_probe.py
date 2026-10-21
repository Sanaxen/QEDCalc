"""Isolated, bounded Kira 3.1 full-stage syntax probe, never a VP05 reduction."""
from __future__ import annotations
import argparse, json, os, resource, shutil, signal, subprocess, tempfile, time
from pathlib import Path

GIB=1024**3
KIN="""kinematics:
  outgoing_momenta: [p]
  kinematic_invariants:
    - [m2, 2]
  scalarproduct_rules:
    - [[p,p], "m2"]
  symbol_to_replace_by_one: m2
"""
FAMILY="""integralfamilies:
  - name: "schema_probe"
    loop_momenta: [k]
    top_level_sectors: [3]
    propagators:
      - ["k", "m2"]
      - ["k-p", "m2"]
"""
JOB="""jobs:
  - reduce_sectors:
      reduce:
        - {topologies: [schema_probe], sectors: [3], r: 2, s: 0, d: 0}
      select_integrals:
        select_mandatory_recursively:
          - {topologies: [schema_probe], sectors: [3], r: 2, s: 0, d: 0}
      run_symmetries: true
      run_initiate: true
      run_triangular: true
      run_back_substitution: true
      run_firefly: false
"""

def memory():
    d={}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if ":" in line:
            k,v=line.split(":",1)
            t=v.split()
            if t and t[0].isdigit(): d[k]=int(t[0])*1024
    return d

def limits():
    resource.setrlimit(resource.RLIMIT_AS,(2*GIB,2*GIB))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))

def terminate(proc):
    if proc.poll() is not None: return
    try: os.killpg(proc.pid,signal.SIGTERM)
    except ProcessLookupError: return
    try: proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try: os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        proc.wait(timeout=3)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--max-seconds",type=int,default=15)
    p.add_argument("--min-mem-available-gib",type=float,default=4)
    p.add_argument("--max-swap-used-gib",type=float,default=12)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kira_schema_isolated_probe.json"))
    a=p.parse_args()
    if os.name!="posix" or not 5<=a.max_seconds<=30 or a.min_mem_available_gib<2 or a.max_swap_used_gib<=0:
        p.error("WSL/Linux and bounded safety limits required")
    exe=shutil.which("kira")
    report={"status":"BLOCKED","kira_executable":exe,"original_project_opened":False,
            "vp05_equations_used":False,"physical_vp05_reduction_executed":False,
            "schema_validated_by_kira":False,"ready_to_execute_vp05":False}
    proc=None
    try:
        m=memory()
        if not exe or not Path(exe).is_file():
            report["reason"]="KIRA_NOT_FOUND"
        elif m.get("MemAvailable",0)<=a.min_mem_available_gib*GIB or (m.get("SwapTotal",0)-m.get("SwapFree",0))>=a.max_swap_used_gib*GIB:
            report["reason"]="RESOURCE_PREFLIGHT_FAILED"
        else:
            with tempfile.TemporaryDirectory(prefix="qedcalc_kira31_schema_",dir="/tmp") as d:
                root=Path(d)
                (root/"config").mkdir()
                (root/"config"/"kinematics.yaml").write_text(KIN)
                (root/"config"/"integralfamilies.yaml").write_text(FAMILY)
                (root/"jobs.yaml").write_text(JOB)
                proc=subprocess.Popen([str(Path(exe).resolve()),"--parallel=1","jobs.yaml"],cwd=root,
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,
                    start_new_session=True,preexec_fn=limits)
                # Use file logging to avoid pipe-buffer deadlock.
                # The fixture is tiny; drain via communicate with a bounded timeout.
                deadline=time.monotonic()+a.max_seconds
                reason=None
                while proc.poll() is None:
                    m=memory()
                    if m.get("MemAvailable",0)<=a.min_mem_available_gib*GIB: reason="RAM_FLOOR";break
                    if (m.get("SwapTotal",0)-m.get("SwapFree",0))>=a.max_swap_used_gib*GIB: reason="SWAP_CEILING";break
                    if time.monotonic()>=deadline: reason="TIME_CEILING";break
                    time.sleep(.2)
                if reason: terminate(proc)
                out=(proc.communicate(timeout=3)[0] or b"").decode("utf-8","replace")[-12000:]
                report.update({"kira_executed":True,"returncode":proc.returncode,
                    "stop_reason":reason,"stdout_tail":out[-6000:],
                    "status":"ISOLATED_KIRA_JOB_COMPLETED" if reason is None and proc.returncode==0 else "ISOLATED_KIRA_JOB_INCOMPLETE",
                    "schema_validated_by_kira":reason is None and proc.returncode==0,
                    "process_reaped":proc.poll() is not None})
                # A successful artificial job proves only this minimal schema, not the VP05 job.
    except Exception as e:
        report.update({"status":"PROBE_ERROR","error":repr(e)})
    finally:
        if proc is not None: terminate(proc)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        print("VP05_KIRA_SCHEMA_ISOLATED_PROBE "+json.dumps(report,ensure_ascii=False),flush=True)
    if not report["schema_validated_by_kira"]: raise SystemExit(2)
if __name__=="__main__":main()
