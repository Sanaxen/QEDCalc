"""Verify physical interpretation and saved two-term relations for VP05 L2 small ID 4.

Read-only: no Kira execution, no output writes, and no coefficient synthesis.
"""
from __future__ import annotations
import gzip,json,re,hashlib
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,parse_file_integrals
P=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
KEY=(4,73)
def main():
 job=(P/"jobs.yaml").read_text(encoding="utf-8-sig")
 m=re.findall(r'^\s*preferred_masters:\s*["\']?([^"\'\s#]+)',job,re.M)
 if len(m)!=1:raise RuntimeError("Expected one preferred_masters declaration")
 path=Path(m[0])
 if path.is_absolute() or ".." in path.parts:raise RuntimeError("Invalid preferred path")
 inp=P/path;out=P/"results/preferredMasters"
 v1=parse_file_integrals(inp);v2=parse_file_integrals(out)
 if len(v1)!=10 or v1!=v2 or len(set(v1))!=10:raise RuntimeError("Preferred master order mismatch")
 entries=[];sector_labels={i:set() for i in range(1,11)};seen=0;bridges=[]
 for f in sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(f,"rt",encoding="utf-8") as stream:
   idx=0
   while marker:=stream.readline():
    if marker.strip()!="Eq":raise ValueError("Malformed marker")
    eid=stream.readline().strip();n=int(stream.readline());idx+=1;seen+=1
    terms=[]
    for _ in range(n):
     fields=stream.readline().split()
     if len(fields)<4:raise ValueError("Truncated term")
     key=(int(fields[2]),int(fields[3]))
     terms.append({"key":list(key),"coefficient":fields[1]})
     if 1<=key[0]<=10:sector_labels[key[0]].add(key[1])
    if KEY in [tuple(t["key"]) for t in terms]:
     entries.append({"source_file":f.name,"equation_ordinal":idx,
      "equation_id":eid,"terms":len(terms)})
     if n==2:bridges.append({"source_file":f.name,"equation_ordinal":idx,"equation_id":eid,"terms":terms})
 if seen!=2678:raise RuntimeError("Expected saved L2 source with 2678 equations")
 physical=[{"small_id":i,"exponents":list(x),"physical_sector":sum((1<<j) for j,e in enumerate(x) if e>0),
  "observed_sectors":sorted(sector_labels[i])} for i,x in enumerate(v1,1)]
 match=all(r["observed_sectors"]==[r["physical_sector"]] for r in physical)
 report={"status":"VP05_SECTOR202_SMALL4_PHYSICAL_SOURCE_AUDIT",
  "preferred_order_verified":True,"all_ten_sector_labels_match":match,
  "small4":physical[3],"preferred_input_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
  "preferred_result_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
  "saved_equations":seen,"small4_equation_count":len(entries),
  "small4_equation_samples":entries[:18],"small4_exact_two_term_bridges":bridges[:15],
  "two_term_bridges_total":len(bridges),
  "interpretation":"Preferred order and matching Kira small sector tags support physical identity of ID4; Kira version-specific compact-ID source semantics and exact coefficient reduction remain independent checks.",
  "kira_version_source_semantics_verified":False,
  "two_target_exact_coefficients_proven":False,"kira_executed":False,"files_modified":False}
 print("VP05_SECTOR202_SMALL4_SOURCE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
