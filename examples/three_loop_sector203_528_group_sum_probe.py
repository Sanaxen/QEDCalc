"""Classify VP05 multi-source compressed rows via modular group aggregation.

All checks are finite-field diagnostics, never exact source replay.
"""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS
from examples.three_loop_sector203_target_scope_preflight import POINTS
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows

def scalar(a,b,p):
 if set(a)!=set(b):return None
 if not a:return 1
 k=next(iter(a))
 if not b.get(k):return None
 x=a[k]*pow(b[k],-1,p)%p
 return x if all(a[k]==x*v%p for k,v in b.items()) else None

def group_sum(vectors,p):
 result={}
 for row in vectors:
  for k,v in row.items():
   n=(result.get(k,0)+v)%p
   if n:result[k]=n
   else:result.pop(k,None)
 return result

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--equations",type=Path,default=DEFAULT)
 ap.add_argument("--witness",type=Path,default=WITNESS)
 a=ap.parse_args()
 src=json.loads(a.equations.read_text(encoding="utf-8-sig"))["rows"]
 w=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
 if len(src)!=166 or len(w)!=528:ap.error("Incorrect expected row counts")
 for pt in POINTS:
  p,z,d=pt
  cr=mod_rows(src,p,z,d);wr=mod_rows(w,p,z,d)
  counts={"single":0,"multi":0,"multi_proportional_sum":0,"multi_exact_sum":0,
          "multi_proportional_any_member":0,"multi_unmatched_sum":0}
  examples=[]
  for i,row in enumerate(src):
   ids=row["original_rows"]
   if not ids or not all(type(j)==int and 0<=j<len(w) for j in ids):
    raise ValueError("Invalid original_rows witness-list index")
   if len(ids)==1:counts["single"]+=1;continue
   counts["multi"]+=1
   members=[wr[j] for j in ids]
   summed=group_sum(members,p)
   mul=scalar(cr[i],summed,p)
   if mul is not None:counts["multi_proportional_sum"]+=1
   else:counts["multi_unmatched_sum"]+=1
   if mul==1:counts["multi_exact_sum"]+=1
   if any(scalar(cr[i],v,p) is not None for v in members):counts["multi_proportional_any_member"]+=1
   if len(examples)<12:
    examples.append({"compressed_row":i,"original_rows_count":len(ids),
       "sum_scalar":mul,"compressed_support":len(cr[i]),"sum_support":len(summed),
       "witness_row_indices":[w[j]["row_index"] for j in ids[:3]]})
  print("VP05_528_GROUP_SUM_POINT "+json.dumps({"point":pt,**counts,"samples":examples[:5],
    "symbolic_exact_replay":False}),flush=True)
if __name__=="__main__":main()
