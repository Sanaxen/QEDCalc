"""Audit compact Kira IDs against the actual L2 preferred-master input.

Kira PyRed source: Integral::set_preferred_masters() assigns 1-based IDs in
imported preference order. Verify jobs reference, saved input/results list,
distinctness, 10 observed small SYSTEM pairs and sector masks. No Kira run.
"""
from __future__ import annotations
import argparse,hashlib,json,re,gzip
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import parse_file_integrals
TARGETS=((10,203),(6,203),(5,201))
def sec(v):return sum(1<<i for i,x in enumerate(v) if x>0)
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,default=DEFAULT);a=p.parse_args()
 root=a.project.resolve()
 job=(root/"jobs.yaml").read_text(encoding="utf-8-sig")
 m=re.findall(r'^\s*preferred_masters:\s*["\']?([^"\'\s#]+)',job,re.M)
 if len(m)!=1:p.error("Exactly one preferred_masters entry required")
 name=m[0]
 if Path(name).is_absolute() or ".." in Path(name).parts:p.error("Unsafe preferred reference")
 inp=root/name;result=root/"results/preferredMasters"
 if not inp.is_file() or not result.is_file():p.error("Missing configured preferred input or saved preferredMasters")
 a1=parse_file_integrals(inp);a2=parse_file_integrals(result)
 if len(a1)!=10 or len(a2)!=10 or len(set(a1))!=10 or a1!=a2:
  p.error("Preferred input and saved result must match as 10 ordered distinct integrals")
 observed=defaultdict(set);count=0
 for f in sorted((root/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(f,"rt",encoding="utf-8") as stream:
   while mark:=stream.readline():
    if mark.strip()!="Eq":raise RuntimeError("Bad SYSTEM marker")
    stream.readline();n=int(stream.readline().strip());count+=1
    for _ in range(n):
     words=stream.readline().split()
     if len(words)<4:raise RuntimeError("Bad SYSTEM term")
     w,s=int(words[2]),int(words[3])
     if 1<=w<=10:observed[w].add(s)
 if count!=2678:p.error("Unexpected SYSTEM equation count")
 rows=[]
 for i,x in enumerate(a1,1):
  sectors=sorted(observed[i])
  rows.append({"small_weight":i,"observed_recorded_sectors":sectors,
    "computed_sector_mask":sec(x),"sector_matches":sectors==[sec(x)],
    "exponents":list(x),"target":(i,sec(x)) in TARGETS})
 checks={"configured_input_matches_saved_preferred_order":True,
         "all_ten_ids_present":set(observed)==set(range(1,11)),
         "all_ten_sectors_match":all(x["sector_matches"] for x in rows)}
 report={"status":"PREFERRED_COMPACT_ID_MAPPING_VERIFIED" if all(checks.values()) else "PREFERRED_COMPACT_ID_MAPPING_INCOMPLETE",
  "checks":checks,"targets":[r for r in rows if r["target"]],"all_preferred":rows,
  "configured_input":name,"saved_preferred":"results/preferredMasters",
  "input_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
  "result_sha256":hashlib.sha256(result.read_bytes()).hexdigest(),
  "source_reference":"https://github.com/BootLoops-ai/kira/blob/main/src/pyred/integrals.cpp",
  "source_semantics":"set_preferred_masters assigns ordered 1-based weights; properties remaps via s_weight_map",
  "kira_version_compatibility_verified":False,
  "physical_propagator_mapping_verified":False,
  "previous_anchor_bridge_can_be_symmetry_equivalent_not_literal_same_indices":True,
  "kira_executed":False,"source_files_modified":False}
 print("VP05_PREFERRED_COMPACT_ID_AUDIT "+json.dumps(report,ensure_ascii=False),flush=True)
 if not all(checks.values()):raise SystemExit(2)
if __name__=="__main__":main()
