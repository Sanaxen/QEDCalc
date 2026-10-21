"""Audit physical VP05 target vectors directly against original 528 Kira SYSTEM columns.

Unlike the earlier small-weight algebraic target, vectors are sourced from
mandatory list and encoded by original Kira database backed WeightCodec.
Column membership is exact; modular rowspace is NOT a symbolic proof.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_physical_target_column_audit.json"))
 a=p.parse_args()
 data=json.loads(a.witness.read_text(encoding="utf-8-sig"))
 rows=data["rows"]
 if len(rows)!=528:p.error("Expected 528 original SYSTEM witness rows")
 counts={};sources={}
 for i,r in enumerate(rows):
  for t in r["terms"]:
   key=tuple(t["key"])
   counts[key]=counts.get(key,0)+1
   if key not in sources:sources[key]={"row_index":r.get("row_index"),"file":r.get("file"),"equation_id":r.get("equation_id")}
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 mandatory=a.project/"mandatory_provisional64_sector203.txt"
 if not mandatory.is_file():p.error("Original mandatory integral list missing")
 integrals=parse_file_integrals(mandatory)
 if len(integrals)!=5:p.error("Expected exactly five mandatory VP05 targets")
 records=[]
 for powers in integrals:
  weight=int(codec.encode(powers));sector=int(m.sec_of(powers))
  decoded=tuple(int(x) for x in codec.decode(weight))
  if decoded!=powers:raise ValueError("Kira codec roundtrip FAILED")
  key=(weight,sector)
  pair_records=[{"recorded_sector":s,"occurrences":n,"sample":sources[(weight,s)]}
    for (w,s),n in sorted(counts.items()) if w==weight]
  records.append({"integral":"VP05_full["+",".join(map(str,powers))+"]",
     "exponents":list(powers),"weight":weight,"computed_sector":sector,
     "roundtrip_verified":True,"exact_key_present_in_528":key in counts,
     "exact_key_occurrences":counts.get(key,0),"observed_weight_sector_pairs":pair_records})
 report={"status":"PHYSICAL_TARGET_COLUMN_PRESENCE_AUDIT","source":str(a.witness),
  "source_sha256":hashlib.sha256(a.witness.read_bytes()).hexdigest(),
  "project":str(a.project),"mandatory_targets":records,
  "all_five_exact_columns_present":all(x["exact_key_present_in_528"] for x in records),
  "target_reduction_symbolically_proven":False,
  "note":"This audit proves identity/column provenance only; no rowspace, amplitudes or IBP reductions computed."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_PHYSICAL_TARGET_COLUMN "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
