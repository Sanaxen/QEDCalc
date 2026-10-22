"""VP05 three-small-ID independence diagnostic over two finite fields.

Rank(A)-rank(A with the three target columns removed) counts independent
row-space relations supported entirely on those three columns. This is a
sampled algebraic diagnostic, not an exact symbolic proof nor a physical alias.
No Kira and no source changes.
"""
from __future__ import annotations
import json
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,modular_echelon
from examples.three_loop_sector203_target_scope_preflight import TARGET
ROOT=Path("output/three_loop_integral_family_audit")
SRC=ROOT/"vp05_target_symbolic_compressed.equations.json"
POINTS=((1000037,21,15),(1001003,19,53))
def rank(rows,p):
 return len(modular_echelon(rows,p)[1])
def main():
 obj=json.loads(SRC.read_text(encoding="utf-8-sig"))
 rows=obj["rows"]
 if obj.get("type")!="symbolic_exact_linear_combinations" or len(rows)!=166:
  raise SystemExit("Expected 166 exact compressed rows")
 keys=set(TARGET)
 available={tuple(t["key"]) for r in rows for t in r["terms"]}
 if not keys<=available:raise SystemExit("Missing target keys")
 results=[]
 for p,z,d in POINTS:
  mat=mod_rows(rows,p,z,d)
  full=rank(mat,p)
  other=[{k:v for k,v in row.items() if k not in keys} for row in mat]
  non_target=rank(other,p)
  dim=full-non_target
  result={"point":[p,z,d],"rows":len(rows),"columns":len(available),
          "full_rank":full,"non_target_rank":non_target,
          "independent_relations_supported_only_on_three_keys":dim,
          "unique_identification_of_two_ids_from_anchor_supported":dim>=2,
          "symbolic_proof":False}
  results.append(result)
  print("VP05_THREE_ID_QUOTIENT_POINT "+json.dumps(result),flush=True)
 print("VP05_THREE_ID_QUOTIENT_SUMMARY "+json.dumps({
  "results":results,"all_sampled_dimensions_equal":len({r["independent_relations_supported_only_on_three_keys"] for r in results})==1,
  "physical_alias_verified":False,
  "interpretation":"Rank gap is only the number of sampled relations supported on three keys; no individual physical exponent aliases follow.",
  "kira_executed":False,"source_files_modified":False}),flush=True)
if __name__=="__main__":main()
