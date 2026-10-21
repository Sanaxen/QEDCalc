"""Audit VP05 target column labels against raw SYSTEM integral integer fields.

Do not decode integers as propagator indices without a verified Kira codec.
Prints observed integer fields, bit widths, and direct matches for target
labels to prevent accidental reinterpretation of (weight,sector) keys.
"""
import argparse,gzip,json,collections
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_raw_integer_id_audit.json"))
 a=p.parse_args()
 targets={(10,203),(6,203),(5,201)}
 source=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
 observed={t:[] for t in targets}
 raw_file=a.project/"tmp/VP05_full/SYSTEM_VP05_full_202.gz"
 integers=collections.Counter();examples=[];triplets=collections.Counter()
 with gzip.open(raw_file,"rt",encoding="utf-8",errors="replace") as fh:
  for n,line in enumerate(fh,1):
   f=line.strip().split()
   if len(f)!=6:continue
   try:
    count=int(f[0]);internal=int(f[2]);sector=int(f[3]);aux=(int(f[4]),int(f[5]))
   except ValueError:continue
   integers[(internal,sector)]+=1
   if len(examples)<15:examples.append({"line":n,"row_header_first_field":count,"coefficient":f[1],
     "internal_integer":internal,"sector":sector,"aux":list(aux),"bit_length":internal.bit_length(),
     "hex":hex(internal)})
   if (count,sector) in targets and len(observed[(count,sector)])<10:
    observed[(count,sector)].append({"line":n,"raw":f,"internal_integer":internal})
 report={"status":"RAW_ID_AUDIT_ONLY","source_rows":len(source),"raw_sector_file":str(raw_file),
   "distinct_internal_integer_sector_pairs":len(integers),"raw_samples":examples,
   "target_matches_by_first_field_and_sector":{str(k):v for k,v in observed.items()},
   "warning":"First field on SYSTEM term lines is not proven to equal certificate key weight; no ID-to-12-exponent mapping is claimed",
   "physical_index_mapping_verified":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_RAW_ID_AUDIT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
