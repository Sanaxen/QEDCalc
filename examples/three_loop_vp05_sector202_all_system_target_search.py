"""Read-only search for physical sector202 targets across ALL saved Kira SYSTEM files.

Kira's stored sector label can differ from physical exponent-sector mask.
Therefore do NOT limit search to SYSTEM_*_202.gz. Use project-local DB codec.
"""
from __future__ import annotations
import gzip,json,re
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
def main():
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 result=[]
 for project in sorted((ROOT/"output").glob("kira_vp05*")):
  folder=project/"tmp/VP05_full"
  files=sorted(folder.glob("SYSTEM_VP05_full_*.gz")) if folder.is_dir() else []
  if not files:continue
  db=project/"results/kira.db";cfg=project/"config/integralfamilies.yaml"
  row={"project":str(project),"system_files":len(files)}
  try:
   if not db.is_file() or not cfg.is_file():raise ValueError("missing DB/config")
   bits,ordering=m.from_kiradb(str(db))
   match=re.search(r"top_level_sectors:\s*\[([^]]+)\]",cfg.read_text(encoding="utf-8"))
   if not match:raise ValueError("missing top-level sector declaration")
   tops=[int(x.strip()) for x in match.group(1).split(",") if x.strip()]
   codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=tops)
   target_weights={codec.encode(x):x for x in TARGETS}
   if len(target_weights)!=3 or any(tuple(codec.decode(w))!=v for w,v in target_weights.items()):raise ValueError("codec roundtrip mismatch")
   matches=Counter();head_matches=Counter();files_by_target={}
   eq_count=0
   for file in files:
    hits=Counter()
    with gzip.open(file,"rt",encoding="utf-8",errors="replace") as fh:
     while marker:=fh.readline():
      if marker.strip()!="Eq":raise ValueError("invalid equation marker")
      head=int(fh.readline().strip());n=int(fh.readline().strip());eq_count+=1
      if head in target_weights:head_matches[(head,file.name)]+=1
      for _ in range(n):
       fields=fh.readline().split()
       if len(fields)<4:raise ValueError("invalid SYSTEM term")
       w=int(fields[2]);s=int(fields[3])
       if w in target_weights:hits[(w,s)]+=1
    if hits:
     for key,count in hits.items():matches[key]+=count
     files_by_target[file.name]=[{"weight":w,"stored_sector":s,"occurrences":n} for (w,s),n in hits.items()]
   row.update({"ordering":ordering,"top_level_sectors":tops,"equations":eq_count,
    "targets":[{"exponents":list(t),"weight":w,
       "term_hits":[{"recorded_sector":s,"count":count} for (weight,s),count in matches.items() if weight==w],
       "head_hits":[{"file":fn,"count":n} for (weight,fn),n in head_matches.items() if weight==w]} for w,t in target_weights.items()],
    "files_with_target_weights":files_by_target})
  except Exception as exc:row["error"]=type(exc).__name__+": "+str(exc)[:280]
  result.append(row)
 print("VP05_SECTOR202_ALL_SYSTEM_TARGET_SEARCH "+json.dumps({
  "status":"VP05_SECTOR202_ALL_SYSTEM_TARGET_SEARCH","project_count":len(result),
  "projects":result,"coefficients_proven":False,"kira_executed":False,"files_modified":False,
  "note":"Exact target encoded weights searched in ALL SYSTEM filenames. A target appearing as a term is not automatically evidence of a solved reduction."},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
