"""Audit mandatory VP05 targets versus actual Kira masters and selection logs.

Read-only. Shows complete bounded tail of Kira logs around recursive
selection, regeneration, initiate and termination, to avoid treating
generated SYSTEM equation count as selected reduction proof.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import parse_file_integrals,load_codec

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_mandatory_master_selection_audit.json"))
 a=p.parse_args()
 mandatory=parse_file_integrals(a.project/"mandatory_provisional64_sector203.txt")
 masters=parse_file_integrals(a.project/"results/VP05_full/masters")
 if len(mandatory)!=5:raise ValueError("Expected five mandatory integrals")
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 records=[]
 for v in mandatory:
  w=int(codec.encode(v))
  if tuple(codec.decode(w))!=v:raise RuntimeError("Kira codec roundtrip mismatch")
  records.append({"integral":"VP05_full["+",".join(map(str,v))+"]",
    "weight":w,"sector":int(m.sec_of(v)),"in_saved_masters":v in masters,
    "master_list_position_one_based":masters.index(v)+1 if v in masters else None})
 logs=[]
 for filename in ("kira.log","monitored_kira.log"):
  file=a.project/filename;entry={"file":filename,"present":file.is_file()}
  if file.is_file():
   lines=file.read_text(encoding="utf-8-sig",errors="replace").splitlines()
   entry["line_count"]=len(lines)
   entry["last_lines"]=[{"line":i+1,"text":s} for i,s in list(enumerate(lines))[-85:]]
  logs.append(entry)
 report={"status":"MASTER_SELECTION_TRACE_ONLY",
  "mandatory_count":len(mandatory),"saved_master_count":len(masters),
  "mandatory_masters":sum(v["in_saved_masters"] for v in records),
  "mandatory_nonmasters":[x for x in records if not x["in_saved_masters"]],
  "targets":records,"logs":logs,
  "reduction_of_nonmaster_verified":False,
  "interpretation":"Kira log's 0 equations then 2678 regeneration must be read in context. A master requires no reduction, while a selected non-master requires a verified reduction or explicitly unresolved status. Exact physical reduction not proven."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_MANDATORY_MASTER_SELECTION "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
