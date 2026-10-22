"""Read-only scan of VP05 saved sector202 Kira SYSTEM gzip equations.

Parse saved files with the existing equation inventory parser. Do not claim
physical target coverage until Kira ID mapping has been independently checked.
"""
from __future__ import annotations
import json
from pathlib import Path
from examples.three_loop_sector203_system_inventory import inspect
ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/"output"
def main():
 rows=[]
 for project in sorted(OUTPUT.glob("kira_vp05*")):
  if not project.is_dir() or project.is_symlink():continue
  p=project/"tmp"/"VP05_full"/"SYSTEM_VP05_full_202.gz"
  if not p.is_file() or p.is_symlink():continue
  try:
   data=inspect(p)
   rows.append({"project":str(project),"path":str(p),
     "compressed_bytes":data["compressed_bytes"],
     "equations":data["equations"],"terms":data["terms"],
     "unique_internal_ids":data["unique_internal_ids"],
     "term_sector_distribution":data["term_sector_distribution"],
     "parse_errors":data["parse_errors"],"sample_equations":data["sample_equations"]})
  except Exception as exc:
   rows.append({"project":str(project),"path":str(p),
    "parse_failure":type(exc).__name__+": "+str(exc)[:250]})
 report={"status":"VP05_SAVED_SECTOR202_SYSTEM_CONTENT_INVENTORY",
  "system_file_count":len(rows),"files":rows,
  "has_any_parsed_equations":any(r.get("equations",0)>0 and not r.get("parse_errors") for r in rows),
  "target_physical_id_mapping_verified":False,
  "proves_two_target_coefficient_reconstruction":False,
  "next_step":"Map target exponent IDs to Kira internal identifiers and establish target rowspace in a suitable saved SYSTEM set.",
  "kira_executed":False,"files_modified":False}
 print("VP05_SAVED_SECTOR202_SYSTEM_CONTENT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
