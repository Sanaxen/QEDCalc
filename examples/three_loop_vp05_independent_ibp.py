"""Independent streamed VP05 IBP generator, restricted diagnostic only.

Uses Kira's propagator convention P_i=q_i^2-m_i^2, m2=1.
No LI, symmetry, zero-sector assumptions, or full closure promotion.
"""
import argparse,hashlib,itertools,json,os,time
from pathlib import Path
import sympy as sp
from three_loop.master_basis_api import build_family_spec
ROOT=Path(__file__).resolve().parents[1]

SECTORS=(69,196,200)
Z=sp.Symbol("z")
D=sp.Symbol("d")
MOM=sp.symbols("k l r p q")
PAIRS=tuple((i,j) for i in range(3) for j in range(i,5))
X=sp.symbols("x0:12")
Y=sp.symbols("P0:12")
POINTS=((1000003,17,7),(1000033,19,11))
MAX_TERMS=500000
MAX_FILL=5000

def dot(i,j):
    a,b=sorted((i,j))
    if a<3:return X[PAIRS.index((a,b))]
    return {(3,3):sp.S.One,(3,4):-Z/2,(4,4):Z}[a,b]

def build_kernel(propagators):
    if len(propagators)!=12:raise ValueError("Need twelve propagators")
    vectors=[]
    polys=[]
    for prop in propagators:
        expr=sp.sympify(prop.momentum,locals=dict(zip(map(str,MOM),MOM)))
        v=[expr.coeff(m) for m in MOM]
        if sp.expand(expr-sum(c*m for c,m in zip(v,MOM)))!=0 or any(not c.is_Rational for c in v):
            raise ValueError("Nonlinear momentum")
        if prop.mass not in ("0","m2"):raise ValueError("Unsupported mass")
        vectors.append(v)
        polys.append(sp.expand(sum(v[i]*v[j]*dot(i,j) for i in range(5) for j in range(5))-(1 if prop.mass=="m2" else 0)))
    matrix=sp.Matrix([[p.coeff(x) for x in X] for p in polys])
    constants=sp.Matrix([p.subs(dict.fromkeys(X,0)) for p in polys])
    sol=matrix.inv()*(sp.Matrix(Y)-constants)
    sub=dict(zip(X,sol))
    if any(sp.expand(p.subs(sub,simultaneous=True)-y)!=0 for p,y in zip(polys,Y)):
        raise RuntimeError("Propagator inversion failed")
    result={}
    for i in range(3):
        for j in range(5):
            entries=[]
            for v,p in zip(vectors,polys):
                raw=sp.expand(2*v[i]*sum(v[t]*dot(j,t) for t in range(5)))
                # Independent component-level derivative of the scalar products.
                check=sp.expand(sum(p.diff(x)*((dot(j,b) if a==i else 0)+(dot(a,j) if b==i else 0)) for x,(a,b) in zip(X,PAIRS)))
                if sp.expand(raw-check)!=0:raise RuntimeError("Derivative cross-check failed")
                val=sp.expand(raw.subs(sub,simultaneous=True))
                cs=tuple(val.coeff(y) for y in Y)
                c0=sp.expand(val-sum(c*y for c,y in zip(cs,Y)))
                if c0.free_symbols-{Z} or any(c.free_symbols-{Z} for c in cs):
                    raise RuntimeError("Non-affine derivative")
                entries.append((c0,cs))
            result[i,j]=entries
    return result

def compositions(total,n):
    if n==1:
        yield (total,);return
    for x in range(total+1):
        for t in compositions(total-x,n-1):yield (x,)+t

def seeds(sec,smax):
    pos=[i for i in range(12) if sec&(1<<i)]
    neg=[i for i in range(12) if not sec&(1<<i)]
    for s in range(smax+1):
        for d in range(3):
            for dots in compositions(d,len(pos)):
                for nums in compositions(s,len(neg)):
                    a=[0]*12
                    for i,x in zip(pos,dots):a[i]=1+x
                    for i,x in zip(neg,nums):a[i]=-x
                    yield tuple(a)

def row(a,entries,i,j,dim):
    out={}
    def add(key,c):
        out[key]=out.get(key,0)+c
    if i==j:add(a,dim)
    for h,(c0,cs) in enumerate(entries):
        if not a[h]:continue
        b=list(a);b[h]+=1
        if c0:add(tuple(b),-a[h]*c0)
        for k,c in enumerate(cs):
            if c:
                t=b.copy();t[k]-=1
                add(tuple(t),-a[h]*c)
    return {k:v for k,v in out.items() if v}

def evaluate(expr,p,z):
    n,d=sp.fraction(sp.cancel(expr.subs(Z,z))) if hasattr(expr,"subs") else (expr,1)
    return int(n)%p*pow(int(d)%p,-1,p)%p

def insert(r,pivots,p,stored):
    cur={k:v%p for k,v in r.items() if v%p}
    while cur:
        # deterministic lexicographic ordering, not Kira's integral ordering
        key=min(cur)
        if key not in pivots:
            if stored+len(cur)>MAX_TERMS:raise RuntimeError("Stored term cap")
            inv=pow(cur[key],-1,p)
            pivots[key]={k:v*inv%p for k,v in cur.items()}
            return len(cur),True
        c=cur[key]
        for k,v in pivots[key].items():
            x=(cur.get(k,0)-c*v)%p
            if x:cur[k]=x
            else:cur.pop(k,None)
        if len(cur)>MAX_FILL:raise RuntimeError("Fill cap")
    return 0,False

def atomic(path,obj):
    if path.exists():raise RuntimeError("Checkpoint already exists")
    tmp=path.with_suffix(".tmp")
    with tmp.open("x",encoding="utf-8") as f:
        json.dump(obj,f,separators=(",",":"));f.flush();os.fsync(f.fileno())
    if path.exists():raise RuntimeError("Checkpoint appeared during write")
    tmp.rename(path)

def memory_guard():
    # Windows host physical memory, conservative stop independent of WSL.
    if os.name=="nt":
        import ctypes
        class MemoryStatus(ctypes.Structure):
            _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(name,ctypes.c_ulonglong) for name in ("total","available","total_page","available_page","total_virtual","available_virtual","extended")]
        info=MemoryStatus();info.length=ctypes.sizeof(info)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
            raise RuntimeError("Windows RAM measurement failed")
        if info.available<8*1024**3:raise RuntimeError("Windows available RAM below 8 GiB")
    else:
        info=dict((x.split(":")[0],int(x.split()[1])) for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith(("MemAvailable:","SwapTotal:","SwapFree:","MemTotal:")))
        if info["MemAvailable"]<8*1024**2 or info["MemTotal"]-info["MemAvailable"]>=22*1024**2 or info["SwapTotal"]-info["SwapFree"]>=8*1024**2:raise RuntimeError("Linux RAM/swap guard")

def run_sector(sec,kernel,smax,budget,dest):
    dest.mkdir(exist_ok=True)
    # Each numerator shell has a durable, exclusive independent output.
    # No large in-memory matrix: finite-field pivot state bounded by term cap.
    for shell in range(smax+1):
        out=dest/f"shell{shell}.json"
        if out.is_symlink():raise RuntimeError("Linked checkpoint")
        if out.exists():
            saved=json.loads(out.read_text(encoding="utf-8"))
            if saved.get("status")!="VP05_IBP_SHELL_COMPLETE" or saved.get("sector")!=sec or saved.get("shell")!=shell or saved.get("kernel_sha256")!=digest(kernel):
                raise RuntimeError("Existing shell mismatch")
            print("VP05_IBP_REUSE "+json.dumps({k:saved[k] for k in ("sector","shell","rows","ranks")}),flush=True)
            continue
        if time.monotonic()>=budget:return
        piv=[{},{}];stored=[0,0];count=0;selected=[[],[]];nseed=0
        evaluated=[{ij:[(evaluate(c,p,z),tuple(evaluate(x,p,z) for x in cs)) for c,cs in entries] for ij,entries in kernel.items()} for p,z,d in POINTS]
        try:
            for a in seeds(sec,shell):
                if sum(-x for x in a if x<0)!=shell:continue
                nseed+=1
                if nseed%10==1:memory_guard()
                for i,j in kernel:
                    if time.monotonic()>=budget:raise TimeoutError("Time budget")
                    count+=1
                    for t,(p,z,d) in enumerate(POINTS):
                        r=row(a,evaluated[t][i,j],i,j,d)
                        n,inc=insert(r,piv[t],p,stored[t]);stored[t]+=n
                        if inc:selected[t].append([list(a),i,j])
            payload={"status":"VP05_IBP_SHELL_COMPLETE","sector":sec,"shell":shell,"kernel_sha256":digest(kernel),
                     "seeds":nseed,"rows":count,"ranks":[len(x) for x in piv],"stored_terms":stored,
                     "points":POINTS,"selected_original_seed_derivatives":selected,"full_closure_proven":False}
            atomic(out,payload)
            print("VP05_IBP_SHELL "+json.dumps({k:v for k,v in payload.items() if k!="selected_original_seed_derivatives"}),flush=True)
        except (TimeoutError,RuntimeError) as exc:
            print("VP05_IBP_SHELL_STOP "+json.dumps({"sector":sec,"shell":shell,"rows":count,"reason":str(exc),"saved_complete_shell":False}),flush=True)
            return

def digest(kernel):
    return hashlib.sha256(repr(kernel).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smax",type=int,default=2)
    p.add_argument("--hours",type=float,default=12)
    a=p.parse_args()
    if not 0<=a.smax<=6 or not 0<a.hours<=12:p.error("Invalid limits")
    spec=build_family_spec("VP05_full")
    kernel=build_kernel(spec.propagators)
    print("VP05_IBP_KERNEL "+json.dumps({"sha256":digest(kernel),"propagators":[[x.momentum,x.mass] for x in spec.propagators],"derivative_checks":180,"inverse_verified":True}),flush=True)
    dest=ROOT/"output"/"vp05_independent_ibp_pilot01"
    dest.mkdir(exist_ok=True)
    end=time.monotonic()+a.hours*3600
    memory_guard()
    for sec in SECTORS:run_sector(sec,kernel,a.smax,end,dest/f"sec{sec}")
    print("VP05_INDEPENDENT_IBP_DIAGNOSTIC_NOT_CLOSURE",flush=True)

if __name__=="__main__":main()
