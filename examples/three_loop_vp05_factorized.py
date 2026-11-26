"""Exact on-demand factorized tadpole reducer for VP05 three-line sectors.

Wick pairings are tensor averages, not Gaussian assumptions: each loop's
rank 2n tensor has denominator d(d+2)...(d+2n-2), radial moment from
(u^2)^n=(P+1)^n. All masses normalized to one, DR scaleless moments zero.
No assertion that parent-sector row space is closed.
"""
import argparse
import functools
import itertools
import json
import math
import os
import time
from examples import three_loop_vp05_direct_affine as a

e=a.e
old=a.old
sp=a.sp
gap=a.gap
n=a.n
v=a.v
ROOT=n.BASE/"output"/"vp05_factorized05"
EVIDENCE=a.ROOT/"direct_evidence.json"
EVIDENCE_SHA="7baed2a12a9328e60a191259b84ddc701e83419e593acf048f54b06cd3fb8a6c"
SECTORS=(69,196,200)
D=old.D
Z=old.Z
PAIRS=old.PAIRS
X=old.X
MAX_DEGREE=6
MAX_DOTS=4
MAX_POLY_TERMS=200000
MAX_CONTRACTIONS=2000000

@functools.lru_cache(maxsize=128)
def radial(power,rank):
    # J_b/J_1, b<=0 scaleless. recurrence b J_(b+1)=(d/2-b)J_b.
    return sp.cancel(sum(math.comb(rank,j)*sp.prod((D/2-k)/k for k in range(1,power-j))
                         for j in range(rank+1) if power-j>=1))

def pairings(items):
    if not items:
        yield ();return
    for j in range(1,len(items)):
        for rest in pairings(items[1:j]+items[j+1:]):
            yield ((items[0],items[j]),)+rest

def scalar(sec):
    return tuple(int(bool(sec&(1<<i))) for i in range(12))

class Reducer:
    def __init__(self,props,sec,deadline):
        self.sec=sec;self.deadline=deadline;self.count=0
        self.lines,S,A,shift=a.basis(props,scalar(sec))
        self.mapping=(A.inv()*(sp.Matrix(old.MOM[:3])-shift)).applyfunc(sp.expand)
        self.map=a.affine(props,scalar(sec),a.CAND)
        self.polys=[]
        for prop in props:
            if prop.mass not in ("0","m2"):raise RuntimeError("Mass scope")
            expr=a.momentum(prop).subs(dict(zip(old.MOM[:3],self.mapping)),simultaneous=True).expand()
            c=[expr.coeff(m) for m in old.MOM]
            if sp.expand(expr-sum(x*m for x,m in zip(c,old.MOM)))!=0:raise RuntimeError("Nonlinear momentum")
            self.polys.append(sp.Poly(sp.expand(sum(c[i]*c[j]*old.dot(i,j) for i in range(5) for j in range(5))-(1 if prop.mass=="m2" else 0)),*X))
        for j,i in enumerate(self.lines):
            if self.polys[i].as_expr()!=old.dot(j,j)-1:raise RuntimeError("Denominator mapping")
        self.moment=functools.lru_cache(maxsize=4096)(self._moment)
    def guard(self):
        if time.monotonic()>=self.deadline:raise TimeoutError("Factorization budget")
        if self.count>MAX_CONTRACTIONS:raise RuntimeError("Contraction cap")
        e.b.a.memory()
    def _moment(self,mon,powers):
        # Each dot product is an edge with one Lorentz index. Pair endpoints
        # belonging to each integrated loop. Connected index components are
        # closed traces (d) or paths joining external vectors (p.p,p.q,q.q).
        loops=[[] for _ in range(3)];external={};edges=[]
        for (i,j),power in zip(PAIRS,mon):
            for _ in range(power):
                edge=len(edges);edges.append((i,j))
                for label in (i,j):
                    if label<3:loops[label].append(edge)
                    else:external.setdefault(edge,[]).append(label)
        if any(len(x)%2 for x in loops):return sp.S.Zero
        ranks=[len(x)//2 for x in loops]
        factor=sp.prod(radial(p,r)/sp.prod(D+2*k for k in range(r)) for p,r in zip(powers,ranks))
        if not factor:return sp.S.Zero
        total=0
        for choices in itertools.product(*(tuple(pairings(tuple(x))) for x in loops)):
            self.count+=1
            if self.count%256==0:self.guard()
            parent=list(range(len(edges)))
            def find(x):
                while parent[x]!=x:x=parent[x]
                return x
            for pairs in choices:
                for i,j in pairs:parent[find(i)]=find(j)
            components={find(i):[] for i in range(len(edges))}
            for i,labels in external.items():components[find(i)].extend(labels)
            term=sp.S.One
            for labels in components.values():
                if not labels:term*=D
                elif len(labels)==2:term*=old.dot(*labels)
                else:raise RuntimeError("Invalid tensor contraction")
            total+=term
        return sp.cancel(factor*total)
    def reduce(self,ex):
        self.guard()
        if gap.sector(ex)!=self.sec or len(ex)!=12 or sum(-x for x in ex if x<0)>MAX_DEGREE or sum(max(x-1,0) for x in ex)>MAX_DOTS:
            raise RuntimeError("Outside factorized envelope")
        poly=sp.Poly(1,*X)
        for i,x in enumerate(ex):
            if x<0:
                poly*=self.polys[i]**(-x)
                if len(poly.terms())>MAX_POLY_TERMS:raise RuntimeError("Polynomial support cap")
        powers=tuple(ex[i] for i in self.lines)
        coeff=sp.cancel(sum(c*self.moment(mon,powers) for mon,c in poly.terms()))
        return coeff
    def close(self):
        self.moment.cache_clear()

def evaluate(expr,field):
    p,z,d=field
    num,den=sp.fraction(expr.subs({D:d,Z:z}))
    return int(num)%p*pow(int(den)%p,-1,p)%p

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        if (a.ROOT/"running.lock").exists():raise RuntimeError("Affine engine running")
        if n.sha(EVIDENCE)!=EVIDENCE_SHA or n.sha(e.SOURCE)!=e.SHA:raise RuntimeError("Evidence SHA")
        evidence=gap.read(EVIDENCE)
        if evidence["direct_targets_proven"]!=12:raise RuntimeError("Evidence scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        manifest=gap.read(path);pins={path:n.sha(path),EVIDENCE:EVIDENCE_SHA,e.SOURCE:e.SHA}
        if a.CAND not in [gap.indices(x) for x in manifest["candidate_masters"]]:raise RuntimeError("Candidate missing")
        spec=old.build_family_spec("VP05_full")
        if old.digest(old.build_kernel(spec.propagators))!=e.b.c.PIN:raise RuntimeError("Kernel")
        exact={}
        for item in evidence["ibp_certificates"]:
            src=old.ROOT / item["file"]
            if n.sha(src)!=item["sha256"]:raise RuntimeError("Certificate SHA")
            pins[src]=item["sha256"];obj=gap.read(src)
            exact[tuple(obj["target"])]=sp.sympify(obj["remainder"][0][1],locals={"d":D,"z":Z})
        exact[tuple(a.BLOCK)]=D-2
        if len(exact)!=12:raise RuntimeError("Expected 12 identities")
        data=gap.read(e.SOURCE);results=[];maps=[]
        for sec in SECTORS:
            reducer=Reducer(spec.propagators,sec,deadline)
            maps.append(reducer.map);v.log("VP05_FACTORIZED_MAP",sector=sec,**reducer.map)
            targets={tuple(x) for x in exact if gap.sector(x)==sec}
            # Actual prior partial envelope, deterministic stratified sample.
            parent=e.m.q.SOURCE if hasattr(e.m.q,"SOURCE") else e.m.SOURCE
            if n.sha(parent)!=e.m.SHA:raise RuntimeError("Parent demand SHA")
            pins[parent]=e.m.SHA
            potential=gap.read(parent)["potential"]
            sample={}
            for ex,_ in potential:
                ex=tuple(ex)
                if gap.sector(ex)==sec:
                    key=(sum(-x for x in ex if x<0),sum(max(x-1,0) for x in ex))
                    if key not in sample:sample[key]=ex
            targets.update(sample.values())
            # Exercise every s=0..6 and dot=0..4, with nontrivial mixed numerators.
            neg=[i for i in range(12) if not sec&(1<<i)]
            for s in range(7):
                for dots in range(5):
                    ex=list(scalar(sec));ex[reducer.lines[0]]+=dots
                    for j in range(s):ex[neg[j%len(neg)]]-=1
                    targets.add(tuple(ex))
            for ex in sorted(targets):
                coeff=reducer.reduce(ex)
                if ex in exact and sp.cancel(coeff-exact[ex])!=0:raise RuntimeError("Exact certificate mismatch")
                observed=[r for r in data["results"] if tuple(r["target"])==ex]
                for r in observed:
                    if len(r["remainder"])!=1 or evaluate(coeff,r["field"])!=r["remainder"][0][1]:raise RuntimeError("Modular comparison")
                row={"sector":sec,"target":list(ex),"coefficient":str(coeff),"existing_exact_match":ex in exact,"modular_checks":len(observed),"potential_sample":ex in sample.values()}
                results.append(row);v.log("VP05_FACTORIZED_TARGET",**row)
            reducer.close()
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Protected input changed")
        if sum(r["existing_exact_match"] for r in results)!=12 or sum(r["modular_checks"] for r in results)!=24:raise RuntimeError("Regression coverage")
        payload={"status":"VP05_FACTORIZED_PILOT_NOT_CLOSURE","inputs":{str(p):h for p,h in pins.items()},"maps":maps,"results":results,"max_numerator_degree":MAX_DEGREE,"max_dot_degree":MAX_DOTS,"full_closure_proven":False,"recursive_parent_reduction_proven":False}
        dest=ROOT/"pilot.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing pilot differs")
        else:old.atomic(dest,payload)
        v.log("VP05_FACTORIZED_PILOT_NOT_CLOSURE",targets=len(results),exact_matches=12,modular_checks=24,maps=3,sha256=n.sha(dest),inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
