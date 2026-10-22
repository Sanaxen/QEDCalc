"""Diagnostic for VP05 sector202 target ID absence in saved SYSTEM records.

Decode observed term IDs using source-project Kira DB; contrast actual
physical sector distributions and nearby integral indices with three targets.
No fabricated IDs, Kira runs, or source writes.
"""
from __future__ import annotations
import argparse,gzip,json
from collections import Counter,defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--codec-file",type=Path,default=ROOT/"output/tools/pyred_weight.py")
 a=ap.parse_args()
 project=ROOT/"output/kira_vp05_full_masters_candidate_closure_r8s3d0_r8s4d3"
 db=project/"results/kira.db";source=project/"tmp/VP05_full/SYSTEM_VP05_full_202.gz"
 m=load_codec(a.codec_file.resolve())
 bits,ordering=m.from_kiradb(str(db))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[255])
 counts=Counter();sector_map=defaultdict(Counter);near=[]
 errors=[];entries=0
 with gzip.open(source,"rt",encoding="utf-8") as fh:
  while marker:=fh.readline():
   if marker.strip()!="Eq":raise ValueError("Invalid Kira equation marker")
   fh.readline();n=int(fh.readline())
   for _ in range(n):
    v=fh.readline().split()
    weight=int(v[2]);recorded=int(v[3]);entries+=1
    if (weight,recorded) in counts:counts[(weight,recorded)]+=1;continue
    counts[(weight,recorded)]+=1
 for (weight,recorded),occ in counts.items():
  try:
   e=tuple(codec.decode(weight))
   physical=m.sec_of(e)
   if codec.encode(e)!=weight:raise ValueError("roundtrip mismatch")
   sector_map[recorded][physical]+=1
   if physical==202:
    dist=min(sum(abs(x-y) for x,y in zip(e,t)) for t in TARGETS)
    if dist<=3:near.append({"exponents":list(e),"weight":weight,"recorded_sector":recorded,"distance":dist,"occurrences":occ})
  except Exception as exc:
   if len(errors)<8:errors.append({"weight":weight,"recorded":recorded,"error":str(exc)})
 near.sort(key=lambda x:(x["distance"],-x["occurrences"]))
 print("VP05_SECTOR202_OBSERVED_CODEC "+json.dumps({
  "status":"VP05_SECTOR202_OBSERVED_CODEC_DIAGNOSTIC","project":str(project),
  "source":str(source),"integral_ordering":ordering,
  "term_count":entries,"unique_weight_sector_pairs":len(counts),
  "recorded_to_physical_sector":{str(k):dict(v) for k,v in sorted(sector_map.items())},
  "near_target_decoded_integrals":near[:35],"near_target_total":len(near),
  "decode_error_examples":errors,
  "targets":[{"exponents":list(t),"encoded_weight":codec.encode(t)} for t in TARGETS],
  "target_relation_proven":False,"kira_executed":False,"files_modified":False},
  ensure_ascii=False),flush=True)
if __name__=="__main__":main()
