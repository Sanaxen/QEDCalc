"""Conservative modular quotient sensitivity test for VP05 physical sector202.

Adds actual observed opaque low Kira ID columns as *formal free columns*
only in a deliberately relaxed model. Never identifies them as physical masters
or interprets relaxed membership as an exact reduction.
"""
from __future__ import annotations
import argparse,gzip,json
from pathlib import Path
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
P=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-fill",type=int,default=20000)
 args=ap.parse_args()
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=m.from_kiradb(str(P/"results/kira.db"))
 if ordering!=5:raise RuntimeError("unexpected ordering")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 target=[(codec.encode(x),139) for x in TARGETS]
 if any(tuple(codec.decode(k[0]))!=x for x,k in zip(TARGETS,target)):raise RuntimeError("codec mismatch")
 files=sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 rows=[];columns=set()
 for file in files:
  for row in equations(file,1000003,17,7):
   rows.append(row);columns.update(row)
 if len(rows)!=2678:raise RuntimeError("unexpected row count")
 if not all(x in columns for x in target):raise RuntimeError("target column missing")
 small=sorted(k for k in columns if k[0]<1024)
 result={"status":"VP05_SECTOR202_QUOTIENT_SENSITIVITY",
  "rows":len(rows),"columns":len(columns),"small_id_opaque_columns":[list(x) for x in small],
  "prime":1000003,"z":17,"d":7,"cases":[]}
 for name,free in [
  ("retained_sector202_C_only",[target[2]]),
  ("retained_C_plus_all_opaque_small_IDs",[target[2]]+small)]:
  span={}
  try:
   for row in rows:insert(row,span,1000003,args.max_fill)
   raw_rank=len(span)
   appended=[]
   for key in dict.fromkeys(free):
    inc=insert({key:1},span,1000003,args.max_fill)
    appended.append({"key":list(key),"rank_increased":inc})
   probes=[]
   for x,key in zip(TARGETS[:2],target[:2]):
    t=span.copy()
    inc=insert({key:1},t,1000003,args.max_fill)
    probes.append({"exponents":list(x),"in_equation_plus_free_columns_span":not inc})
   result["cases"].append({"name":name,"raw_rank":raw_rank,
    "rank_after_free_columns":len(span),"free_column_rank_increases":appended,
    "reduced_target_probes":probes})
  except Exception as exc:
   result["cases"].append({"name":name,"error":type(exc).__name__+": "+str(exc)[:200]})
 result["exact_reduction_proven"]=False
 result["limitation"]="Small Kira IDs are opaque and NOT assigned to physical masters. These two cases are sensitivity diagnostics, not the complete 63-master quotient, not proof or disproof of true reduction."
 result["kira_executed"]=False;result["files_modified"]=False
 print("VP05_SECTOR202_QUOTIENT_SENSITIVITY "+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
