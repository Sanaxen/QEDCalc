"""Inspect whether VP05 compressed rows are exact scalar multiples of witness rows.

A match alone is not exact proof. First compares modular proportionality at
four points; exact rational equality must be independently established.
"""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS
from examples.three_loop_sector203_target_scope_preflight import POINTS
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows

def proportional(a,b,p):
 if set(a)!=set(b):return False
 if not a:return not b
 k=next(iter(a))
 if not b.get(k):return False
 scale=a[k]*pow(b[k],-1,p)%p
 return all(a[x]==scale*b[x]%p for x in a)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--equations",type=Path,default=DEFAULT)
 ap.add_argument("--witness",type=Path,default=WITNESS)
 ap.add_argument("--max-groups",type=int,default=166)
 a=ap.parse_args()
 s=json.loads(a.equations.read_text(encoding="utf-8-sig"))["rows"]
 w=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
 if len(s)!=166 or len(w)!=528:ap.error("Expected 166 compressed and 528 witness rows")
 if not 1<=a.max_groups<=166:ap.error("--max-groups must be 1..166")
 results=[]
 # original_rows is apparently an index into witness LIST (0..527), not the
 # raw SYSTEM row_index (e.g. 11,133,...); test both only via explicit bounds.
 for pt in POINTS:
  p,z,d=pt
  sm=mod_rows(s[:a.max_groups],p,z,d)
  wm=mod_rows(w,p,z,d)
  matched=0;single=0;multi=0;nomatch=[];group_match=[]
  for i,row in enumerate(s[:a.max_groups]):
   inds=row["original_rows"]
   if not inds or not all(type(x)==int and 0<=x<len(w) for x in inds):
    raise ValueError("original_rows contains invalid witness-list index")
   matches=[j for j in inds if proportional(sm[i],wm[j],p)]
   if matches:matched+=1
   else:nomatch.append(i)
   if len(inds)==1:single+=1
   else:multi+=1
   group_match.append({"row":i,"group_size":len(inds),"matching_witness_list_indices":matches[:8]})
  result={"point":pt,"groups_tested":a.max_groups,"single_groups":single,
    "multi_groups":multi,"groups_with_proportional_member":matched,
    "groups_without_match_count":len(nomatch),"sample_nonmatching_groups":nomatch[:12],
    "first_groups":group_match[:8],"symbolic_proof":False}
  results.append(result)
  print("VP05_528_SCALAR_PROBE_POINT "+json.dumps({k:v for k,v in result.items() if k not in ("first_groups",)}),flush=True)
 print("VP05_528_SCALAR_PROBE_SUMMARY "+json.dumps({
   "all_groups_have_scalar_member_all_points":all(r["groups_with_proportional_member"]==a.max_groups for r in results),
   "per_point_matching":[r["groups_with_proportional_member"] for r in results],
   "interpretation":"Modular proportionality only; source row_index and exact scale must still be established",
   "original_528_row_exact_replay_verified":False}),flush=True)
if __name__=="__main__":main()
