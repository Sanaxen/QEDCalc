"""Inspect original Kira result metadata for mappings of small SYSTEM IDs.

Read-only, bounded search; no inference from list positions. Record snippets
from masters, tables, and solver result files that contain index references.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_master_reference_inventory.json"))
 ap.add_argument("--max-bytes",type=int,default=5_000_000)
 a=ap.parse_args()
 roots=[a.project/"results",a.project/"config"]
 paths=[]
 for root in roots:
  if root.is_dir():
   paths.extend(x for x in root.rglob("*") if x.is_file())
 details=[]
 for path in sorted(paths):
  rel=str(path.relative_to(a.project))
  entry={"path":rel,"bytes":path.stat().st_size}
  if path.stat().st_size<=a.max_bytes and path.suffix.lower() not in (".db",".gz",".zip",".pdf",".png",".jpg"):
   try:
    s=path.read_text(encoding="utf-8-sig")
    lines=s.splitlines()
    matched=[{"line":n,"text":line.strip()[:280]} for n,line in enumerate(lines,1)
      if re.search(r"(master|reference|weight|sector|integral|\b(201|203)\b)",line,re.I)]
    entry["head"]=lines[:4]
    entry["matches"]=matched[:25]
    entry["match_count"]=len(matched)
   except (UnicodeError,OSError) as e:entry["read_error"]=str(e)
  details.append(entry)
 report={"status":"KIRA_REFERENCE_INVENTORY_ONLY","scanned_files":len(paths),
   "files":details,"target_keys":[[10,203],[6,203],[5,201]],
   "physical_mapping_verified":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_MASTER_REFERENCE_INVENTORY "+json.dumps({"status":report["status"],
   "scanned_files":len(paths),
   "files":[{"path":x["path"],"bytes":x["bytes"],"head":x.get("head",[])[:3],
      "matches":x.get("matches",[])[:4]} for x in details],
   "output":str(a.output),"physical_mapping_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
