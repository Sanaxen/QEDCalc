"""Read-only exact-target readiness gate for the 166-row VP05 compressed system.

Checks source provenance and modular target-closure invariants before any
unbounded rational-function Fermat calculation. No symbolic proof claimed.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_target_scope_preflight import (
 POINTS,TARGET,dependency_closure,estimates,target_trace)
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,modular_echelon
from examples.three_loop_sector203_target_rowspace_audit import eliminate,residue

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
WITNESS_DIR=Path("output/three_loop_integral_family_audit")

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--compressed",type=Path,default=DEFAULT)
 ap.add_argument("--witness",type=Path)
 ap.add_argument("--max-cells",type=int,default=20000)
 ap.add_argument("--output",type=Path,default=WITNESS_DIR/"vp05_exact_target_readiness.json")
 a=ap.parse_args()
 data=json.loads(a.compressed.read_text(encoding="utf-8-sig"))
 if data.get("type")!="symbolic_exact_linear_combinations":ap.error("Not a symbolic exact-combination dataset")
 rows=data["rows"]
 if len(rows)!=166:ap.error("Expected 166 compressed rows")
 witness=a.witness
 if witness is None:
  matches=sorted(WITNESS_DIR.glob("vp05_candidate4_witness_*.equations.json"))
  if not matches:ap.error("No 528-row original SYSTEM witness")
  witness=matches[-1]
 source=json.loads(witness.read_text(encoding="utf-8-sig"))["rows"]
 if len(source)!=528:ap.error("Expected 528-row original witness")
 indices=[r.get("row_index") for r in source]
 if any(not isinstance(i,int) or i<0 for i in indices) or len(set(indices))!=528:
  ap.error("Original witness missing unique row_index")
 if not all(isinstance(t.get("coefficient"),str) and isinstance(t.get("key"),list) for r in rows for t in r["terms"]):
  ap.error("Compressed coefficients or keys malformed")
 results=[]
 schedules=[]
 target_owners=[]
 for prime,z,d in POINTS:
  matrix=mod_rows(rows,prime,z,d)
  schedule,pivots=modular_echelon(matrix,prime)
  trace,remainder=target_trace(matrix,pivots,prime,z,d)
  target={k:residue(c,prime,z,d) for k,c in TARGET.items()}
  check=eliminate(matrix,target,prime)
  needed=dependency_closure(schedule,(owner for owner,_ in trace))
  scope=estimates(rows,schedule,needed)
  result={"point":[prime,z,d],"rank":len(pivots),"remainder_size":len(remainder),
      "target_in_rowspace":check["target_in_rowspace"],"certificate_replay":check["certificate_original_equation_replay_verified"],
      "dependency_rows":len(needed),"target_owners":len({owner for owner,_ in trace}),
      "estimated_cells":scope["estimated_array_cells_allocated"],"estimated_peak_live_cells":scope["estimated_peak_live_cells_if_released"],
      "within_cell_cap":scope["estimated_array_cells_allocated"]<=a.max_cells}
  results.append(result)
  schedules.append(schedule);target_owners.append([(int(o),list(k)) for o,k in trace])
 if not all(r["target_in_rowspace"] and r["certificate_replay"] and r["remainder_size"]==0 for r in results):
  status="BLOCKED_MODULAR_REPLAY"
 elif not all(s==schedules[0] for s in schedules[1:]):
  status="BLOCKED_DIFFERENT_PIVOT_SCHEDULE"
 elif not all(t==target_owners[0] for t in target_owners[1:]):
  status="BLOCKED_DIFFERENT_TARGET_PIVOTS"
 elif not all(r["within_cell_cap"] for r in results):
  status="BLOCKED_RESOURCE_ESTIMATE"
 else:status="PREFLIGHT_PASS_NOT_PROOF"
 output={"status":status,"source":str(a.compressed),"source_sha256":hashlib.sha256(a.compressed.read_bytes()).hexdigest(),
    "witness":str(witness),"witness_sha256":hashlib.sha256(witness.read_bytes()).hexdigest(),
    "source_rows":528,"compressed_rows":166,"points":results,
    "symbolic_identity_verified":False,"exact_528_row_replay_verified":False,
    "warning":"Modular schedules do not certify symbolic zero pivots, expression swell, exact combination provenance, or target identity. Preflight success does not authorize assuming modular zeros are exact."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
 print("VP05_EXACT_TARGET_READINESS "+json.dumps({**output,"output":str(a.output)}),flush=True)
 if status!="PREFLIGHT_PASS_NOT_PROOF":raise SystemExit(2)
if __name__=="__main__":main()
