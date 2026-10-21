"""Read-only VP05 Kira executable and environment inventory (WSL).
Never starts Kira, changes a project, or asserts jobs.yaml schema support.
"""
from __future__ import annotations
import argparse,json,os,shutil,subprocess
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kira_environment_inventory.json"))
 a=p.parse_args()
 if os.name!="posix":p.error("Requires WSL/Linux Python")
 kira=shutil.which("kira")
 candidates=[kira, "/usr/local/bin/kira",str(Path.home()/"kira/build/bin/kira")]
 resolved=next((str(Path(x).resolve()) for x in candidates if x and Path(x).is_file() and os.access(x,os.X_OK)),None)
 report={"status":"EXECUTABLE_FOUND_SCHEMA_UNVERIFIED" if resolved else "KIRA_EXECUTABLE_NOT_FOUND",
  "path_lookup":kira,"executable_path":resolved,
  "wsl_distro":os.environ.get("WSL_DISTRO_NAME"),
  "version_verified":False,"schema_validated_by_kira":False,
  "kira_executed":False,"ready_to_execute":False,
  "next_requirement":"Establish executable version and validate full-stage job schema in a separate controlled test, never using original project."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_KIRA_ENVIRONMENT "+json.dumps(report),flush=True)
if __name__=="__main__":main()
