"""Read-only Kira project execution/artifact audit for VP05 physical-target gaps.

Inspects actual project artifacts and timestamps. No execution of Kira.
Timestamps and directory names are circumstantial, not evidence of completion.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

KEYWORDS=("symmetr","mapping","identit","replac","master","seed","initi","sector",
          "generate","reduce","job","log","stdout","stderr","status","input","output")
def stamp(n):
 return datetime.fromtimestamp(n,timezone.utc).isoformat()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--max-files",type=int,default=3000)
 p.add_argument("--max-text-bytes",type=int,default=200000)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_execution_symmetry_evidence.json"))
 a=p.parse_args()
 if not a.project.is_dir():p.error("Project directory missing")
 entries=[];candidates=[]
 for n,path in enumerate(sorted(a.project.rglob("*"))):
  if n>=a.max_files:break
  if not path.is_file():continue
  rel=str(path.relative_to(a.project));size=path.stat().st_size
  item={"path":rel,"bytes":size,"modified_utc":stamp(path.stat().st_mtime)}
  entries.append(item)
  if any(k in rel.lower() for k in KEYWORDS) or path.suffix.lower() in (".log",".yaml",".yml"):
   record=item.copy()
   if size<=a.max_text_bytes and path.suffix.lower() not in (".gz",".db",".sqlite",".zip",".png",".jpg"):
    try:
     lines=path.read_text(encoding="utf-8-sig").splitlines()
     hits=[{"line":i,"text":line.strip()[:250]} for i,line in enumerate(lines,1)
      if re.search(r"symmetr|identit|mandator|initi|triang|firefly|master|reduce|seed|truncate|select_integrals",line,re.I)]
     record["head"]=lines[:5]
     record["relevant_lines"]=hits[:20]
    except (UnicodeError,OSError) as err:record["error"]=str(err)
   candidates.append(record)
 statuses=[]
 for rel in ("provisional64_sector203_preflight.json","qedcalc_master_basis_manifest.json"):
  f=a.project/rel
  if f.is_file():
   try:
    data=json.loads(f.read_text(encoding="utf-8-sig"))
    statuses.append({"file":rel,"status":data.get("status"),"stage":data.get("stage"),
       "execution":data.get("execution")})
   except (UnicodeError,ValueError) as err:statuses.append({"file":rel,"error":str(err)})
 report={"status":"EXECUTION_AND_SYMMETRY_EVIDENCE_ONLY",
  "project":str(a.project),"scanned_files":len(entries),"scan_truncated":len(entries)>=a.max_files,
  "candidates":candidates,"status_metadata":statuses,
  "conclusion":"Presence of saved SYSTEM files proves they exist, not when/which job flags generated them; no target canonicalization has been verified.",
  "physical_target_mapping_verified":False,"regeneration_authorized":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_EXECUTION_SYMMETRY_EVIDENCE "+json.dumps({
  "status":report["status"],"scanned_files":len(entries),"scan_truncated":report["scan_truncated"],
  "candidates":[{"path":x["path"],"bytes":x["bytes"],"relevant_lines":x.get("relevant_lines",[])[:3]} for x in candidates],
  "status_metadata":statuses,"output":str(a.output),
  "physical_target_mapping_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
