"""Inspect raw Kira SYSTEM integral headers and family configuration safely.

Read-only: reports bounded structural snippets, never infers exponent tuples
from compressed (weight,sector) labels alone.
"""
from __future__ import annotations
import argparse,gzip,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def sample(path,limit=80):
 opener=gzip.open if path.suffix==".gz" else open
 lines=[]
 with opener(path,"rt",encoding="utf-8",errors="replace") as f:
  for n,line in enumerate(f,1):
   t=line.rstrip()
   if t and (len(lines)<limit):lines.append({"line":n,"text":t[:400]})
   if n>=2000 or len(lines)>=limit:break
 return lines
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_system_id_format_audit.json"))
 a=p.parse_args()
 rels=["config/integralfamilies.yaml","tmp/VP05_full/SYSTEMconfig",
       "tmp/VP05_full/SYSTEM_VP05_full_202.gz",
       "preferred_provisional64_sector203.txt","mandatory_provisional64_sector203.txt"]
 result=[]
 for rel in rels:
  f=a.project/rel
  entry={"file":rel,"exists":f.is_file()}
  if f.is_file():
   try:entry["sample"]=sample(f,50 if f.suffix!=".gz" else 24)
   except (OSError,UnicodeError) as e:entry["error"]=str(e)
  result.append(entry)
 report={"status":"FORMAT_INSPECTION_ONLY","project":str(a.project),"files":result,
         "target_columns":[[10,203],[6,203],[5,201]],
         "physical_index_mapping_verified":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_SYSTEM_ID_FORMAT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
