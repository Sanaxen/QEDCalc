"""Identify first nontrivial elimination rows in saved VP05 modular plan.

No exact arithmetic and no Fermat execution. Locate the smallest prefix
containing a genuine pivot-row subtraction for a bounded exact smoke test.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT,OUTPUT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--equations",type=Path,default=DEFAULT)
 p.add_argument("--plan",type=Path,default=OUTPUT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_exact_elimination_probe.json"))
 a=p.parse_args()
 plan=json.loads(a.plan.read_text(encoding="utf-8-sig"))
 digest=hashlib.sha256(a.equations.read_bytes()).hexdigest()
 if plan["source_sha256"]!=digest:p.error("Input digest mismatch")
 schedules=[point["schedule"] for point in plan["points"]]
 if not schedules or any(x!=schedules[0] for x in schedules[1:]):p.error("Modular schedules differ")
 sch=schedules[0]
 active=[{"row_zero_based":i,"operations":len(row["operations"]),"owners":[op["owner"] for op in row["operations"]],"lead":row["lead"]} for i,row in enumerate(sch) if row["operations"]]
 first=active[0] if active else None
 result={"rows":len(sch),"rows_with_pivot_elimination":len(active),
   "first_nontrivial_row":first,"first_ten":active[:10],
   "suggested_prefix_rows":first["row_zero_based"]+1 if first else None,
   "within_existing_five_row_smoke_limit":bool(first and first["row_zero_based"]<5),
   "no_symbolic_proof":True}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_EXACT_ELIMINATION_PROBE "+json.dumps({**result,"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
