"""Read-only inventory of original VP05 sector202 Kira reduction evidence.

Enumerates original project and nearby sector202 project artifacts without
modifying files or treating a terminal classification as a coefficient proof.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PREFIX="kira_vp05_full_firefly_numerator_r8s3d0_r6s6d2_sec202"
def scan(root):
 if not root.is_dir():return {"exists":False}
 files=[]
 kinds={}
 for p in root.rglob("*"):
  if p.is_symlink():continue
  if not p.is_file():continue
  rel=p.relative_to(root).as_posix()
  # Aggregate even large repositories without opening or copying project files.
  suffix=p.suffix.lower()
  kinds[suffix]=kinds.get(suffix,0)+1
  if len(files)<120:
   files.append({"relative":rel,"bytes":p.stat().st_size})
 return {"exists":True,"files_count":sum(kinds.values()),"by_suffix":kinds,
         "sample_files":files,"sample_truncated":sum(kinds.values())>len(files),
         "has_system_equations":any(x["relative"].split("/")[-1].startswith("SYSTEM_") for x in files),
         "has_reduction_tables":any("kira" in x["relative"].lower() and x["relative"].endswith(".out") for x in files)}
def main():
 original=ROOT/"output"/PREFIX
 matches=sorted((ROOT/"output").glob("*sec202*"))
 rows=[{"project":str(p),"inventory":scan(p)} for p in matches if p.is_dir()]
 report={"status":"VP05_SECTOR202_SAVED_EQUATIONS_INVENTORY",
         "original_project":str(original),"original":scan(original),
         "related_project_count":len(rows),"related_projects":rows[:30],
         "read_only":True,"kira_executed":False,
         "warning":"Stored Kira master classification is NOT an explicit reduction coefficient relation."}
 print("VP05_SECTOR202_SAVED_EQUATIONS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
