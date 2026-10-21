"""Bounded exact VP05 group lift: compressed row as symbolic witness-row combination.

Default one small group. Check each coefficient column exactly over Q(z,d).
Do not claim a full 528-row proof unless all 166 groups and combined target
have been verified in a separate subsequent stage.
"""
from __future__ import annotations
import argparse,hashlib,json,multiprocessing as mp,queue
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS
from examples.three_loop_sector203_exact_prefix_smoke import parse_coeff
from examples.three_loop_sector203_fermat_gaussian_pilot import order

OUT=Path("output/three_loop_integral_family_audit/vp05_exact_group_lift.json")

def coefficients(row,z,d):
    out={}
    for t in row["terms"]:
        k=tuple(t["key"])
        out[k]=sp.cancel(out.get(k,0)+parse_coeff(t["coefficient"],z,d))
    return {k:v for k,v in out.items() if v!=0}

def exact_solve(vectors,target):
    # Transposed augmented elimination: each equation is one coefficient
    # column; unknowns are the original witness-row multipliers.
    m=len(vectors);basis={}
    for col in sorted(set(target).union(*(set(x) for x in vectors)),key=order):
        expr=[vectors[j].get(col,sp.Integer(0)) for j in range(m)]
        residual=target.get(col,sp.Integer(0))
        for pivot,(row,rhs) in sorted(basis.items()):
            factor=sp.cancel(expr[pivot])
            if factor==0:continue
            expr=[sp.cancel(a-factor*b) for a,b in zip(expr,row)]
            residual=sp.cancel(residual-factor*rhs)
        nonzero=next((j for j,v in enumerate(expr) if sp.cancel(v)!=0),None)
        if nonzero is None:
            if sp.cancel(residual)!=0:raise AssertionError(("inconsistent exact source span",col))
            continue
        divisor=expr[nonzero]
        basis[nonzero]=([sp.cancel(v/divisor) for v in expr],sp.cancel(residual/divisor))
    answer=[sp.Integer(0)]*m
    for pivot,(row,rhs) in sorted(basis.items(),reverse=True):
        answer[pivot]=sp.cancel(rhs-sum((row[j]*answer[j] for j in range(pivot+1,m)),sp.Integer(0)))
    rebuilt={}
    for coeff,vec in zip(answer,vectors):
        if coeff==0:continue
        for k,v in vec.items():rebuilt[k]=rebuilt.get(k,0)+coeff*v
    wrong=[k for k in set(rebuilt)|set(target) if sp.cancel(rebuilt.get(k,0)-target.get(k,0))!=0]
    if wrong:raise AssertionError(("symbolic source replay failed",wrong[:3]))
    return answer,len(basis)

def work(args,resultq):
    try:
        raw=args.equations.read_bytes()
        wr=args.witness.read_bytes()
        src=json.loads(raw.decode("utf-8-sig"))["rows"]
        witness=json.loads(wr.decode("utf-8-sig"))["rows"]
        if len(src)!=166 or len(witness)!=528:raise ValueError("Unexpected source sizes")
        z,d=sp.symbols("z d")
        all_results=[]
        for i in range(args.start,args.start+args.count):
            ids=src[i]["original_rows"]
            if not ids or any(type(j)!=int or j<0 or j>=528 for j in ids):
                raise ValueError("Malformed witness-list source indices")
            if len(ids)>args.max_group_size:
                raise ValueError(f"Group {i} size {len(ids)} exceeds safety cap {args.max_group_size}")
            vectors=[coefficients(witness[j],z,d) for j in ids]
            target=coefficients(src[i],z,d)
            weights,rank=exact_solve(vectors,target)
            terms=[{"witness_list_index":j,"system_row_index":witness[j]["row_index"],
                "coefficient":str(c)} for j,c in zip(ids,weights) if c!=0]
            all_results.append({"compressed_row":i,"group_size":len(ids),"rank":rank,
                "source_support":len(terms),"exact_replay_verified":True,"weights":terms})
            print("VP05_EXACT_GROUP_LIFT_ROW "+json.dumps({
                "row":i,"group_size":len(ids),"rank":rank,
                "source_support":len(terms),"exact_replay_verified":True}),flush=True)
        report={"stage":"exact_group_lift_subset","compressed_sha256":hashlib.sha256(raw).hexdigest(),
            "witness_sha256":hashlib.sha256(wr).hexdigest(),"start":args.start,
            "count":args.count,"rows":all_results,
            "all_166_exact_provenance_verified":False,
            "original_528_row_target_replay_verified":False}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        tmp=args.output.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        tmp.replace(args.output)
        resultq.put(("ok",len(all_results)))
    except Exception as exc:resultq.put(("error",type(exc).__name__+": "+str(exc)))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--equations",type=Path,default=DEFAULT)
    p.add_argument("--witness",type=Path,default=WITNESS)
    p.add_argument("--output",type=Path,default=OUT)
    p.add_argument("--start",type=int,default=82)
    p.add_argument("--first-multi",action="store_true",help="Select smallest multi-source group deterministically")
    p.add_argument("--count",type=int,default=1)
    p.add_argument("--max-group-size",type=int,default=4)
    p.add_argument("--timeout",type=int,default=120)
    a=p.parse_args()
    if a.first_multi:
        rows=json.loads(a.equations.read_text(encoding="utf-8-sig"))["rows"]
        candidates=[(len(row["original_rows"]),i) for i,row in enumerate(rows) if len(row["original_rows"])>1 and len(row["original_rows"])<=a.max_group_size]
        if not candidates:p.error("No multi-source group within --max-group-size")
        a.start=min(candidates)[1]
        a.count=1
        print("VP05_EXACT_GROUP_LIFT_SELECTED "+json.dumps({"row":a.start,"group_size":len(rows[a.start]["original_rows"])}),flush=True)
    if not 0<=a.start<166 or not 1<=a.count<=10 or a.start+a.count>166:
        p.error("Invalid bounded group range")
    if not 1<=a.max_group_size<=68:p.error("Invalid group cap")
    if not 1<=a.timeout<=3600:p.error("Invalid timeout")
    q=mp.Queue();proc=mp.Process(target=work,args=(a,q));proc.start();proc.join(a.timeout)
    if proc.is_alive():
        proc.terminate();proc.join()
        print("VP05_EXACT_GROUP_LIFT_STATUS "+json.dumps({"status":"TIMEOUT","symbolic_proof":False}),flush=True)
        raise SystemExit(2)
    try:status,payload=q.get(timeout=3)
    except queue.Empty:raise SystemExit("Worker exited without status")
    if status!="ok":
        print("VP05_EXACT_GROUP_LIFT_STATUS "+json.dumps({"status":"FAILED","reason":payload}),flush=True)
        raise SystemExit(1)
    print("VP05_EXACT_GROUP_LIFT_STATUS "+json.dumps({
        "status":"PASS","verified_groups":payload,"output":str(a.output),
        "all_166_exact_provenance_verified":False,
        "original_528_row_target_replay_verified":False}),flush=True)
if __name__=="__main__":main()
