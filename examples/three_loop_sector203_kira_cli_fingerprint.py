"""Kira CLI fingerprint only; no project/job invocation.

Kira --version/--help may be unsupported. Probe bounded and from a neutral
temporary directory, with no jobs.yaml and no Kira project present.
"""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--kira",default=None)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kira_cli_fingerprint.json"))
 a=p.parse_args()
 if os.name!="posix":p.error("WSL/Linux required")
 exe=a.kira or shutil.which("kira")
 result={"status":"KIRA_NOT_FOUND","executable":exe,"probes":[],
  "kira_project_opened":False,"physical_reduction_executed":False,
  "schema_validated_by_kira":False,"ready_to_execute":False}
 if exe and Path(exe).is_file() and os.access(exe,os.X_OK):
  result["status"]="CLI_FINGERPRINT_ONLY"
  with tempfile.TemporaryDirectory(prefix="qedcalc_kira_cli_probe_") as td:
   for arg in ("--version","--help"):
    try:
     res=subprocess.run([str(Path(exe).resolve()),arg],cwd=td,
      capture_output=True,text=True,errors="replace",timeout=5,check=False)
     result["probes"].append({"argument":arg,"returncode":res.returncode,
       "stdout":res.stdout[:2000],"stderr":res.stderr[:1000]})
    except subprocess.TimeoutExpired:
     result["probes"].append({"argument":arg,"status":"TIMEOUT_5_SECONDS"})
    except OSError as e:
     result["probes"].append({"argument":arg,"status":"ERROR","detail":str(e)})
 else:
  result["note"]="Pass --kira /absolute/path/to/kira if the WSL PATH does not expose it"
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_KIRA_CLI_FINGERPRINT "+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
