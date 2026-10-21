"""Trace small target column IDs back to actual Kira SYSTEM term fields.

Inspect raw weights in ALL SYSTEM files (not the equation-term count field).
This is an identity/lineage audit, not a proof that small IDs decode as
physical propagator powers.
"""
from __future__ import annotations
import argparse,gzip,json,collections
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

TARGET=((10,203),(6,203),(5,201))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 ap.add_argument("--witness",type=Path,default=WITNESS)
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_raw_column_lineage.json"))
 a=ap.parse_args()
 witness=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
 source_hits={k:[] for k in TARGET}
 for i,row in enumerate(witness):
  for term in row["terms"]:
   key=tuple(term["key"])
   if key in source_hits:
    source_hits[key].append({"witness_list_index":i,"system_row_index":row["row_index"],
       "file":row["file"],"equation_id":row["equation_id"],
       "coefficient":term["coefficient"]})
 raw_hits={k:[] for k in TARGET}
 files=sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 low_weights=collections.Counter()
 for file in files:
  with gzip.open(file,"rt",encoding="utf-8",errors="replace") as fh:
   equation=0
   while marker:=fh.readline():
    if marker.strip()!="Eq":raise ValueError("Bad raw SYSTEM marker")
    equation+=1
    eid=int(fh.readline().strip());count=int(fh.readline().strip())
    for term_index in range(count):
     fields=fh.readline().split()
     if len(fields)<4:raise ValueError("Malformed raw SYSTEM term")
     weight=int(fields[2]);sector=int(fields[3])
     if weight<1000:low_weights[(weight,sector)]+=1
     key=(weight,sector)
     if key in raw_hits and len(raw_hits[key])<30:
      raw_hits[key].append({"file":file.name,"equation_ordinal_in_file":equation,
       "equation_id":eid,"term_index":term_index,"raw_line":fields[:6]})
 report={"status":"SOURCE_ID_LINEAGE_ONLY",
  "raw_system_files":len(files),"witness_rows":len(witness),
  "target_columns":[{"key":list(k),"witness_occurrences":len(source_hits[k]),
     "witness_examples":source_hits[k][:8],
     "raw_system_examples":raw_hits[k],"found_in_raw_system":bool(raw_hits[k])} for k in TARGET],
  "low_weight_raw_pairs":[{"weight":w,"sector":s,"occurrences":n}
      for (w,s),n in low_weights.most_common(24)],
  "physical_exponent_tuple_mapping_verified":False,
  "interpretation":"Raw field 2 is the encoded weight; first field is a term-list datum. Presence proves raw provenance, not decodability."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_TARGET_RAW_COLUMN_LINEAGE "+json.dumps({
  "status":report["status"],"raw_system_files":len(files),
  "target_columns":[{"key":v["key"],"witness_occurrences":v["witness_occurrences"],
    "found_in_raw_system":v["found_in_raw_system"],"raw_system_examples":v["raw_system_examples"][:3]} for v in report["target_columns"]],
  "low_weight_raw_pairs":report["low_weight_raw_pairs"][:10],
  "physical_exponent_tuple_mapping_verified":False,"output":str(a.output)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
