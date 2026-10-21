"""Bounded exact rational-function pivot smoke test for VP05's saved 166-row plan.

Runs only an explicitly small prefix of exact compressed equations. Verifies
each computed pivot row as a symbolic linear combination of its source prefix.
No full-system solve or target proof is attempted.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_fermat_gaussian_pilot import order
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT,OUTPUT

def parse_coeff(expr,z,d):
    # Sympy parser is fed trusted local QEDCalc-generated JSON, not user code.
    symbols={"z":z,"d":d}
    value=sp.sympify(expr.replace("^","**"),locals=symbols)
    if value.free_symbols-{z,d}:raise ValueError("Unknown coefficient symbols")
    return value

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--plan",type=Path,default=OUTPUT)
    ap.add_argument("--rows",type=int,default=3)
    ap.add_argument("--max-seconds",type=float,default=30)
    args=ap.parse_args()
    if not 1<=args.rows<=6:ap.error("Exact prefix smoke test is strictly limited to 1..6 rows")
    if args.max_seconds<=0:ap.error("--max-seconds must be positive")
    source=json.loads(args.equations.read_text(encoding="utf-8-sig"))
    plan=json.loads(args.plan.read_text(encoding="utf-8-sig"))
    import hashlib
    if hashlib.sha256(args.equations.read_bytes()).hexdigest()!=plan["source_sha256"]:
        ap.error("Reverse certificate plan source digest mismatch")
    if not plan["shared_pivot_schedule"]:ap.error("Modular plan did not share schedule")
    rows=source["rows"][:args.rows]
    schedule=plan["points"][0]["schedule"][:args.rows]
    z,d=sp.symbols("z d")
    normalized={}
    combinations={}
    start=time.monotonic()
    for i,row in enumerate(rows):
        current={}
        for t in row["terms"]:
            k=tuple(t["key"])
            current[k]=current.get(k,0)+parse_coeff(t["coefficient"],z,d)
        coeffs={i:sp.Integer(1)}
        ops=schedule[i]["operations"]
        for op in ops:
            owner=op["owner"];key=tuple(op["pivot"])
            factor=sp.cancel(current.get(key,sp.Integer(0)))
            for col,value in normalized[owner].items():
                current[col]=sp.cancel(current.get(col,0)-factor*value)
            current={col:v for col,v in current.items() if v!=0}
            for j,val in combinations[owner].items():
                coeffs[j]=sp.cancel(coeffs.get(j,0)-factor*val)
            if time.monotonic()-start>args.max_seconds:raise TimeoutError("Exact-prefix budget reached after operation")
        lead=tuple(schedule[i]["lead"])
        if lead not in current or sp.cancel(current[lead])==0:
            raise AssertionError(("invalid symbolic pivot",i,lead))
        if min(current,key=order)!=lead:
            raise AssertionError(("symbolic lead differs from sampled lead",i,lead))
        divisor=current[lead]
        normalized[i]={k:sp.cancel(v/divisor) for k,v in current.items()}
        combinations[i]={j:sp.cancel(v/divisor) for j,v in coeffs.items()}
        replay={}
        for j,multiplier in combinations[i].items():
            for t in rows[j]["terms"]:
                col=tuple(t["key"])
                replay[col]=replay.get(col,0)+multiplier*parse_coeff(t["coefficient"],z,d)
        diffs={col:sp.cancel(replay.get(col,0)-normalized[i].get(col,0))
               for col in set(replay)|set(normalized[i])}
        if any(v!=0 for v in diffs.values()):
            raise AssertionError(("symbolic original-prefix replay failed",i))
        if time.monotonic()-start>args.max_seconds:raise TimeoutError("Exact-prefix budget reached")
        print("VP05_EXACT_PREFIX_ROW "+json.dumps({
            "row_zero_based":i,"normalized_columns":len(normalized[i]),
            "source_rows_in_certificate":len(combinations[i]),"pivot_elimination_operations":len(ops),"symbolic_source_replay_verified":True,
            "full_target_proof":False}),flush=True)
    print("VP05_EXACT_PREFIX_SUMMARY "+json.dumps({
        "rows_verified":args.rows,"symbolic_replay_all":True,
        "target_symbolic_proof":False,"original_528_row_replay":False}),flush=True)
if __name__=="__main__":main()
