"""Read-only structural classification of small weights in original Kira SYSTEM.

Collect full per-file counts, term flags and equation-header relations for
small-weight columns. Classification is evidence only, not an integral codec.
"""
from __future__ import annotations
import argparse,collections,gzip,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

TARGET=((10,203),(6,203),(5,201))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--max-small-weight",type=int,default=32)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_weight_role_audit.json"))
 a=p.parse_args()
 files=sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 if not files:p.error("No original SYSTEM files")
 file_counts={};small={};equations_with_targets={str(k):[] for k in TARGET}
 flags=collections.Counter();equation_heads=collections.Counter()
 for path in files:
  stats=collections.Counter()
  with gzip.open(path,"rt",encoding="utf-8",errors="replace") as fh:
   ordinal=0
   while marker:=fh.readline():
    if marker.strip()!="Eq":raise ValueError("Malformed SYSTEM marker")
    ordinal+=1;eid=int(fh.readline().strip());n=int(fh.readline().strip())
    equation_heads[eid]+=1
    terms=[]
    for _ in range(n):
     x=fh.readline().split()
     if len(x)!=6:raise ValueError("Unexpected SYSTEM field count")
     weight=int(x[2]);sector=int(x[3]);term=(weight,sector)
     stats["terms"]+=1
     if 0<=weight<=a.max_small_weight:
      stats["small_terms"]+=1
      v=small.setdefault(str(term),{"count":0,"files":collections.Counter(),"flags":collections.Counter(),"samples":[]})
      v["count"]+=1;v["files"][path.name]+=1;v["flags"][(x[4],x[5])]+=1
      if len(v["samples"])<3:v["samples"].append({"file":path.name,"equation_ordinal":ordinal,"equation_id":eid,"fields":x})
     terms.append(term)
    stats["equations"]+=1
    if any(0<=weight<=a.max_small_weight for weight,_ in terms):
     stats["equations_with_small"]+=1
     if any(weight>a.max_small_weight for weight,_ in terms):stats["mixed_equations"]+=1
    for target in TARGET:
     if target in terms and len(equations_with_targets[str(target)])<15:
      equations_with_targets[str(target)].append({"file":path.name,"equation_ordinal":ordinal,
       "equation_id":eid,"term_count":n,"large_terms":sum(x[0]>a.max_small_weight for x in terms),
       "distinct_sectors":sorted({x[1] for x in terms})})
  file_counts[path.name]=dict(stats)
 compact={k:{"count":v["count"],"files":dict(v["files"]),
  "flags":{str(key):count for key,count in v["flags"].items()},
  "samples":v["samples"]} for k,v in small.items()}
 report={"status":"STRUCTURAL_ROLE_ONLY","files":len(files),"file_counts":file_counts,
  "distinct_equation_headers":len(equation_heads),
  "small_weights":compact,"target_contexts":equations_with_targets,
  "physical_integral_mapping_verified":False,
  "caution":"Do not assume numeric small SYSTEM weights are valid exponent weights or master indices."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_SMALL_WEIGHT_ROLE "+json.dumps({"status":report["status"],
   "files":len(files),"small_id_count":len(compact),
   "totals":{"small_terms":sum(x.get("small_terms",0) for x in file_counts.values()),
     "mixed_equations":sum(x.get("mixed_equations",0) for x in file_counts.values())},
   "target_contexts":equations_with_targets,
   "output":str(a.output),"physical_integral_mapping_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
