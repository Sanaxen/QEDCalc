"""Bounded two-bubble polynomial IBP system (exact QQ(d,z)).
Dotted tadpole products are retained as independent formal columns except
the constant, which follows from the one-loop tadpole IBP.
Nonzero residual is not an independence or closure certificate.
"""
import argparse
import os
import time
from pathlib import Path
from examples import three_loop_vp05_abc_pair_moments as m

b=m.b;sp=m.sp;old=m.old;n=m.n;p=m.p;gap=m.gap
ROOT=n.BASE/"output"/"vp05_abc_two_bubble28"
SOURCE=m.ROOT/"report_1795814963636843000.json"
SHA="288c33f2e8864cdf079bcea8372b30ceb6aee436920cd74e33c76dac952c7870"
x,y=sp.symbols("X Y")
d,z=old.D,old.Z
S=x+y-z
F=x*(x-4);G=y*(y-4)
N=lambda a:(d-4)*a+4

def check_inner():
    # D=w²-1, E=(K-w)²-1. Equal-mass interchange identifies the two dots.
    D,E=sp.symbols("D E")
    # u divergence after swapping the E-dotted term: numerator 3D+E+4-X.
    u2=D+1;v2=E+1;uv=(x-u2-v2)/2
    assert sp.expand(2*u2-2*uv-(3*D+E+4-x))==0
    # radial derivative numerator 2 K.v = X+E-D.
    assert sp.expand(2*(v2+uv)-(x+E-D))==0
    J,L,U=sp.symbols("J L U")
    inner=(d-3)*J+(x-4)*L-U
    radial=-x*L-J+U  # 2X J'
    if sp.expand((x-4)*radial-(N(x)*J-4*U)+x*inner)!=0:
        raise RuntimeError("Bubble ODE replay")
    return True

def add(row,key,value):
    v=sp.cancel(row.get(key,0)+value)
    if v:row[key]=v
    else:row.pop(key,None)

def polynomial(row,poly,kind):
    # J(X)J(Y) symmetric; U J(Y) is oriented (U J(X) swapped first).
    for (i,j),c in sp.Poly(sp.expand(poly),x,y).terms():
        if kind=="JJ":key=("JJ",max(i,j),min(i,j))
        elif i==j==0:
            add(row,("T",0,0),c*(d/2-1));continue
        else:key=("UJ",i,j)
        add(row,key,c)

def outer(a,c):
    # Vector a(X,Y) K + c(X,Y)(K-q).
    vx=2*x*a+S*c;vy=S*a+2*y*c
    div=d*(a+c)+2*x*sp.diff(a,x)+S*sp.diff(a,y)+S*sp.diff(c,x)+2*y*sp.diff(c,y)
    lx=sp.cancel(vx/(2*F));ly=sp.cancel(vy/(2*G))
    if any(sp.denom(v).has(x,y) for v in (lx,ly)):
        raise RuntimeError("Uncleared bubble derivative")
    row={}
    polynomial(row,div+lx*N(x)+ly*N(y),"JJ")
    polynomial(row,-4*lx,"UJ")
    polynomial(row,(-4*ly).subs({x:y,y:x},simultaneous=True),"UJ")
    return row

def sources():
    # tangent to Y: (2Y,-S); tangent to X: (-S,2X).
    # Multipliers guarantee divisibility without introducing rational weights.
    for i in range(3):
        for j in range(3-i):
            w=x**i*y**j
            yield ("tangent_Y",i,j),outer(2*y*F*w,-S*F*w)
            yield ("radial",i,j),outer(F*G*w,0)

def order(k):
    kind,i,j=k
    # eliminate high moments first, then oriented single-bubble moments.
    return (i+j,kind=="UJ",i,j,kind)

def reduce_exact(rows,target):
    piv={}
    for index,row0 in enumerate(rows):
        row=dict(row0);certificate={index:sp.S.One}
        while row:
            k=max(row,key=order)
            if k not in piv:
                scale=1/row[k]
                piv[k]=({q:sp.cancel(v*scale) for q,v in row.items()},
                        {q:sp.cancel(v*scale) for q,v in certificate.items()})
                break
            rr,cc=piv[k];scale=row[k]
            for q,v in rr.items():add(row,q,-scale*v)
            for q,v in cc.items():add(certificate,q,-scale*v)
    # Reduce every reducible column, not just the leading column.
    row=dict(target);used={}
    for k in sorted(piv,key=order,reverse=True):
        if k not in row:continue
        rr,cc=piv[k];scale=row[k]
        for q,v in rr.items():add(row,q,-scale*v)
        for q,v in cc.items():add(used,q,scale*v)
    replay=dict(row)
    for i,c in used.items():
        for k,v in rows[i].items():add(replay,k,c*v)
    if replay!=target:raise RuntimeError("Exact source replay")
    return row,used,len(piv)

def encode(row):
    return [[list(k),str(v)] for k,v in sorted(row.items())]

def calculate(saved):
    check_inner()
    coeff={k:sp.cancel(sp.sympify(v,locals={"d":d,"z":z})) for k,v in saved["coefficients"].items()}
    if set(coeff)!={"B","H","C","T"}:raise RuntimeError("Moment scope")
    target={("JJ",2,0):coeff["B"],("JJ",1,1):coeff["H"],("JJ",0,0):coeff["C"],("T",0,0):coeff["T"]}
    # Verify that the formal target reproduces the earlier physical moment rows.
    physical=m.combine(*[(coeff[k],p.decode(saved["moments"][k])) for k in coeff])
    m.require_equal(physical,p.decode(saved["remainder"]),"Pinned physical target")
    specs=list(sources());rows=[r for _,r in specs]
    remainder,used,rank=reduce_exact(rows,target)
    return {"inner_ode_verified":True,"source_replay_verified":True,"target":encode(target),
            "sources":[{"spec":list(k),"row":encode(r)} for k,r in specs],
            "rank":rank,"columns":len(set().union(*[set(r) for r in rows],set(target))),
            "remainder":encode(remainder),"multipliers":[[i,str(v)] for i,v in sorted(used.items())],
            "physical_target_replay":True,"physical_original_row_replay":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic()
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Pair moment SHA")
        saved=gap.read(SOURCE)
        if saved["status"]!="VP05_ABC_PAIR_MOMENTS_VERIFIED_NOT_PROOF" or saved["kernel_sha256"]!=b.f.e.b.c.PIN:raise RuntimeError("Pair moment scope")
        pins={Path(k):v for k,v in saved["inputs"].items()};pins[SOURCE]=SHA
        if pins.get(m.SOURCE)!=m.SHA or any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=b.f.e.b.c.PIN:raise RuntimeError("Kernel")
        b.geometry(props);old.memory_guard()
        result=calculate(saved["result"])
        if time.monotonic()-start>args.hours*3600:raise TimeoutError("Sampled time budget")
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_TWO_BUBBLE_FORMAL_ZERO_REVIEW_REQUIRED" if not result["remainder"] else "VP05_ABC_TWO_BUBBLE_RESIDUAL_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):v for k,v in pins.items()},"result":result,"full_closure_proven":False,"registry_changed":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=b.prior.physical.scope.c.save(dest,payload)
        b.v.log(status,source_rows=len(result["sources"]),rank=result["rank"],columns=result["columns"],remainder=result["remainder"],
                inner_ode_verified=True,source_replay_verified=True,physical_target_replay=True,physical_original_row_replay=False,
                report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
