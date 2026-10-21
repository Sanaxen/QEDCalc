"""Diagnose Kira small SYSTEM weights against proven good encoded integrals.

Read-only. Does not assume small weights map to propagator tuples.
"""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_weight_semantics.json"))
 a=p.parse_args()
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 candidates=[]
 for name in ("preferred_provisional64_sector203.txt","mandatory_provisional64_sector203.txt"):
  path=a.project/name
  if not path.is_file():continue
  for powers in parse_file_integrals(path)[:6]:
   weight=int(codec.encode(powers))
   back=tuple(int(x) for x in codec.decode(weight))
   candidates.append({"source":name,"powers":list(powers),"encoded_weight":weight,
      "hex":hex(weight),"roundtrip":back==powers})
 examples=[]
 for w,s in ((10,203),(6,203),(5,201),(8,203),(3,202),(4,73)):
  item={"weight":w,"recorded_sector":s,"hex":hex(w)}
  try:item["decoded"]=list(codec.decode(w))
  except Exception as e:item["error"]=str(e)
  examples.append(item)
 report={"status":"WEIGHT_ENCODING_DIAGNOSTIC","bits":list(bits),
   "ordering":ordering,"target_and_small_weight_examples":examples,
   "known_integral_roundtrip_examples":candidates,
   "physical_target_mapping_verified":False,
   "warning":"Even valid codec on listed integrals does not establish small weights as valid physical integral IDs."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_SMALL_WEIGHT_SEMANTICS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
