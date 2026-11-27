"""Exact complementary-pair moment audit; no new IBP or closure claim."""
import argparse
import os
import time
from pathlib import Path
from examples import three_loop_vp05_abc_banana as b

sp=b.sp;old=b.old;p=b.p;n=b.n;gap=b.gap
ROOT=n.BASE/"output"/"vp05_abc_pair_moments27"
SOURCE=b.ROOT/"report_1795776965054678800.json"
SHA="94a7cca21d42f8bce3d68e2f606e63d83bd0eb812b6cc150c9066220560af2bf"
T=(1,0,0,1,0,0,1,0,0,0,0,0)

def combine(*terms):
    row={}
    for scale,part in terms:b.add(row,part,scale)
    return row

def require_equal(a,c,label):
    residual=combine((1,a),(-1,c))
    if residual:raise RuntimeError(label+": "+str(p.encode(residual)))

def compact(P,Q,R,z):
    return {"B":sp.cancel(Q+P/4),"H":sp.cancel(-P/4),
            "C":sp.cancel(R+P*(2-z/4)*(z+8)/6),
            "T":sp.cancel(P*(2+(2-z/4)*sp.Rational(4,3)))}

def calculate(props,target,saved,deadline):
    center,original,lines,maps=b.geometry(props)
    u,v,w,t=lines
    z=old.Z;q=old.MOM[4]
    X=b.sq(w+t);Y=b.sq(u+v)
    inverse=b.s.inverse_polys(props)
    C={b.BASE:sp.S.One};tad={T:sp.S.One}
    def evaluate(poly):
        if time.monotonic()>=deadline:raise TimeoutError("Pair moment budget")
        old.memory_guard()
        avg=b.average(b.covariance(sp.sympify(poly)),lines)
        row,_=b.expand_integral(avg,original,props,inverse)
        top,lower,remaining,proofs=b.reduce_pinches(row,props,deadline)
        if remaining:raise RuntimeError("Unresolved pair-moment pinches")
        return combine((1,top),(1,lower))
    # Reconstruct original physical A/B/C, not just the proposed formulas.
    props_poly=b.s.polys(props)
    actual={}
    for name,key,item in zip("ABC",gap.TARGETS,saved["targets"]):
        if item["name"]!=name or tuple(item["integral"])!=key:raise RuntimeError("Saved target scope")
        raw=sp.sympify(sp.prod(props_poly[i]**(-x) for i,x in enumerate(key) if x<0))
        actual[name]=evaluate(b.transform(raw,center))
        if p.decode(item["pinch_unresolved"]):raise RuntimeError("Saved unresolved pinches")
        require_equal(actual[name],combine((1,p.decode(item["top"])),(1,p.decode(item["pinch_reduced"]))),"Saved "+name)
    require_equal(actual["B"],evaluate(X**2),"B definition")
    require_equal(actual["C"],C,"C definition")
    H=evaluate(X*Y);M=evaluate(X)
    require_equal(M,combine(((z+8)/6,C),(sp.Rational(4,3),tad)),"First pair moment")
    require_equal(evaluate(X*(b.sq(u)-1)),combine((2,tad)),"Pinched X moment")
    require_equal(actual["A"],combine((2-z/4,M),(sp.Rational(1,4),actual["B"]),(-sp.Rational(1,4),H),(2,tad)),"A identity")
    P,Q,R=(target[k] for k in gap.TARGETS)
    coefficients=compact(P,Q,R,z)
    moments={"B":actual["B"],"H":H,"C":C,"T":tad}
    remainder=combine(*[(coefficients[name],row) for name,row in moments.items()])
    direct=combine(*[(target[k],actual[name]) for name,k in zip("ABC",gap.TARGETS)])
    require_equal(remainder,direct,"Compact target replay")
    require_equal(remainder,p.decode(saved["combined"]["remainder"]),"Saved banana remainder")
    return {"verified_identities":["B_definition","C_definition","first_pair_moment","pinched_X_moment","A_identity","compact_target","saved_remainder"],
            "coefficients":{k:str(x) for k,x in coefficients.items()},
            "moments":{k:p.encode(row) for k,row in moments.items()},
            "first_moment":p.encode(M),"remainder":p.encode(remainder),"analytic_zero":not remainder}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Banana SHA")
        saved=gap.read(SOURCE)
        if saved["status"]!="VP05_ABC_BANANA_RESIDUAL_NOT_PROOF" or saved["analytic_replay_verified"] is not True or saved["kernel_sha256"]!=b.f.e.b.c.PIN:raise RuntimeError("Banana scope")
        pins={Path(k):d for k,d in saved["inputs"].items()};pins[SOURCE]=SHA
        if pins.get(b.SOURCE)!=b.SHA or any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input SHA")
        target=p.decode(gap.read(b.SOURCE)["target"])
        if set(target)!=set(gap.TARGETS):raise RuntimeError("Target scope")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=b.f.e.b.c.PIN:raise RuntimeError("Kernel")
        result=calculate(props,target,saved["result"],deadline)
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_PAIR_MOMENTS_ANALYTIC_PROVEN_NOT_CLOSURE" if result["analytic_zero"] else "VP05_ABC_PAIR_MOMENTS_VERIFIED_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):d for k,d in pins.items()},"result":result,
                 "kernel_sha256":b.f.e.b.c.PIN,"full_closure_proven":False,"registry_changed":False,"new_ibp_rows":0}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=b.prior.physical.scope.c.save(dest,payload)
        b.v.log(status,verified_identities=result["verified_identities"],coefficients=result["coefficients"],
                compact_nonzero_terms=sum(x!="0" for x in result["coefficients"].values()),expanded_remainder_terms=len(result["remainder"]),
                report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
