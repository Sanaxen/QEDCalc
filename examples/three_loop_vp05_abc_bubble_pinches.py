"""Reduce oriented UJ columns by independently mapped physical tadpoles."""
import argparse
import os
import time
from pathlib import Path
from examples import three_loop_vp05_abc_two_bubble as a

m=a.m;b=a.b;sp=a.sp;old=a.old;n=a.n;p=a.p;gap=a.gap
ROOT=n.BASE/"output"/"vp05_abc_bubble_pinches29"
SOURCE=a.ROOT/"report_1795815561200739700.json"
SHA="36ac101f9c240543ddc331e6b38a121311e14cd782d4e874b32eb75ba9da2149"

def decode(items):
    return {tuple(k):sp.cancel(sp.sympify(v,locals={"d":a.d,"z":a.z})) for k,v in items}

def substitute(row,rules):
    out={}
    for k,v in row.items():
        if k[0]=="UJ":a.add(out,("T",0,0),v*rules[k])
        else:a.add(out,k,v)
    return out

def calculate(props,saved,deadline):
    original_rows=list(a.sources())
    if saved["sources"]!=[{"spec":list(k),"row":a.encode(r)} for k,r in original_rows]:
        raise RuntimeError("Saved IBP source replay")
    target=decode(saved["target"])
    if a.reduce_exact([r for _,r in original_rows],target)[0]!=decode(saved["remainder"]):
        raise RuntimeError("Saved residual replay")
    _,original,lines,_=b.geometry(props)
    u,v,w,t=lines
    X=b.sq(w+t);Y=b.sq(u+v)
    inverse=b.s.inverse_polys(props)
    # U J(Y): retain u,v and w²-1 squared, remove t.
    # (u,v,w) independent; K=q-u-v, t=K-w.
    if abs(sp.Matrix([u,v,w]).jacobian(old.MOM[:3]).det())!=1:
        raise RuntimeError("Pinch Jacobian")
    if b.f.a.CAND!=m.T:raise RuntimeError("Tadpole scope")
    rules={};proofs=[]
    keys=sorted({k for _,r in original_rows for k in r if k[0]=="UJ"}|{("UJ",0,0)})
    for key in keys:
        if time.monotonic()>=deadline:raise TimeoutError("Pinch budget")
        old.memory_guard()
        _,i,j=key
        # Expand with original four-line base first, then multiply by
        # D8/D7 to obtain the pinched/dotted denominator.
        row,poly=b.expand_integral(sp.expand(X**i*Y**j),original,props,inverse)
        shifted={}
        for k,c in row.items():
            ex=list(k);ex[6]+=1;ex[7]-=1
            b.add(shifted,{tuple(ex):c},1)
        reduced,remaining,cert=b.s.reduce_terms(shifted,{m.T},props,deadline)
        if remaining or set(reduced)-{m.T}:
            raise RuntimeError("Unresolved UJ moment "+str(key)+": "+str(p.encode(remaining)))
        value=sp.cancel(reduced.get(m.T,0));rules[key]=value
        proofs.append({"key":list(key),"polynomial":str(poly),"physical_row":p.encode(shifted),
                       "factorized_proofs":cert,"coefficient":str(value)})
        b.v.log("VP05_BUBBLE_PINCH_MOMENT",key=list(key),coefficient=str(value),terms=len(shifted))
    if sp.cancel(rules[("UJ",0,0)]-(a.d/2-1))!=0:raise RuntimeError("Dotted tadpole normalization")
    rows=[substitute(r,rules) for _,r in original_rows]
    remainder,used,rank=a.reduce_exact(rows,target)
    return {"rules":proofs,"rows":[a.encode(r) for r in rows],"rank":rank,
            "columns_before":saved["columns"],"columns_after":len(set(target).union(*(set(r) for r in rows))),
            "target":a.encode(target),"remainder":a.encode(remainder),"unchanged":remainder==target,
            "multipliers":[[i,str(v)] for i,v in sorted(used.items())],
            "source_replay_verified":True,"physical_original_row_replay":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Two bubble SHA")
        data=gap.read(SOURCE)
        if data["status"]!="VP05_ABC_TWO_BUBBLE_RESIDUAL_NOT_PROOF":raise RuntimeError("Two bubble scope")
        pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
        if pins.get(a.SOURCE)!=a.SHA or any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=b.f.e.b.c.PIN:raise RuntimeError("Kernel")
        result=calculate(props,data["result"],deadline)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_BUBBLE_PINCH_FORMAL_ZERO_REVIEW_REQUIRED" if not result["remainder"] else "VP05_ABC_BUBBLE_PINCH_RESIDUAL_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):v for k,v in pins.items()},"result":result,"full_closure_proven":False,"registry_changed":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=b.prior.physical.scope.c.save(dest,payload)
        b.v.log(status,source_rows=len(result["rows"]),pinch_rules=len(result["rules"]),rank=result["rank"],
                columns_before=result["columns_before"],columns_after=result["columns_after"],remainder=result["remainder"],
                unchanged=result["unchanged"],source_replay_verified=True,physical_original_row_replay=False,
                report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
