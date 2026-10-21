"""Locate evidence for mapping VP05 certificate (weight,sector) columns to Kira integrals.

Read-only inventory. A sector/weight column is NOT an exponent tuple.
No identity is certified unless an explicit matching tuple occurs in
Kira-produced metadata (not inferred from weight and sector).
"""
from __future__ import annotations
import argparse,gzip,json,re
from pathlib import Path
from examples.three_loop_sector203_exact_528_target_replay import OUT as CERT

DEFAULT_PROJECT=Path("output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734")
TOKENS=("VP05_full","top_level_sectors","integral_families","integralfamilies","sector","masters","weight")
def find_lines(path,max_lines=120000,max_bytes=12_000_000):
 opener=gzip.open if path.suffix==".gz" else open
 hits=[];seen=0
 with opener(path,"rt",encoding="utf-8",errors="replace") as f:
  for lineno,line in enumerate(f,1):
   seen+=len(line)
   if seen>max_bytes or lineno>max_lines:break
   if any(token in line.lower() for token in ("vp05_full","[0,1,0,1","sector","masters","integral_family")):
    hits.append({"line":lineno,"text":line.strip()[:220]})
    if len(hits)>=8:break
 return hits

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 ap.add_argument("--certificate",type=Path,default=CERT)
 ap.add_argument("--max-files",type=int,default=2500)
 ap.add_argument("--max-candidates",type=int,default=35)
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_integral_id_source_inventory.json"))
 a=ap.parse_args()
 if not a.certificate.exists():ap.error("Missing exact original 528-row certificate")
 cert=json.loads(a.certificate.read_text(encoding="utf-8-sig"))
 if cert.get("original_528_row_exact_replay_verified") is not True:ap.error("Require full 528-row exact certificate PASS")
 if not a.project.exists():ap.error("Kira project directory not found: "+str(a.project))
 paths=[]
 for i,p in enumerate(a.project.rglob("*")):
  if i>=a.max_files:break
  if p.is_file():paths.append(p)
 prioritized=sorted((p for p in paths if any(x in p.name.lower() for x in ("master","integral","famil","sector","kira","config","system"))),key=lambda p:(p.suffix==".gz",str(p)))
 candidates=[]
 for p in prioritized:
  if len(candidates)>=a.max_candidates:break
  if p.suffix.lower() not in (".gz",".yaml",".yml",".json",".txt",".dat",".map",".config") and "SYSTEM" not in p.name:continue
  rel=str(p.relative_to(a.project))
  result={"path":rel,"bytes":p.stat().st_size}
  if p.stat().st_size<10_000_000 or p.suffix==".gz":
   try:result["matches"]=find_lines(p)
   except (OSError,UnicodeError) as e:result["read_error"]=str(e)[:140]
  candidates.append(result)
 report={"status":"SOURCE_INVENTORY_ONLY","certificate_exact_528_replay":True,
   "project":str(a.project),"scanned_files":len(paths),
   "scan_truncated":len(paths)>=a.max_files,"candidates":candidates,
   "physical_exponent_tuple_mapping_verified":False,
   "required":"Explicit Kira source mapping of each target certificate key (weight,sector) to a 12-entry signed integral index vector, checked against the actual project family definition"}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_INTEGRAL_ID_SOURCE_INVENTORY "+json.dumps({"status":report["status"],
    "scanned_files":len(paths),"candidates":[{"path":v["path"],"matches":v.get("matches",[])[:3]} for v in candidates[:15]],
    "output":str(a.output),"physical_exponent_tuple_mapping_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
