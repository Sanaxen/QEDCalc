"""Finite-field rank gap for all 2678 saved VP05 Kira SYSTEM equations.

Reports dimension of row-space supported only on three raw target keys.
This is modular evidence, NOT symbolic or physical-alias proof.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,modular_echelon
from examples.three_loop_sector203_target_scope_preflight import TARGET
POINTS=((1000037,21,15),(1001003,19,53))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--point",type=int,choices=(1,2),default=1)
 a=p.parse_args()
 rows=read_rows(a.project)
 if len(rows)!=2678:p.error("Expected 2678 original SYSTEM equations")
 target=set(TARGET)
 point=POINTS[a.point-1];prime,z,d=point
 print("VP05_FULL_SYSTEM_THREE_ID_BEGIN "+json.dumps({"equations":len(rows),"point":point,"target_keys":[list(k) for k in sorted(target)],"proof":False}),flush=True)
 matrix=mod_rows(rows,prime,z,d)
 columns={k for r in matrix for k in r}
 if not target<=columns:raise SystemExit("Missing target keys")
 del rows
 full_rank=len(modular_echelon(matrix,prime)[1])
 print("VP05_FULL_SYSTEM_THREE_ID_FULL_RANK "+json.dumps({"point":point,"rank":full_rank}),flush=True)
 other=[{k:v for k,v in row.items() if k not in target} for row in matrix]
 del matrix
 non_target_rank=len(modular_echelon(other,prime)[1])
 gap=full_rank-non_target_rank
 report={"point":point,"system_equations":2678,"columns":len(columns),"full_rank":full_rank,
  "non_target_rank":non_target_rank,"target_only_relation_dimension":gap,
  "independent_second_relation_sampled":gap>=2,"symbolic_proof":False,
  "physical_alias_verified":False,"kira_executed":False,"source_files_modified":False}
 print("VP05_FULL_SYSTEM_THREE_ID_RESULT "+json.dumps(report),flush=True)
if __name__=="__main__":main()
