"""Read-only global VP05 saved Kira equation file locator.

Find saved SYSTEM equation files in other VP05 projects without opening or
parsing their large contents. Candidate sector 202 presence in a filename is
not proof that specific mandatory targets can be reduced.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/"output"
def main():
 rows=[]
 examined=0
 for project in sorted(OUTPUT.glob("kira_vp05*")):
  if not project.is_dir() or project.is_symlink():continue
  examined+=1
  family=project/"tmp"/"VP05_full"
  if not family.is_dir():continue
  systems=[]
  for path in sorted(family.glob("SYSTEM_VP05_full_*")):
   if not path.is_file() or path.is_symlink():continue
   size=path.stat().st_size
   systems.append({"file":path.name,"bytes":size,
      "name_mentions_sector202":path.name.startswith("SYSTEM_VP05_full_202.")})
  if systems:
   rows.append({"project":str(project),"system_count":len(systems),
     "total_system_bytes":sum(v["bytes"] for v in systems),
     "system_202_files":[v for v in systems if v["name_mentions_sector202"]],
     "first_system_files":systems[:8]})
 report={"status":"VP05_GLOBAL_SAVED_SYSTEM_LOCATOR",
   "vp05_projects_examined":examined,
   "projects_with_systems":len(rows),"projects":rows,
   "note":"A SYSTEM_202 file is a potential evidence source, not a verified reduction of the two sector202 targets. Global IBP systems must be audited for integral-ID coverage and coefficient provenance.",
   "kira_executed":False,"file_contents_opened":False,"files_modified":False}
 print("VP05_GLOBAL_SAVED_SYSTEM "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
