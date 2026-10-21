"""Discover directly recorded 2-term alias relations for small Kira SYSTEM IDs.

Read-only and evidence-only. A two-term equation with large-weight partner
suggests an alias but alone does not establish 12-index mapping, which needs
codec roundtrip and sector validation.
"""
from __future__ import annotations
import argparse,collections,gzip,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

TARGET=((10,203),(6,203),(5,201))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_weight_alias_edges.json"))
 p.add_argument("--small-cap",type=int,default=32)
 a=p.parse_args()
 edges=[];small_counts=collections.Counter();small_to_large=collections.Counter()
 for file in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(file,"rt",encoding="utf-8",errors="replace") as f:
   ordinal=0
   while marker:=f.readline():
    if marker.strip()!="Eq":raise ValueError("Unexpected Eq marker")
    ordinal+=1;eid=int(f.readline().strip());n=int(f.readline().strip())
    terms=[]
    for _ in range(n):
     parts=f.readline().split()
     if len(parts)!=6:raise ValueError("Malformed SYSTEM term")
     terms.append({"weight":int(parts[2]),"sector":int(parts[3]),"coefficient":parts[1],
                   "flags":parts[4:6]})
    if n!=2:continue
    low=[t for t in terms if 0<=t["weight"]<=a.small_cap]
    high=[t for t in terms if t["weight"]>a.small_cap]
    if len(low)!=1 or len(high)!=1:continue
    l,h=low[0],high[0];k=(l["weight"],l["sector"])
    small_counts[k]+=1;small_to_large[(k,(h["weight"],h["sector"]))]+=1
    edges.append({"file":file.name,"equation_ordinal":ordinal,"equation_id":eid,
       "small":l,"large":h})
 summary={}
 for k in TARGET:
  partners=[{"large":list(high),"equations":n} for (low,high),n in small_to_large.items() if low==k]
  partners.sort(key=lambda x:-x["equations"])
  sample=[edge for edge in edges if (edge["small"]["weight"],edge["small"]["sector"])==k][:12]
  summary[str(k)]={"two_term_edges":small_counts[k],"large_partners":partners,"samples":sample}
 report={"status":"ALIAS_EDGE_DISCOVERY_ONLY","two_term_edges_total":len(edges),
    "target_edges":summary,
    "small_pair_count":len(small_counts),
    "all_edges":edges,
    "physical_id_mapping_verified":False,
    "requirement":"Independent Kira codec proof for large partners, recorded-sector consistency and exact nonzero coefficient relation. Never merge columns solely on two-term appearance."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_SMALL_WEIGHT_ALIAS_EDGES "+json.dumps({"status":report["status"],
    "two_term_edges_total":len(edges),"small_pair_count":len(small_counts),
    "target_edges":summary,"physical_id_mapping_verified":False,"output":str(a.output)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
