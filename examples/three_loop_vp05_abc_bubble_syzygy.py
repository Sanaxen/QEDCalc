"""Low-degree polynomial syzygy search for the two-bubble IBP system."""
import argparse
import os
import time
from pathlib import Path
from examples import three_loop_vp05_abc_bubble_pinches as h

a=h.a;b=h.b;m=h.m;sp=h.sp;n=h.n;gap=h.gap;old=h.old
x,y,d,z=a.x,a.y,a.d,a.z
ROOT=n.BASE/"output"/"vp05_abc_bubble_syzygy30"
SOURCE=h.ROOT/"report_1795815760635920600.json"
SHA="4a78f565232dc9f264e970dedb89e36f86c94b5c940bd659e3a0e6f59c313a89"

def vectors(degree):
    mon=[x**i*y**j for i in range(degree+1) for j in range(degree+1-i)]
    pairs=[(w,sp.S.Zero) for w in mon]+[(sp.S.Zero,w) for w in mon]
    def constraints(A,C):
        vx=2*x*A+a.S*C;vy=a.S*A+2*y*C
        return [sp.Poly(vx.subs(x,k),y) for k in (0,4)]+[sp.Poly(vy.subs(y,k),x) for k in (0,4)]
    columns=[]
    for A,C in pairs:
        columns.append([p.nth(i) for p in constraints(A,C) for i in range(degree+2)])
    matrix=sp.Matrix(columns).T
    for vec in matrix.nullspace():
        A=sp.expand(sum(c*w[0] for c,w in zip(vec,pairs)))
        C=sp.expand(sum(c*w[1] for c,w in zip(vec,pairs)))
        if matrix*vec!=sp.zeros(matrix.rows,1):
            if any(sp.cancel(v) for v in matrix*vec):raise RuntimeError("Syzygy replay")
        yield A,C

def calculate(saved,pair,deadline):
    rules={tuple(r["key"]):sp.cancel(sp.sympify(r["coefficient"],locals={"d":d,"z":z})) for r in saved["rules"]}
    target=h.decode(saved["target"]);base=[h.decode(r) for r in saved["rows"]]
    expected=[h.substitute(r,rules) for _,r in a.sources()]
    if base!=expected:raise RuntimeError("Saved pinch source replay")
    if a.reduce_exact(base,target)[0]!=h.decode(saved["remainder"]):raise RuntimeError("Saved pinch residual replay")
    # The first moment identity was independently verified in the pair audit.
    moment={("JJ",1,0):sp.S.One,("JJ",0,0):-(z+8)/6,("T",0,0):-sp.Rational(4,3)}
    rows=base+[moment];records=[];missing=[]
    for degree in (1,2,3,4):
        old.memory_guard()
        if time.monotonic()>=deadline:raise TimeoutError("Syzygy budget")
        count=0
        for A,C in vectors(degree):
            raw=a.outer(A,C)
            need=set(k for k in raw if k[0]=="UJ")-set(rules)
            if need:
                missing.append({"degree":degree,"A":str(A),"C":str(C),"missing":[list(k) for k in sorted(need)]})
                continue
            row=h.substitute(raw,rules)
            if not row or row in rows:continue
            rows.append(row);count+=1
            records.append({"degree":degree,"A":str(A),"C":str(C),"row":a.encode(row)})
        rem,used,rank=a.reduce_exact(rows,target)
        b.v.log("VP05_BUBBLE_SYZYGY_DEGREE",degree=degree,new_rows=count,rank=rank,remainder=a.encode(rem),unchanged=rem==target)
        if not rem:break
    # Compare first moment's physical meaning against the pinned pair report.
    if "first_pair_moment" not in pair["verified_identities"]:raise RuntimeError("Missing first moment proof")
    return {"source_rows":len(rows),"rank":rank,"columns":len(set(target).union(*(set(r) for r in rows))),
            "syzygies":records,"unsupported":missing,"first_moment_row":a.encode(moment),
            "target":a.encode(target),"remainder":a.encode(rem),"unchanged":rem==target,
            "multipliers":[[i,str(v)] for i,v in sorted(used.items())],"source_replay_verified":True,
            "physical_original_row_replay":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Pinch SHA")
        data=gap.read(SOURCE)
        if data["status"]!="VP05_ABC_BUBBLE_PINCH_RESIDUAL_NOT_PROOF":raise RuntimeError("Pinch scope")
        pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
        if pins.get(h.SOURCE)!=h.SHA or pins.get(a.SOURCE)!=a.SHA or any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
        pair=gap.read(a.SOURCE)
        if pair["status"]!="VP05_ABC_PAIR_MOMENTS_VERIFIED_NOT_PROOF":raise RuntimeError("Pair scope")
        result=calculate(data["result"],pair["result"],deadline)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_BUBBLE_SYZYGY_FORMAL_ZERO_REVIEW_REQUIRED" if not result["remainder"] else "VP05_ABC_BUBBLE_SYZYGY_RESIDUAL_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):v for k,v in pins.items()},"result":result,"full_closure_proven":False,"registry_changed":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=b.prior.physical.scope.c.save(dest,payload)
        b.v.log(status,source_rows=result["source_rows"],rank=result["rank"],columns=result["columns"],
                syzygies=len(result["syzygies"]),unsupported=len(result["unsupported"]),remainder=result["remainder"],
                unchanged=result["unchanged"],source_replay_verified=True,physical_original_row_replay=False,
                report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
