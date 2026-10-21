"""Find five codec-verified physical VP05 targets in ALL original SYSTEM rows.

Unlike 528-row selected witness, examine all 14 raw SYSTEM gzip files.
Count exact sector matches and mismatched recorded sectors separately.
Never interpret small raw weight IDs as physical exponent tuples.
"""
from __future__ import annotations
import argparse,collections,gzip,json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_full_system_physical_target_presence.json"))
 a=p.parse_args()
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 if ordering!=5:p.error("Unexpected integral ordering")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 target_file=a.project/"mandatory_provisional64_sector203.txt"
 vectors=parse_file_integrals(target_file)
 if len(vectors)!=5:p.error("Expected five mandatory integral vectors")
 weights={}
 for powers in vectors:
  weight=int(codec.encode(powers))
  if tuple(int(x) for x in codec.decode(weight))!=powers:raise RuntimeError("Codec roundtrip failed")
  weights[weight]={"integral":"VP05_full["+",".join(map(str,powers))+"]",
    "exponents":list(powers),"weight":weight,"computed_sector":int(m.sec_of(powers)),
    "observations":collections.Counter(),"sample_rows":[]}
 files=sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 if not files:p.error("No raw SYSTEM files")
 equation_count=0;term_count=0
 for file in files:
  with gzip.open(file,"rt",encoding="utf-8",errors="replace") as f:
   ordinal=0
   while marker:=f.readline():
    if marker.strip()!="Eq":raise ValueError("Unexpected SYSTEM marker")
    ordinal+=1;equation_count+=1
    eid=int(f.readline().strip());n=int(f.readline().strip())
    for j in range(n):
     t=f.readline().split()
     if len(t)<4:raise ValueError("Malformed raw SYSTEM term")
     term_count+=1
     w,s=int(t[2]),int(t[3])
     if w in weights:
      rec=weights[w];rec["observations"][(s,file.name)]+=1
      if len(rec["sample_rows"])<8:rec["sample_rows"].append({"file":file.name,
          "equation_ordinal":ordinal,"equation_id":eid,"term_index":j,
          "recorded_sector":s,"coefficient":t[1]})
 result=[]
 for record in weights.values():
  obs=[{"sector":sec,"file":file,"occurrences":count} for (sec,file),count in sorted(record["observations"].items())]
  matched=sum(x["occurrences"] for x in obs if x["sector"]==record["computed_sector"])
  result.append({k:v for k,v in record.items() if k!="observations"} |
     {"recorded_occurrences":sum(x["occurrences"] for x in obs),
       "exact_sector_occurrences":matched,"observed_sector_file_counts":obs})
 report={"status":"FULL_SYSTEM_TARGET_PRESENCE_AUDIT","source_equations":equation_count,
   "source_files":len(files),"source_terms":term_count,"targets":result,
   "all_five_present":all(x["recorded_occurrences"]>0 for x in result),
   "all_five_exact_sector_present":all(x["exact_sector_occurrences"]>0 for x in result),
   "physical_ibp_reduction_proven":False,
   "interpretation":"Presence in original SYSTEM is not a proof of target reducibility."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_FULL_SYSTEM_PHYSICAL_TARGET "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
