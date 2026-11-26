"""Exact rational-function certificates for the observed direct demands.
Reconstruct only modular pivot ancestors, replay original IBP rows over QQ(z,d).
No claim of parent closure or scalar independence.
"""
import argparse
import gc
import json
import os
import time
from collections import Counter
from examples import three_loop_vp05_direct_demand as m

t=m.t
b=m.b
n=m.n
v=m.v
gap=m.gap
old=b.c.old
sp=old.sp
ROOT=n.BASE/"output"/"vp05_direct_exact03"
SOURCE=m.ROOT/"reduction_1795664268348935900.json"
SHA="161d836d36820dc1fb6cd7ba1379a36b75823c88bd324cbf91d3ffd49df2e421"
MAX_PIVOTS=3000
MAX_TERMS=200000
MAX_OPS=2000000

def axpy(row,other,factor):
    for k,val in other.items():
        value=row.get(k,0)+factor*val
        if value:row[k]=value
        else:row.pop(k,None)
    if len(row)>MAX_TERMS:raise RuntimeError("Exact support cap")

class Exact:
    def __init__(self,sec,point,kernel,stores,deadline):
        self.sec=sec;self.point=point;self.kernel=kernel;self.stores=stores;self.deadline=deadline
        self.p,self.z,self.d=old.POINTS[point]
        self.F,_,_=sp.polys.fields.field("z,d",sp.QQ)
        self.indices=[dict(zip(st.piv,st.selected)) for st in stores]
        self.sources=[list(b.c.rows(sec,s)) for s in range(len(stores))]
        self.memo={};self.raw={};self.ops=0;self.terms=0
    def guard(self):
        if time.monotonic()>=self.deadline:raise TimeoutError("Exact budget")
        if self.ops>MAX_OPS or len(self.memo)>MAX_PIVOTS or self.terms>MAX_TERMS:raise RuntimeError("Exact budget cap")
        b.a.memory()
    def mod(self,x):
        a=x.as_expr().subs({old.Z:self.z,old.D:self.d})
        num,den=sp.fraction(a)
        return int(num)%self.p*pow(int(den)%self.p,-1,self.p)%self.p
    def original(self,s,index):
        tag=(s,index)
        if tag not in self.raw:
            ex,i,j=self.sources[s][index]
            self.raw[tag]={b.c.key(k):self.F.from_expr(c) for k,c in m.q.exact_row(ex,self.kernel[i,j],i,j).items()}
        return self.raw[tag]
    def modular(self,row):
        out={}
        for k,val in row.items():
            c=self.mod(val)
            if c:out[k]=c
        return out
    def pivot(self,s,lead):
        tag=(s,lead)
        if tag in self.memo:return self.memo[tag]
        self.guard()
        index=self.indices[s][lead]
        raw=self.original(s,index)
        mod=self.modular(raw)
        deps=[]
        # Same leading-key elimination as original independent shell.
        while mod and max(mod)!=lead:
            k=max(mod)
            if k not in self.indices[s] or self.indices[s][k]>=index:raise RuntimeError("Modular ancestry mismatch")
            f=mod[k];deps.append(k)
            for a,c in self.stores[s].items(k):
                val=(mod.get(a,0)-f*c)%self.p
                if val:mod[a]=val
                else:mod.pop(a,None)
        if not mod or max(mod)!=lead:raise RuntimeError("Missing modular pivot")
        inv=pow(mod[lead],-1,self.p)
        if {k:c*inv%self.p for k,c in mod.items()}!=dict(self.stores[s].items(lead)):raise RuntimeError("Saved pivot replay mismatch")
        row=dict(raw);certificate={(s,index):self.F.one}
        for k in deps:
            other,proof=self.pivot(s,k)
            f=row.get(k,self.F.zero)
            if not f or max(row)!=k:raise RuntimeError("Symbolic path diverged")
            axpy(row,other,-f);axpy(certificate,proof,-f)
            self.ops+=len(other)+len(proof)
            self.guard()
        if not row or max(row)!=lead:raise RuntimeError("Exact leading key mismatch")
        inv=1/row[lead]
        row={k:c*inv for k,c in row.items()}
        certificate={k:c*inv for k,c in certificate.items()}
        if self.modular(row)!=dict(self.stores[s].items(lead)):raise RuntimeError("Exact pivot modular mismatch")
        self.memo[tag]=(row,certificate);self.terms+=len(row)+len(certificate)
        self.guard()
        return row,certificate
    def verify_saved(self,payload,result,other):
        if payload["source_sha256"]!=SHA or payload["kernel_sha256"]!=b.c.PIN or payload["sector"]!=self.sec or payload["target"]!=result["target"] or payload["original_symbolic_replay"] is not True or payload["second_point_match"] is not True:
            raise RuntimeError("Saved proof scope")
        def parse(expr):
            return self.F.from_expr(sp.sympify(expr,locals={"z":old.Z,"d":old.D}))
        remainder={b.c.key(k):parse(c) for k,c in payload["remainder"]}
        if len(remainder)!=len(payload["remainder"]) or not all(remainder.values()):raise RuntimeError("Saved remainder")
        if self.modular(remainder)!={b.c.key(k):c for k,c in result["remainder"]}:raise RuntimeError("Saved first point")
        p,z,d=other["field"]
        def ev(c):
            num,den=sp.fraction(c.as_expr().subs({old.Z:z,old.D:d}))
            return int(num)%p*pow(int(den)%p,-1,p)%p
        if {k:ev(c) for k,c in remainder.items()}!={b.c.key(k):c for k,c in other["remainder"]}:raise RuntimeError("Saved second point")
        replay={};seen=set()
        for term in payload["multipliers"]:
            s,i=term["shell"],term["index"]
            if not 0<=s<len(self.sources) or not 0<=i<len(self.sources[s]) or (s,i) in seen:raise RuntimeError("Saved source index")
            seen.add((s,i))
            ex,j,k=self.sources[s][i]
            if term["seed"]!=list(ex) or term["derivative"]!=[j,k]:raise RuntimeError("Saved source provenance")
            factor=parse(term["coefficient"])
            if not factor:raise RuntimeError("Zero multiplier")
            axpy(replay,self.original(s,i),factor);self.guard()
        want={b.c.key(result["target"]):self.F.one}
        axpy(want,remainder,-self.F.one)
        if replay!=want:raise RuntimeError("Saved original replay mismatch")

    def prove(self,result,other):
        self.guard()
        target=b.c.key(result["target"])
        row={target:self.F.one};proof={}
        for step in result["trace"]:
            s=step["shell"];k=b.c.key(step["lead"])
            pivot,cert=self.pivot(s,k)
            f=row.get(k,self.F.zero)
            if self.mod(f)!=step["factor"]:raise RuntimeError("Target modular factor mismatch")
            axpy(row,pivot,-f);axpy(proof,cert,f)
            self.ops+=len(pivot)+len(cert);self.guard()
        expected={b.c.key(k):c for k,c in result["remainder"]}
        if self.modular(row)!=expected or set(row)!=set(expected):raise RuntimeError("Exact remainder mismatch")
        p,z,d=other["field"]
        def evaluate(c):
            num,den=sp.fraction(c.as_expr().subs({old.Z:z,old.D:d}))
            return int(num)%p*pow(int(den)%p,-1,p)%p
        if {k:evaluate(c) for k,c in row.items()}!={b.c.key(k):val for k,val in other["remainder"]}:raise RuntimeError("Second point mismatch")
        # Independent expansion of original source multipliers.
        replay={}
        for (s,index),factor in proof.items():
            axpy(replay,self.original(s,index),factor)
            self.guard()
        want={target:self.F.one}
        axpy(want,row,-self.F.one)
        if replay!=want:raise RuntimeError("Original IBP replay mismatch")
        return {"sector":self.sec,"target":result["target"],"remainder":[[list(b.c.decode(k)),str(c.as_expr())] for k,c in sorted(row.items())],
                "multipliers":[{"shell":s,"index":i,"seed":list(self.sources[s][i][0]),"derivative":list(self.sources[s][i][1:]),"coefficient":str(c.as_expr())} for (s,i),c in sorted(proof.items())],
                "original_symbolic_replay":True,"second_point_match":True}

def scalar_inventory(spec,manifest):
    # For three independent denominator momenta, change of loop variables
    # with unit absolute determinant removes all external shifts. A massless
    # isolated tadpole is scaleless; report only structural evidence here.
    candidates=[gap.indices(x) for x in manifest["candidate_masters"]]
    props=spec.propagators
    def describe(ex):
        lines=[i for i,a in enumerate(ex) if a>0]
        if len(lines)!=3 or any(a not in (0,1) for a in ex):return None
        mat=sp.Matrix([[sp.sympify(props[i].momentum,locals=dict(zip(map(str,old.MOM),old.MOM))).coeff(m) for m in old.MOM[:3]] for i in lines])
        det=mat.det()
        return {"target":list(ex),"determinant":str(det),"masses":sorted(props[i].mass for i in lines),"unit_determinant":abs(det)==1}
    out=[]
    for sec in (196,200):
        ex=tuple(int(bool(sec&(1<<i))) for i in range(12))
        desc=describe(ex)
        matches=[]
        if desc and desc["unit_determinant"]:
            for cand in candidates:
                other=describe(cand)
                if other and other["unit_determinant"] and other["masses"]==desc["masses"]:matches.append(list(cand))
        out.append({"sector":sec,"description":desc,"matching_unit_determinant_scalar_candidates":matches,"scaleless_factor_candidate":bool(desc and desc["unit_determinant"] and "0" in desc["masses"])})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        for root in (m.ROOT,m.q.ROOT,b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,t.x.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Direct reduction SHA")
        data=gap.read(SOURCE)
        if data["status"]!="VP05_DIRECT_DEMAND_NOT_CLOSURE" or len(data["results"])!=24 or data["kernel_sha256"]!=b.c.PIN:raise RuntimeError("Direct reduction scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        manifest=gap.read(path)
        pins={SOURCE:SHA,path:n.sha(path)}
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel")
        inventory=scalar_inventory(spec,manifest)
        for item in inventory:v.log("VP05_DIRECT_SCALAR_INVENTORY",**item)
        proofs=[]
        for sec in (196,200):
            stores=[t.low_shell(sec,s,0,kernel) for s in (0,1)]
            if sec==200:
                source=b.a.state_path(sec,2,0);pins[source]=n.sha(source)
                _,store,_,_=b.read_legacy(sec,2,0,old.POINTS[0][0]);stores.append(store)
            engine=Exact(sec,0,kernel,stores,deadline)
            left=[r for r in data["results"] if r["sector"]==sec and r["point"]==0]
            right={tuple(r["target"]):r for r in data["results"] if r["sector"]==sec and r["point"]==1}
            if len(left)!=len(right) or len(left)!=(7 if sec==196 else 5):raise RuntimeError("Target counts")
            for result in left:
                ex=tuple(result["target"])
                dest=ROOT/("sec"+str(sec)+"_"+str(left.index(result))+".json")
                try:
                    if dest.exists():
                        payload=gap.read(dest)
                        engine.verify_saved(payload,result,right[ex])
                        proof=payload
                    else:
                        proof=engine.prove(result,right[ex])
                        payload={"source_sha256":SHA,"kernel_sha256":b.c.PIN,**proof}
                        old.atomic(dest,payload)
                        engine.verify_saved(gap.read(dest),result,right[ex])
                    proofs.append({"target":list(ex),"sha256":n.sha(dest)})
                    v.log("VP05_DIRECT_EXACT_PROOF",sector=sec,target=list(ex),remainder=proof["remainder"],original_multipliers=len(proof["multipliers"]),original_symbolic_replay=True)
                except (RuntimeError,TimeoutError,ZeroDivisionError) as exc:
                    v.log("VP05_DIRECT_EXACT_BLOCKED",sector=sec,target=list(ex),reason=str(exc))
                    if isinstance(exc,TimeoutError):break
            del engine,stores
            if sec==200:del store
            gc.collect()
            if time.monotonic()>=deadline:break
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Input changed")
        v.log("VP05_DIRECT_EXACT_NOT_CLOSURE",proved=len(proofs),expected=12,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
