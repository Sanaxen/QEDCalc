"""Inspect whether small SYSTEM IDs designate numbered Kira masters.

Uses original project's results/VP05_full/masters and external DB-backed
WeightCodec; only reports potential positional correlations. Does not claim
master numbering convention absent explicit source documentation.
"""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_master_index_hypothesis.json"))
 a=p.parse_args()
 master_file=a.project/"results/VP05_full/masters"
 if not master_file.is_file():p.error("Missing results/VP05_full/masters")
 text=master_file.read_text(encoding="utf-8-sig")
 powers=parse_file_integrals(master_file)
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 entries=[]
 for i,x in enumerate(powers):
  w=int(codec.encode(x))
  entries.append({"position_zero_based":i,"position_one_based":i+1,
   "integral":"VP05_full["+",".join(map(str,x))+"]",
   "weight":w,"codec_sector":int(m.sec_of(x)),"roundtrip":tuple(codec.decode(w))==tuple(x)})
 report={"status":"MASTER_NUMBERING_HYPOTHESIS_ONLY","master_file":str(master_file),
   "master_count":len(entries),"master_file_first_lines":text.splitlines()[:8],
   "masters":entries,"small_id_targets":[[10,203],[6,203],[5,201]],
   "physical_target_mapping_verified":False,
   "warning":"Matching numeric range or position does not by itself establish Kira's small-weight master-index convention; inspect raw Kira mapping metadata."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_MASTER_INDEX_HYPOTHESIS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
