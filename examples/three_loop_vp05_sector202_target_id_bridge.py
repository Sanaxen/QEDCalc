"""Read-only Kira weight-to-physical-integral bridge for saved VP05 sector202 SYSTEMs.

Requires external GPL pyred_weight.py supplied by the user. Decode with each
project's own Kira DB metadata; never guess integer ID encodings or reuse
a sector-rank map across projects.
"""
from __future__ import annotations
import argparse,gzip,json,re
from pathlib import Path
from collections import Counter,defaultdict
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
TARGETS=((0,1,0,1,-1,-1,1,1,0,0,0,0),(0,1,0,1,-2,0,1,1,0,0,0,0),(0,1,0,1,0,0,1,1,0,0,0,0))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--codec-file",type=Path,required=True)
 a=ap.parse_args()
 m=load_codec(a.codec_file.resolve())
 records=[]
 for project in sorted((ROOT/"output").glob("kira_vp05*")):
  path=project/"tmp/VP05_full/SYSTEM_VP05_full_202.gz"
  db=project/"results/kira.db"
  cfg=project/"config/integralfamilies.yaml"
  if not path.is_file():continue
  record={"project":str(project),"system_path":str(path),"db_exists":db.is_file()}
  if not db.is_file() or not cfg.is_file():
   record["error"]="project metadata missing";records.append(record);continue
  try:
   bits,ordering=m.from_kiradb(str(db))
   if ordering not in (1,5):raise ValueError("unsupported integral ordering "+str(ordering))
   config=cfg.read_text(encoding="utf-8")
   match=re.search(r"top_level_sectors:\s*\[([^]]+)\]",config)
   if not match:raise ValueError("top_level_sectors not explicitly specified")
   tops=[int(v.strip()) for v in match.group(1).split(",") if v.strip()]
   if not tops:raise ValueError("top_level_sectors empty")
   codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=tops)
   weights={codec.encode(x):x for x in TARGETS}
   if len(weights)!=len(TARGETS):raise ValueError("target weights collide")
   for x in TARGETS:
    if tuple(codec.decode(codec.encode(x)))!=x:raise ValueError("target encode/decode roundtrip failed")
   counts=Counter();heads=Counter();decoded_sector_ranks=defaultdict(Counter)
   eq=0;term=0;invalid=0
   with gzip.open(path,"rt",encoding="utf-8") as fh:
    while line:=fh.readline():
     if line.strip()!="Eq":raise ValueError("bad equation marker")
     head=int(fh.readline().strip());n=int(fh.readline().strip());eq+=1
     if head in weights:heads[head]+=1
     for _ in range(n):
      fields=fh.readline().split()
      if len(fields)<4:raise ValueError("short SYSTEM row")
      w=int(fields[2]);s=int(fields[3]);term+=1
      if w in weights:counts[(w,s)]+=1
      # Sample real labels only for the target weights, not all IDs.
      if w in weights:
       dec=codec.decode(w)
       if codec.encode(dec)!=w or tuple(dec)!=weights[w]:invalid+=1
       decoded_sector_ranks[s][m.sec_of(dec)]+=1
   if invalid:raise ValueError("target decode roundtrip mismatch "+str(invalid))
   record.update({"top_level_sectors":tops,"integral_ordering":ordering,"equations":eq,
    "terms":term,"targets":[{
     "exponents":list(x),"weight":codec.encode(x),
     "physical_sector":m.sec_of(x),
     "term_occurrences":[{"recorded_sector":s,"count":v} for (w,s),v in sorted(counts.items()) if w==codec.encode(x)],
     "head_occurrences":heads[codec.encode(x)]} for x in TARGETS],
    "recorded_to_physical_sector_for_target_weights":{str(s):dict(c) for s,c in decoded_sector_ranks.items()},
    "target_id_codec_roundtrip":True})
  except Exception as exc:record["error"]=type(exc).__name__+": "+str(exc)[:350]
  records.append(record)
 print("VP05_SECTOR202_TARGET_ID_BRIDGE "+json.dumps({
  "status":"VP05_SAVED_SECTOR202_TARGET_ID_BRIDGE","projects_scanned":len(records),
  "projects":records,"coefficient_relation_proven":False,
  "scope":"read-only target-weight coverage; non-target IDs and algebraic rank not yet certified",
  "kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
