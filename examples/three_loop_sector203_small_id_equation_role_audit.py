"""Inspect VP05 SYSTEM auxiliary IDs against raw heads and neighboring weights.

Evidence-only diagnostic: do not infer a physical exponent mapping.
"""
from __future__ import annotations
import argparse,gzip,json
from collections import defaultdict,Counter
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_equation_role_audit.json"))
 a=p.parse_args()
 counts=Counter(); cooccur=defaultdict(Counter); heads=Counter(); samples=defaultdict(list); nrows=0
 for path in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(path,"rt",encoding="utf-8") as f:
   while (mark:=f.readline()):
    if mark.strip()!="Eq":raise ValueError("Bad SYSTEM marker")
    head=int(f.readline().strip()); length=int(f.readline().strip())
    heads[head]+=1;nrows+=1; terms=[]
    for _ in range(length):
     t=f.readline().split()
     if len(t)<4:raise ValueError("Malformed term")
     terms.append((int(t[2]),int(t[3]),t[1]))
    tiny=sorted({(w,s) for w,s,_ in terms if 1<=w<=10})
    large=sorted({(w,s) for w,s,_ in terms if w>10})
    for key in tiny:
     counts[key]+=1
     for other in tiny:
      if other!=key:cooccur[key][other]+=1
     if len(samples[key])<7:
      samples[key].append({"file":path.name,"head":head,"term_count":length,
       "small_keys":[list(x) for x in tiny],"large_key_count":len(large),
       "large_key_samples":[list(x) for x in large[:5]]})
 if nrows!=2678:p.error("Wrong source project")
 entries=[]
 for key in sorted(counts):
  entries.append({"key":list(key),"equations_containing_key":counts[key],
   "small_id_as_equation_head":heads[key[0]],
   "cooccurring_small_ids":[{"key":list(k),"equations":v} for k,v in cooccur[key].most_common(9)],
   "equation_examples":samples[key]})
 result={"system_equations":nrows,"distinct_equation_heads":len(heads),
  "small_ids":entries,"physical_alias_mapping_verified":False,
  "warning":"Co-occurrence and head counts are structural evidence, not a justified physical-integral mapping."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_SMALL_ID_EQUATION_ROLE "+json.dumps({**result,"output":str(a.output)}),flush=True)
if __name__=="__main__": main()
